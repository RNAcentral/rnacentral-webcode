/*
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/**
 * Angular.js code for exporting metadata search results.
 */

;angular.module('textSearch').controller('ExportResultsCtrl', ['$scope', '$location', '$http', '$window', 'routes', function($scope, $location, $http, $window, routes) {

    $scope.export = {
        query: null,
        job_id: null,
        data_type: null,
        status: "loading",
        hits: null,
        progress: -1,
        ended_at: null,
        enqueued_at: null,
        error_message: '',
    };
    $scope.routes = routes;

    /**
     * Get status of the export job and return a promise.
     */
    function get_job_status() {
        return $http({
            url: routes.exportApp() + '/download/' + $scope.export.job_id + '/' + $scope.export.data_type,
            method: 'GET'
        }).then(
            function(response) {
                // get_job_status will be called as long as the content-type is
                // equal to application/json and the status is different from FAILURE
                if (response.headers('content-type').includes('application/json')) {
                    $scope.export.hits = response.data.hit_count;

                    // Check progress
                    if ($scope.export.data_type === 'fasta') {
                        $scope.export.progress = (response.data.progress_ids + response.data.progress_fasta) / 2 || 0;
                    } else if ($scope.export.data_type === 'json') {
                        $scope.export.progress = (response.data.progress_ids + response.data.progress_db_data) / 2 || 0;
                    } else {
                        $scope.export.progress = response.data.progress_ids || 0;
                    }

                    // Set polling interval based on the number of hits.
                    var interval;
                    if ($scope.export.hits<=10000) {
                        interval = 1000
                    } else if ($scope.export.hits>10000 && $scope.export.hits<=100000) {
                        interval = 3000
                    } else if ($scope.export.hits>100000 && $scope.export.hits<=1000000) {
                        interval = 10000
                    } else if ($scope.export.hits>1000000) {
                        interval = 30000
                    }

                    // Check status
                    $scope.export.status = response.data.state === 'RUNNING' ? 'running' : response.data.state ? response.data.state : 'pending';
                    if ($scope.export.status !== 'FAILURE') {
                        setTimeout(get_job_status, interval);
                    } else {
                        $scope.export.error_message = 'Job failed';
                    }
                } else {
                    $scope.export.status = 'finished';
                    $scope.export.progress = 100;
                }
                update_page_title();
            },
            function(response) {
                if (response.status === 404) {
                    $scope.export.error_message = 'Job not found';
                } else {
                    $scope.export.error_message = 'Unknown error';
                }
                update_page_title();
            }
        );
    }

    /**
     * Format progress for use with ng-style and CSS.
     */
    $scope.get_progress = function() {
        return $scope.export.progress + '%';
    };

    /**
     * Show progress in page title.
     */
    function update_page_title() {
        if ($scope.export.status === 'FAILURE') {
            $window.document.title = 'Export failed';
        } else if ($scope.export.error_message !== '') {
            $window.document.title = 'Results expired';
        } else {
            $window.document.title = Math.round($scope.export.progress) + '% | Exporting results';
        }
    }

    /**
     * Download file.
     */
    $scope.triggerDownload = function() {
        var downloadUrl = routes.exportApp() + '/download/' + $scope.export.job_id + '/' + $scope.export.data_type;
        var filename = $scope.export.job_id + '.' + ($scope.export.data_type === 'json' ? 'json.gz' : $scope.export.data_type === 'fasta' ? 'fasta.gz' : 'txt.gz');
        var a = document.createElement('a');

        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    /**
     * Get job id from the url and begin retrieving data.
     */
    function initialize() {
        if ($location.url().indexOf("/export/results?job=") > -1) {
            $scope.export.job_id = $location.search().job;
            $scope.export.data_type = $location.search().data_type;
            get_job_status();
        }
    }

    // get job id and start updating the status
    initialize();

}]);
