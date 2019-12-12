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
            ctrl.randomExamples = ctrl.getRandomSearchExamples();
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
        };

        /**
         * Get random text search examples from each search category.
         */
        ctrl.getRandomSearchExamples = function() {
            examples = {
              'gene': [
                    {
                        'label': 'human HOTAIR',
                        'search_string': '"HOTAIR" homo sapiens',
                    },
                    {
                        'label': 'human RN7SL',
                        'search_string': 'RN7SL homo sapiens',
                    },
                    {
                        'label': 'KCNQ1OT1',
                        'search_string': 'KCNQ1OT1',
                    },
                ],
                'species': [
                    {
                        'label': 'Homo sapiens',
                        'search_string': 'TAXONOMY:"9606"',
                    },
                    {
                        'label': 'Mus musculus',
                        'search_string': 'TAXONOMY:"10090"',
                    },
                    {
                        'label': 'D. melanogaster',
                        'search_string': 'TAXONOMY:"7227"',
                    },
                    {
                        'label': 'primates',
                        'search_string': 'tax_string:"primates"',
                    },
                    {
                        'label': 'Escherichia coli',
                        'search_string': 'Escherichia coli',
                    },
                    {
                        'label': 'mammals',
                        'search_string': 'Mammalia',
                    },
                    {
                        'label': 'Alphaproteobacteria',
                        'search_string': 'tax_string:"Alphaproteobacteria"',
                    },
                ],
                'rna_type': [
                    {
                        'label': 'lncRNA',
                        'search_string': 'rna_type:"lncRNA"',
                    },
                    {
                        'label': 'miRNA',
                        'search_string': 'rna_type:"miRNA"',
                    },
                    {
                        'label': 'snoRNA',
                        'search_string': 'rna_type:"snoRNA"',
                    },
                    {
                        'label': 'snRNA',
                        'search_string': 'rna_type:"snRNA"',
                    },
                    {
                        'label': '5S rRNA',
                        'search_string': 'RF00001 AND has_secondary_structure:"True" AND expert_db:"5SrRNAdb"',
                    },
                    {
                        'label': 'LSU rRNA',
                        'search_string': '(RF02541 OR RF02543 OR RF02540) has_secondary_structure:"True" AND length:[1000 TO 6000]',
                    },
                    {
                        'label': 'SSU rRNA',
                        'search_string': '(RF00177 OR RF01960 OR RF01959) has_secondary_structure:"True" AND length:[1000 TO 3000]',
                    },
                ],
                'expert_db': [
                    {
                        'label': 'miRBase',
                        'search_string': 'expert_db:"miRBase"',
                    },
                    {
                        'label': 'FlyBase',
                        'search_string': 'expert_db:"FlyBase"',
                    },
                    {
                        'label': 'GtRNAdb',
                        'search_string': 'expert_db:"GtRNAdb"',
                    },
                    {
                        'label': 'HGNC',
                        'search_string': 'expert_db:"HGNC"',
                    },
                    {
                        'label': 'LNCipedia',
                        'search_string': 'expert_db:"LNCipedia"',
                    },
                    {
                        'label': 'TarBase',
                        'search_string': 'expert_db:"TarBase"',
                    },
                    {
                        'label': 'PDBe',
                        'search_string': 'expert_db:"PDBe"',
                    },
                  ],
                    'accession': [
                    {
                        'label': 'ENSG00000228630',
                        'search_string': 'ENSG00000228630',
                    },
                    {
                        'label': '4V4Q',
                        'search_string': '4V4Q',
                    },
                    {
                        'label': 'hsa-mir-126',
                        'search_string': '"hsa-mir-126"',
                    },
                    {
                        'label': "PMID:27174936",
                        'search_string': 'pubmed:"27174936"',
                    },
                    {
                        'label': 'GO:0043410',
                        'search_string': '"GO:2000352"',
                    },
                  ]
            }
            randomExamples = new Array();
            Object.keys(examples).forEach(function(example_type) {
                randomExamples.push(examples[example_type][Math.floor(Math.random()*examples[example_type].length)]);
            });
            return randomExamples;
        }
    }]
};

angular.module('textSearch').component('textSearchBar', textSearchBar);
