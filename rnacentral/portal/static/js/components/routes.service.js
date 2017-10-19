/**
 * Service for resolving urls from backend, instead of hard
 */

angular.module("rnacentralApp").service('routes', ['$interpolate', function() {
    return {
        helpTextSearch: '/help/text-search/',
        contactUs: '/contact',
        submitQuery: '/export/submit-query',
        resultsPage: '/export/results',
        rnaView: '/rna/{{upi}}/{{taxid}}',
        'expert-dbs-api': $interpolate('/api/v1/expert-dbs/{{ expertDbName }}')
    };
}]);


