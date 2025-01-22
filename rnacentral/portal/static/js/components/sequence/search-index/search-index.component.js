var searchIndex = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', 'routes',  function($http, $interpolate, routes) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.fetchSearhIndexData().then(
                function(response) {
                    const entry = response.data.entries?.[0]?.fields || {};
                    const soRnaType = entry.so_rna_type?.[0] || "";
                    const prettySoRnaType = ctrl.parseSoRnaType(soRnaType);

                    ctrl.length = entry.length?.[0] || "";
                    ctrl.databases = entry.expert_db || [];
                    ctrl.summarySoTerms = prettySoRnaType.slice(1);
                    ctrl.formattedDatabases = ctrl.formatDatabases(angular.copy(ctrl.databases));
                },
                function(response) {
                    ctrl.error = "Failed to fetch Search Index Data";
                }
            );

            ctrl.fetchSpeciesCount().then(
                function(response) {
                    ctrl.otherSpecies = response.data.hitCount || 0;
                }
            )
        };

        ctrl.parseSoRnaType = function(soRnaType) {
            const exceptions = ["RNase_P_RNA", "SRP_RNA", "Y_RNA", "RNase_MRP_RNA"];
            const terms = soRnaType.split("/").filter(term => term); // Split and remove empty terms

            return terms.map(soTerm => {
                if (!exceptions.includes(soTerm)) {
                    soTerm = soTerm[0].toLowerCase() + soTerm.slice(1);
                }
                if (soTerm === "lnc_RNA") return "lncRNA";
                if (soTerm === "pre_miRNA") return "pre-miRNA";
                return soTerm.replace("_", " ");
            });
        };

        ctrl.fetchSearhIndexData = function() {
            return $http.get(routes.ebiSequencePageSummary({ ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT, upi: ctrl.upi, taxid: ctrl.taxid }),
                { timeout: 20000 }
            )
        };

        ctrl.fetchSpeciesCount = function() {
            return $http.get(routes.ebiDbSequences({ ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT, dbQuery: 'entry_type:sequence AND ' + ctrl.upi + '* NOT TAXONOMY:' + ctrl.taxid }),
                { timeout: 20000 }
            )
        };

        ctrl.formatDatabases = function(databases) {
            if (!databases || databases.length === 0) return "";
            if (databases.length === 1) return `${databases[0]}`;
            const last = databases.pop();
            return `${databases.join(', ')} and ${last}`;
        };
    }],
    template: '<ul class="list-inline" id="sequence-overview">' +
              '    <li ng-if="$ctrl.length"> ' +
              '        <strong>{{ $ctrl.length }}</strong> nucleotides ' +
              '    </li>' +
              '    <li ng-if="$ctrl.databases.length"> ' +
              '        <strong>{{ $ctrl.databases.length }}</strong> {{ $ctrl.databases.length === 1 ? \'database\' : \'databases\' }} ' +
              '        <small>({{ $ctrl.formattedDatabases }})</small> ' +
              '    </li>' +
              '    <li> ' +
              '        Found in <strong>{{ $ctrl.otherSpecies }}</strong> other species ' +
              '    </li>' +
              '    <li ng-if="$ctrl.summarySoTerms.length"> ' +
              '        <ol class="breadcrumb well well-sm" style="background-color: white; margin-bottom: 0;"> ' +
              '            <li ng-repeat="so_term in $ctrl.summarySoTerms"> ' +
              '                <a href="/search?q=so_rna_type_name:&#34;{{ so_term }}&#34;" uib-tooltip="Browse {{ so_term }}">{{ so_term }}</a> ' +
              '            </li> ' +
              '        </ol>' +
              '    </li>' +
              '</ul>' +
              '<div ng-if="$ctrl.error"> ' +
              '    Error: {{ $ctrl.error }} ' +
              '</div> '
};

angular.module("rnaSequence").component("searchIndex", searchIndex);
