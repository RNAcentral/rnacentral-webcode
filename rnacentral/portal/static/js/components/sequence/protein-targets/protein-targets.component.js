var proteinTargets = {
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

            if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            ctrl.status = 'loading';
            $http.get(routes.apiProteinTargetsView({ upi: ctrl.upi, taxid: ctrl.taxid }), {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.displayedProteins = response.data.results;
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
            ctrl.paginateOn = 'server';  // load page-by-page from server
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;  // if (time of response) > timeout, paginate on server side
            ctrl.status = 'loading';  // {'loading', 'error' or 'success'} - display spinner, error message or xrefs table

            ctrl.getPageFromServerSide();
        };

        ctrl.ensemblUrl = function(protein) {
            var accession = protein.target_accession.split(":")[1];
            var species = ctrl.genomes.find(function(genome) { return genome.taxid.toString() == ctrl.taxid; }).ensembl_url;
            return $interpolate("https://www.ensembl.org/{{ species }}/Gene/Summary?g={{ accession }};")({ species: species, accession: accession });
        };

        ctrl.tarbaseUrl = function(protein) {
            var tarbaseId = protein.source_accession.split(":")[1];
            var ensemblId = protein.target_accession.split(":")[1];
            var template = "http://carolina.imis.athena-innovation.gr/diana_tools/web/index.php?r=tarbasev8%2Findex&miRNAs%5B0%5D={{ tarbaseId }}&genes%5B0%5D={{ ensemblId }}&sources%5B0%5D=1&sources%5B1%5D=7&sources%5B2%5D=9";
            return $interpolate(template)({ tarbaseId: tarbaseId, ensemblId: ensemblId });
        }
    }],
    templateUrl: '/static/js/components/sequence/protein-targets/protein-targets.html'
};

angular.module("rnaSequence").component("proteinTargets", proteinTargets);
