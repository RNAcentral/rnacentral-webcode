var textSearchBar = {
    bindings: {},
    templateUrl: '/static/js/components/text-search/text-search-bar/text-search-bar.html',
    controller: ['$interpolate', '$location', '$window', '$timeout', '$http', 'search', function($interpolate, $location, $window, $timeout, $http, search) {
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

        /**
         * Sends ajax to text-search help page, copy-pastes its content to the modal,
         * copies over that modal to <body> and opens it.
         */
        ctrl.openTextSearchHelpModal = function() {
            // request text search help from the backend
            $http.get('/help/text-search').then(
                function(result) {
                    // copy-paste help content from text search help page to the modal
                    var $helpContents = $( $(result.data).find('#help-content').get(0) );
                    $helpContents.find('h1').get(0).remove(); // remove page header - we already have a header in modal

                    // make search examples clickable
                    $helpContents.find('code').each(function() {
                        var $this = $(this);
                        var link = '<a target="_blank" rel="nofollow" href="/search?q=' + encodeURIComponent($this.html()) + '">' + $this.html() + '</a>';
                        $this.html(link);
                    });

                    // style table
                    $helpContents.find('table').addClass('table table-bordered table-responsive');

                    // remove fa-links
                    $helpContents.find('a').each(function() {
                        $(this).find('i.fa-link').remove();
                    });

                    // copy over help contents to the modal
                    $('#text-search-help-modal-parent #modal-body').html($helpContents.html());

                    // move modal from our component's html to <body>
                    $('#text-search-help-modal-parent').detach().appendTo('body');

                    // open modal; possible options: { backdrop: true, keyboard: true, show: true }
                    $('#text-search-help-modal-parent').modal();
                }
            );
        }
    }]
};

angular.module('textSearch').component('textSearchBar', textSearchBar);