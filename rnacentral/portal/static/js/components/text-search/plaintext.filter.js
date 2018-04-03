/**
 * Given an array of strings with html markup, strips
 * all the markup from those strings and leaves only the text.
 */
angular.module("textSearch").filter("plaintext", function() {
    return function(items) {
        var result = [];

        angular.forEach(items, function(stringWithHtml) {
            result.push(String(stringWithHtml).replace(/<[^>]+>/gm, ''));
        });

        return result;
    };
});
