var publications = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', 'routes', function($http, routes) {
        var ctrl = this;

        ctrl.defaultPageSize = 25;

        ctrl.$onInit = function() {
            ctrl.abstracts = {};
            // this is slightly error-prone, cause we assign promise to a variable - make sure we don't use it before

            ctrl.fetchPublications(ctrl.defaultPageSize, 1).then(
                function(response) {
                    ctrl.publicationCount = response.data.count;
                    ctrl.publications = response.data.results;
                },
                function(response) {
                    ctrl.error = "Failed to download publications";
                }
            );
        };

        ctrl.fetchPublications = function(pageSize, page) {
            return $http.get(
                routes.apiPublicationsView({ upi: ctrl.upi }),
                { timeout: 5000, params: { page_size: pageSize, page: page } }
            )
        };

        ctrl.loadMore = function(pageSize) {
            var page = Math.ceil(ctrl.publications.length / pageSize) + 1;

            ctrl.fetchPublications(pageSize, page).then(
                function(response) {
                    ctrl.publications = ctrl.publications.concat(response.data.results);
                },
                function(response) {
                    ctrl.error = "Failed to download publications";
                }
            );
        };
    }],
    template: '<div id="publications">' +
              '    <h2>Publications <small>{{ $ctrl.publicationCount }} total</small></h2>' +
              '    <ol>' +
              '        <div ng-repeat="publication in $ctrl.publications" class="col-md-8">' +
              '            <li class="margin-bottom-10px">' +
              '                <publication publication="publication" show-find-other-sequences="true"></publication>' +
              '            </li>' +
              '        </div>' +
              '    </ol>' +
              '    <div ng-if="$ctrl.publications.length < $ctrl.publicationCount" class="col-md-8">' +
              '        <small class="text-muted">Displaying {{ $ctrl.publications.length }} of {{ $ctrl.publicationCount }} publications</small>' +
              '        <br>' +
              '        <button class="btn btn-default btn-large" id="load-more-publications" ng-click="$ctrl.loadMore($ctrl.defaultPageSize)">Load more</button>' +
              '    </div>' +
              '    <div class="row">' +
              '        <div ng-if="!$ctrl.publications" class="col-md-12">' +
              '            <i class="pe-7s-config pe-spin pe-2x pe-va"></i>' +
              '            <span class="margin-left-5px">Loading publications...</span>' +
              '        </div>' +
              '    ' +
              '    </div>' +
              '</div>'
};

angular.module("rnaSequence").component("publications", publications);
