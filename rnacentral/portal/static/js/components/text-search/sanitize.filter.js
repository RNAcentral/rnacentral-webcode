/**
 * Custom filter for inserting HTML code in templates.
 * Used for processing search results highlighting.
 */
angular.module("textSearch").filter("sanitize", ['$sce', function($sce) {
    return function(htmlCode){
        return $sce.trustAsHtml(htmlCode);
    }
}]);