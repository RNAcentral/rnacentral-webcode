angular.module("routes", []).service('routes', ['$interpolate', function($interpolate) {
    var routes = {
        helpTextSearch: '/help/text-search/',
        contactUs: '/contact',
        submitQuery: '/export/submit-query',
        resultsPage: '/export/results',
        rnaView: '/rna/{{ upi }}',
        rnaViewWithTaxid: '/rna/{{upi}}/{{ taxid }}',
        apiPublicationsView: '/api/v1/rna/{{ upi }}/publications/{{ taxid }}',
        apiRnaView: '/api/v1/rna/{{ upi }}',
        apiRnaViewWithTaxid: '/api/v1/rna/{{ upi }}/{{ taxid }}',
        apiGenomeLocationsView: '/api/v1/rna/{{ upi }}/genome-locations/{{ taxid }}',
        apiRfamHitsView: '/api/v1/rna/{{ upi }}/rfam-hits/{{ taxid }}',
        apiProteinTargetsView: '/api/v1/rna/{{ upi }}/protein-targets/{{ taxid }}',
        apiLncrnaTargetsView: '/api/v1/rna/{{ upi }}/lncrna-targets/{{ taxid }}',
        apiSequenceFeaturesView: '/api/v1/rna/{{ upi }}/sequence-features/{{ taxid }}',
        lineageView: '/rna/{{ upi }}/lineage',
        expertDbsApi: '/api/v1/expert-dbs/{{ expertDbName }}',
        expertDbStatsApi: '/api/v1/expert-db-stats/{{ expertDbName }}',
        textSearch: 'search',
        expertDbLogo: '/static/img/expert-db-logos/{{ expertDbName }}.png',
        apiSecondaryStructuresView: '/api/v1/rna/{{ upi }}/2d/{{ taxid }}',
        sequenceSearchSubmitJob: '/sequence-search/submit-job',
        sequenceSearchJobStatus: '/sequence-search/job-status/{{ jobId }}',
        sequenceSearchResults: '/sequence-search/job-results/{{ jobId }}',
        sequenceSearchInfernalJobStatus: '/sequence-search/infernal-job-status/{{ jobId }}',
        sequenceSearchInfernalResults: '/sequence-search/infernal-results/{{ jobId }}',
        apiEnsemblComparaView: '/api/v1/rna/{{ upi }}/ensembl-compara/{{ taxid }}',
        apiInteractionsView: '/api/v1/rna/{{ upi }}/interactions/{{ taxid }}',
        genomesApi: '/api/v1/genomes/{{ ensemblAssembly }}',
        proxy: '/api/internal/proxy?url={{ url }}',
        ebiSearch:
            '{{ ebiBaseUrl }}' +
            '?query={{ query }}' +
            '&format=json' +
            '&hlfields={{ hlfields }}' +
            '&facetcount={{ facetcount }}' +
            '&facetfields={{ facetfields }}' +
            '&facetsdepth=10' +
            '&size={{ pagesize }}' +
            '&start={{ start }}' +
            '&sort={{ sort }}' +
            '&hlpretag=<span class=text-search-highlights>' +
            '&hlposttag=</span>'
        ,
        ebiMd5Lookup:
            '{{ ebiBaseUrl }}' +
            '?query={{ md5 }}' +
            '&fields=description' +
            '&format=json' +
            '&sort=boost:descending'
        ,
        ebiDbSequences:
            '{{ ebiBaseUrl }}' +
            '?query={{ dbQuery }}' +
            '&fields=description,length' +
            '&size=1000' +
            '&format=json'
        ,
        ebiAutocomplete: 'http://www.ebi.ac.uk/ebisearch/ws/rest/RNAcentral/autocomplete?term={{ query }}&format=json',
        apiGoTermsView: '/api/v1/rna/{{ upi }}/go-annotations/{{ taxid }}',
        quickGoSummaryPage: 'https://www.ebi.ac.uk/QuickGO/term/{{ term_id }}',
        quickGoChart: 'https://www.ebi.ac.uk/QuickGO/services/ontology/{{ ontology }}/terms/{{ term_ids }}/chart?base64=true',
        qcStatusApi: '/api/v1/rna/{{ upi }}/qc-status/{{ taxid }}',
        exportApp: 'http://hx-rke-wp-webadmin-12-worker-3.caas.ebi.ac.uk:31867',
    };


    // apply $interpolate to each route template expression
    return Object.keys(routes)
          .map(function(key) { var output = {}; output[key] = $interpolate(routes[key]); return output })
          .reduce(function(result, keyValue ) { return _.extend(result, keyValue) } );
}]);
