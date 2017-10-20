/**
 * Service for resolving urls from backend, instead of hard
 */

angular.module("rnacentralApp").service('routes', ['$interpolate', function() {
    return {
        helpTextSearch: '/help/text-search/',
        contactUs: '/contact',
        submitQuery: '/export/submit-query',
        resultsPage: '/export/results',
        rnaView: $interpolate('/rna/{{upi}}/{{taxid}}'),
        lineageView: $interpolate('/rna/{{upi}}/lineage'),
        expertDbsApi: $interpolate('/api/v1/expert-dbs/{{ expertDbName }}')
    };
}]);


