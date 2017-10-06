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

        /**
         * Given unique rna page url, extracts urs from it.
         */
        ctrl.url2urs = function(url) {
            // if url ends with a slash, strip it
            if (url.slice(-1) === '/') url = url.slice(-1);

            // url might have a taxid, so let's just take the url fragment after 'rna'
            var breadcrumbs = url.split('/');
            for (var urlFragment = 0; urlFragment < breadcrumbs.length; urlFragment++) {
                if (breadcrumbs[urlFragment] === 'rna') return breadcrumbs[urlFragment + 1];
            }
        };

        ctrl.onPageSizeChanged = function(newPageSize, oldPageSize) {
            oldPageSize = parseInt(oldPageSize);

            // re-calculate page, taking new pageSize into account
            ctrl.page = Math.floor(((ctrl.page - 1) * oldPageSize) / newPageSize) + 1;
            ctrl.pageSize = newPageSize;
            ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);
            
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            ctrl.status = 'loading';
            $http.get(ctrl.dataEndpoint, {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.displayedXrefs = response.data.results;
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);
                },
                function(response) {
                    ctrl.status = 'error';
                }
            )
        };

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;
            ctrl.page = ctrl.page || 1;
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'client';
            ctrl.status = 'loading';

            // Request xrefs from server (with taxid, if necessary)
            ctrl.dataEndpoint;
            if (ctrl.taxid) ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            $http.get(ctrl.dataEndpoint, {timeout: ctrl.timeout}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.xrefs = response.data.results;
                    ctrl.displayedXrefs = ctrl.xrefs.slice(0, ctrl.pageSize);
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);
                },
                function(response) {
                    // if it took server too long to respond and request was aborted by timeout
                    // send a paginated request instead and fallback to server-side processing
                    if (response.status === -1) {  // for timeout response.status is -1
                        ctrl.paginateOn = 'server';
                        ctrl.getPageFromServerSide();
                    }
                    else {
                        ctrl.status = 'error';
                    }
                }
            );
        }
    }],
    templateUrl: '/static/js/components/sequence/xrefs/xrefs.html'
};

angular.module("rnaSequence").component("xrefs", xrefs);
