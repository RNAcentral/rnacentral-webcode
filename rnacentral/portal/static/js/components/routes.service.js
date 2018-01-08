/**
 * Service for resolving urls from backend, instead of hard
 */

angular.module("rnacentralApp").service('routes', ['$interpolate', function($interpolate) {
    return {
        helpTextSearch: $interpolate('/help/text-search/'),
        contactUs: $interpolate('/contact'),
        submitQuery: $interpolate('/export/submit-query'),
        resultsPage: $interpolate('/export/results'),
        rnaView: $interpolate('/rna/{{ upi }}'),
        rnaViewWithTaxid: $interpolate('/rna/{{upi}}/{{ taxid }}'),
        apiPublicationsView: $interpolate('/api/v1/rna/{{ upi }}/publications/{{ taxid }}'),
        apiRnaView: $interpolate('/api/v1/rna/{{ upi }}'),
        apiGenomeLocationsView: $interpolate('/api/v1/rna/{{ upi }}/genome-locations/{{ taxid }}'),
        lineageView: $interpolate('/rna/{{ upi }}/lineage'),
        expertDbsApi: $interpolate('/api/v1/expert-dbs/{{ expertDbName }}'),
        expertDbStatsApi: $interpolate('/api/v1/expert-db-stats/{{ expertDbName }}'),
        textSearch: $interpolate('search'),
        expertDbLogo: $interpolate('/static/img/expert-db-logos/{{ expertDbName }}.png'),
        apiSecondaryStructuresView: $interpolate('/api/v1/rna/{{ upi }}/2d/{{ taxid }}'),
        genomesApi: $interpolate('/api/v1/genomes'),
        ebiSearchProxy: $interpolate('/api/internal/ebeye?url={{ ebeyeUrl }}'),
        ebiSearch: $interpolate(
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
        ),
        ebiAutocomplete: $interpolate('http://www.ebi.ac.uk/ebisearch/ws/rest/RNAcentral/autocomplete?term={{ query }}&format=json')
    };
}]);
