/**
 * Makes first letter of the input string captial.
 */
angular.module("textSearch").filter("capitalizeFirst",  function() {
    return function(item) {
        return item.charAt(0).toUpperCase() + item.slice(1);
    };
});
