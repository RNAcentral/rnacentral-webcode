var textSearchBar = {
    bindings: {},
    templateUrl: '/static/js/components/text-search/text-search-bar/text-search-bar.html',
    controller: ['$interpolate', '$location', '$window', '$timeout', 'search', function($interpolate, $location, $window, $timeout, search) {
        var ctrl = this;
        ctrl.search = search;

        ctrl.$onInit = function() {
            ctrl.query = '';
            ctrl.submitted = false; // when form is submitted this flag is set; when its content is edited it is cleared

            // check if the url contains a query when the controller is first created and initiate a search if necessary
            if ($location.url().indexOf("/search?q=") > -1) {
                search.search($location.search().q); // a search result page, launch a new search
            }
        };

        /**
         * Watch search.query and if it's different from ctrl.query, check, who changed and sync if necessary
         */
        ctrl.$doCheck = function() {
            if (search.query != ctrl.query) {
                if (search.status == 'in progress') {
                    // this is a result of search.search() call => sync form input with search.query
                    ctrl.query = search.query;
                }
            }
        };

        /**
         * Called when user changes the value in query string.
         */
        ctrl.autocomplete = function(query) {
            return search.autocomplete(query).then(
                function(response) {
                    // make exact matches appear in the top of the list
                    var exactMatches = [], fuzzyMatches = [];
                    for (var i=0; i < response.data.suggestions.length; i++) {
                        var suggestion = response.data.suggestions[i].suggestion;
                        if (suggestion.indexOf(ctrl.query) === 0) exactMatches.push(suggestion);
                        else fuzzyMatches.push(suggestion);
                    }

                    return exactMatches.concat(fuzzyMatches);
                },
                function(response) {
                    return [];
                }
            );
        };

        /**
         * Called when the form is submitted. If request is invalid, just display error and die, else run search.
         */
        ctrl.submitQuery = function() {
            ctrl.queryForm.text.$invalid ? ctrl.submitted = true : search.search(ctrl.query);
        };
    }]
};
