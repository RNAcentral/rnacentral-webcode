var ensemblCompara = {
    bindings: {
        upi: '=',
        taxid: '=',
    },

    controller: ['$http', 'routes', '$location', function($http, routes, $location) {
        var ctrl = this;

        ctrl.error = null;
        ctrl.count = 0;
        ctrl.next_page = null;
        ctrl.ensembl_compara = [];
        ctrl.ensembl_compara_url = '';
        ctrl.ensembl_compara_status = '';

        ctrl.$onInit = function() {
            ctrl.displayResults();
        };

        // DRF URLs use http which don't work when the site is loaded over https
        ctrl.enforce_https_url = function(url) {
            if (typeof(url) !== 'undefined' && $location.protocol() === 'https' && url.indexOf('https') === -1) {
                url = url.replace('http', 'https');
            }
            return url;
        }

        ctrl.displayResults = function(next_page_url) {
            ctrl.fetchEnsemblCompara(ctrl.enforce_https_url(next_page_url)).then(
                function(response) {
                    ctrl.ensembl_compara = ctrl.ensembl_compara.concat(response.data.results);
                    ctrl.count = response.data.count;
                    ctrl.next_page = response.data.links.next;
                    ctrl.ensembl_compara_url = response.data.ensembl_compara_url;
                    ctrl.ensembl_compara_status = response.data.ensembl_compara_status;
                },
                function(response) {
                    ctrl.error = "Failed to fetch Ensembl Compara annotations";
                }
            );
        };

        ctrl.fetchEnsemblCompara = function(next_page_url) {
            if (typeof next_page_url === 'undefined') {
                return $http.get(
                    routes.apiEnsemblComparaView({ upi: ctrl.upi, taxid: ctrl.taxid }),
                    { timeout: 20000 }
                );
            } else {
                return $http.get(next_page_url, { timeout: 20000 });
            }
        };

        ctrl.loadMoreResults = function() {
            ctrl.displayResults(ctrl.next_page);
        };

        ctrl.has_same_urs = function(rnacentral_id) {
            if (rnacentral_id.indexOf(ctrl.upi) === -1) {
                return false;
            } else {
                return true;
            }
        };

        ctrl.is_paralog = function(rnacentral_id) {
            taxid = rnacentral_id.split('_')[1];
            if (taxid === ctrl.taxid) {
                return true;
            } else {
                return false;
            }
        };
    }],

    templateUrl: '/static/js/components/sequence/ensembl-compara/ensembl-compara.html'
};

angular.module("rnaSequence").component("ensemblCompara", ensemblCompara);
