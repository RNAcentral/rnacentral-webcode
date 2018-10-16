var lncrnaTargets = {
    bindings: {
        upi: '<',
        taxid: '<',
        genomes: '<',
        timeout: '<?',
        page: '<?',
        pageSize: '<?'
    },
    controller: ['$http', '$interpolate', 'routes',  function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.help = '/help/rna-target-interactions';

        ctrl.onPageSizeChanged = function(newPageSize, oldPageSize) {
            oldPageSize = parseInt(oldPageSize);

            // re-calculate page, taking new pageSize into account
            ctrl.page = Math.floor(((ctrl.page - 1) * oldPageSize) / newPageSize) + 1;
            ctrl.pageSize = newPageSize;
            ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);

            if (ctrl.paginateOn === 'client') {
                ctrl.displayedTargets = ctrl.targets.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedTargets = ctrl.targets.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            ctrl.status = 'loading';
            $http.get(routes.apiLncrnaTargetsView({ upi: ctrl.upi, taxid: ctrl.taxid }), {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.displayedTargets = response.data.results;
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
            ctrl.page = ctrl.page || 1;  // human-readable number of page to show, in range of (1, n)
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'client';  // load all Xrefs at once and paginate Xrefs table on client-side, or if too slow, fallback to loading'em page-by-page from server
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;  // if (time of response) > timeout, paginate on server side
            ctrl.status = 'loading';  // {'loading', 'error' or 'success'} - display spinner, error message or xrefs table

            $http.get(routes.apiLncrnaTargetsView({ upi: ctrl.upi, taxid: ctrl.taxid }), { timeout: ctrl.timeout, params: { page: 1, page_size: 1000000000000 } }).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.targets = response.data.results;
                    ctrl.displayedTargets = ctrl.targets.slice(0, ctrl.pageSize);
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
            )
        };

        ctrl.ensemblUrl = function(target) {
            var accession = target.target_accession.split(":")[1];
            var species = ctrl.genomes.find(function(genome) { return genome.taxid.toString() == ctrl.taxid; }).ensembl_url;
            return $interpolate("https://www.ensembl.org/{{ species }}/Gene/Summary?g={{ accession }};")({ species: species, accession: accession });
        };

        ctrl.lncbaseUrl = function(target) {
            var expertDatabaseId = target.source_accession.split(":")[1];
            var ensemblId = target.target_accession.split(":")[1];
            var template = "http://carolina.imis.athena-innovation.gr/diana_tools/web/index.php?r=lncbasev2%2Findex-experimental&miRNAs%5B%5D={{ expertDatabaseId }}&lncRNAs%5B%5D={{ ensemblId }}&filters=0"
            return $interpolate(template)({ expertDatabaseId: expertDatabaseId, ensemblId: ensemblId });
        }
    }],
    templateUrl: '/static/js/components/sequence/lncrna-targets/lncrna-targets.html'
};

angular.module("rnaSequence").component("lncrnaTargets", lncrnaTargets);
