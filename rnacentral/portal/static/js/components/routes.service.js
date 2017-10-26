/**
 * Service for resolving urls from backend, instead of hard
 */

angular.module("rnacentralApp").service('routes', ['$interpolate', function($interpolate) {
    return {
        helpTextSearch: $interpolate('/help/text-search/'),
        contactUs: $interpolate('/contact'),
        submitQuery: $interpolate('/export/submit-query'),
        resultsPage: $interpolate('/export/results'),
        rnaView: $interpolate('/rna/{{upi}}'),
        rnaViewWithTaxid: $interpolate('/rna/{{upi}}/{{taxid}}'),
        apiRnaView: $interpolate('/api/v1/rna/{{upi}}'),
        lineageView: $interpolate('/rna/{{upi}}/lineage'),
        expertDbsApi: $interpolate('/api/v1/expert-dbs/{{ expertDbName }}'),
        expertDbStatsApi: $interpolate('/api/v1/expert-db-stats/{{ expertDbName }}'),
        textSearch: $interpolate('search'),
        expertDbLogo: $interpolate('/static/img/expert-db-logos/{{ expertDbName }}.png'),
        genomesApi: $interpolate('/api/v1/genomes'),
    };
}]);


