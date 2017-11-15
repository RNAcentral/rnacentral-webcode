var MainContent = function($scope, $anchorScroll, $location, search) {
    $scope.displaySearchInterface = false;
    $scope.search = search; // expose search service to templates

    /**
     * Enables scrolling to anchor tags.
     * <a ng-click="scrollTo('anchor')">Title</a>
     */
    $scope.scrollTo = function(id) {
        $location.hash(id);
        $anchorScroll(id);
    };

    /**
     * Watch `displaySearchInterface` in order to hide non-search-related content
     * when a search is initiated.
     */
    $scope.$watch(function() { return search.status; }, function (newValue, oldValue) {
        if (newValue !== null) {
            $scope.displaySearchInterface = !(newValue === 'off');
        }
    });

    /**
     * Watch query and if it changes, modify url accordingly.
     */
    $scope.$watch(function() { return search.query; }, function(newValue, oldValue) {
        if (newValue != oldValue && newValue) {
            $location.url('/search' + '?q=' + search.query);
        }
    });
};

angular.module('rnacentralApp').controller('MainContent', ['$scope', '$anchorScroll', '$location', 'search', MainContent]);
