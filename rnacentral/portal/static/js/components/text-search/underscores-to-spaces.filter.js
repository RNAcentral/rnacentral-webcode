/**
 * Replaced all the occurrences of underscore in the input string with period (dot) and whitespace.
 * E.g. pub_title -> pub. title.
 */
angular.module("rnacentralApp").filter('underscoresToSpaces', function() {
    return function(item) {
        return item.replace(/_/g, ' ');
    }
});