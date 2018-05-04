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
        apiGenomeLocationsView: '/api/v1/rna/{{ upi }}/genome-locations/{{ taxid }}',
        apiGenomeMappingsView: '/api/v1/rna/{{ upi }}/genome-mappings/{{ taxid }}',
        apiRfamHitsView: '/api/v1/rna/{{ upi }}/rfam-hits',
        lineageView: '/rna/{{ upi }}/lineage',
        expertDbsApi: '/api/v1/expert-dbs/{{ expertDbName }}',
        expertDbStatsApi: '/api/v1/expert-db-stats/{{ expertDbName }}',
        textSearch: 'search',
        expertDbLogo: '/static/img/expert-db-logos/{{ expertDbName }}.png',
        apiSecondaryStructuresView: '/api/v1/rna/{{ upi }}/2d/{{ taxid }}',
        genomesApi: '/api/v1/genomes/{{ ensemblAssembly }}',
        ebiSearchProxy: '/api/internal/ebeye?url={{ ebeyeUrl }}',
        ebiSearch:
            '{{ ebiBaseUrl }}' +
            '?query={{ query }}' +
            '&format=json' +
            '&hlfields={{ hlfields }}' +
            '&facetcount={{ facetcount }}' +
            '&facetfields={{ facetfields }}' +
            '&size={{ pagesize }}' +
            '&start={{ start }}' +
            '&sort={{ sort }}' +
            '&hlpretag=<span class=text-search-highlights>' +
            '&hlposttag=</span>'
        ,
        ebiAutocomplete: 'http://www.ebi.ac.uk/ebisearch/ws/rest/RNAcentral/autocomplete?term={{ query }}&format=json'
    };

    // apply $interpolate to each route template expression
    return Object.keys(routes)
          .map(function(key) { var output = {}; output[key] = $interpolate(routes[key]); return output })
          .reduce(function(result, keyValue ) { return _.extend(result, keyValue) } );
}]);
