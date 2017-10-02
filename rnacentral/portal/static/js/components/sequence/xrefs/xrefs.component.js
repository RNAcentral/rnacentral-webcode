var xrefs = {
    bindings: {
        upi: '<',
        timeout: '<?',
        page: '<?',
        pageSize: '<?',
        taxid: '<?',
        onActivatePublications: '&'
    },
    controller: ['routes', '$http', '$interpolate', '$timeout', function(routes, $http, $interpolate, $timeout) {
        var ctrl = this;

        ctrl.onPageSizeChanged = function(pageSize) {
            // re-calculate page, taking new pageSize into account
            ctrl.page = Math.floor(ctrl.page * ctrl.pageSize, pageSize);
            ctrl.pageSize = pageSize;
            
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice(ctrl.page*ctrl.pageSize, (ctrl.page + 1)*ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice(ctrl.page*ctrl.pageSize, (ctrl.page + 1)*ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            $http.get(ctrl.dataEndpoint, {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.displayedXrefs = response.data.results;
                },
                function(response) {
                    console.log("failed to download a page");
                }
            )
        };

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.timeout = parseInt(ctrl.timeout) || 50000;
            ctrl.page = ctrl.page || 1;
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'client';

            // Request xrefs from server (with taxid, if necessary)
            ctrl.dataEndpoint;
            if (ctrl.taxid) ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            $http.get(ctrl.dataEndpoint, {timeout: ctrl.timeout}).then(
                function(response) {
                    ctrl.xrefs = response.data.results;

                    ctrl.displayedXrefs = ctrl.xrefs.slice();
                },
                function(response) {
                    // if it took server too long to respond and request was aborted by timeout
                    // send a paginated request instead and fallback to server-side processing
                    if (response.status === -1) {  // for timeout response.status is -1
                        ctrl.getPageFromServerSide();
                    }
                    else {
                        // TODO: display an error message in template!
                        console.log("Error happened while downloading data");
                    }
                }
            );
        }
    }],
    templateUrl: '/static/js/components/sequence/xrefs/xrefs.html'
};

angular.module("rnaSequence").component("xrefs", xrefs);
