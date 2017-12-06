var xrefs = {
    bindings: {
        upi: '<',
        timeout: '<?',
        page: '<?',
        pageSize: '<?',
        taxid: '<?',
        onActivatePublications: '&',
        onActivateModifiedNucleotides: '&',
        onActivateGenomeBrowser: '&'
    },
    controller: ['routes', '$http', '$interpolate', '$timeout', '$filter', function(routes, $http, $interpolate, $timeout, $filter) {
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
                    ctrl.displayedXrefs = ctrl.orderByModificationsOrCoordinates(response.data.results);
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);
                },
                function(response) {
                    ctrl.status = 'error';
                }
            )
        };

        /**
         * Given results from data json, create a new results array, sorted so that entries
         *  with modifications or genome coordinates go first.
         *
         * @param {Array} results - e.g. [{ database: "Ensembl", is_expert_db: false, accession: {...} ... }, ...]
         * @returns {Array} - sorted copy of results
         */
        ctrl.orderByModificationsOrCoordinates = function(results) {
            var output = [];

            for (var i = 0; i < results.length; i++) {
                if (results[i].modifications.length || results[i].genomic_coordinates) {
                    output.unshift(results[i]);
                } else {
                    output.push(results[i]);
                }
            }

            return output;
        };

        /**
         * Genome browser breaks with chromosomes like 'GL00220.1' (e.g. localhost:8000/rna/URS000075A823/9606)
         * Don't show "View genomic location" button, if that's the case.
         */
        ctrl.chromosomeIsScaffold = function(chromosome) {
            return !!chromosome.match(/\S+\.\S/);
        };

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.page = ctrl.page || 1;  // human-readable number of page to show, in range of (1, n)
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'client';  // load all Xrefs at once and paginate Xrefs table on client-side, or if too slow, fallback to loading'em page-by-page from server
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;  // if (time of response) > timeout, paginate on server side

            ctrl.status = 'loading';  // {'loading', 'error' or 'success'} - display spinner, error message or xrefs table

            // Request xrefs from server (with taxid, if necessary)
            if (ctrl.taxid) ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            $http.get(ctrl.dataEndpoint, {timeout: ctrl.timeout}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.xrefs = ctrl.orderByModificationsOrCoordinates(response.data.results);
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
