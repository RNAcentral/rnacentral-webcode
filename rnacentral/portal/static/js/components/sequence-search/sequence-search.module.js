var sequenceSearchController = function($scope, $http, $timeout, $location, $q, $window, routes, normalizeExpertDbName) {
    $scope.query = {
        sequence: '',
        submitAttempted: false,
        elapsedTime: 0
    };

    $scope.results = {
        id: null,
        entries: [],
        facets: [],
        selectedFacets: {}, // e.g. { facetId1: [facetValue1.value, facetValue2.value], facetId2: [facetValue3.value] }
        hitCount: null,
        start: 0,
        size: 20,
        exactMatch: {},
        textSearchError: false
    };

    $scope.defaults = {
        pollingInterval: 1000, // milliseconds
        minLength: 10, // nucleotides
        maxLength: 10000 // nucleotides
    };

    $scope.messages = {
        getResuts: 'Loading results',
        done: 'Done',
        failed: 'Error',
        submitFailed: 'There was a problem submitting your query. Please try again later or get in touch if the error persists.',
        jobFailed: 'There was a problem with your query. Please try again later or get in touch if the error persists.',
        resultsFailed: 'There was a problem retrieving the results. Please try again later or get in touch if the error persists.',
        notFoundFailed: 'Job with the specified id was not found.',
        cancelled: 'The search was cancelled',
        pending: 'Pending',
        started: 'Running',
        pollJobStatus: 'Waiting for results',
        submitting: 'Submitting query',
        loadingMoreResults: 'Loading more results',
        tooShort: 'The sequence cannot be shorter than ' + $scope.defaults['minLength'].toString() + ' nucleotides',
        expertDbsError: 'Failed to retrieve the list of expert databases.',
        textSearchError: 'Failed to retrieve text search facets from EBI search.'
    };

    $scope.help = {
        rfam: "/help/rfam-annotations",
        crs: "/help/conserved-motifs",
        go: "/help/gene-ontology-annotations",
        genomeMapping: "/help/genomic-mapping"
    };

    $scope.ordering = [
        { sortField: 'e_value', label: 'E-value (low to high)'},
        { sortField: '-e_value', label: 'E-value (high to low)'},
        { sortField: '-identity', label: 'Identity ↓' },
        { sortField: 'identity', label: 'Identity ↑' },
        { sortField: '-query_coverage', label: 'Query coverage ↓' },
        { sortField: 'query_coverage', label: 'Query coverage ↑' },
        { sortField: '-target_coverage', label: 'Target coverage ↓' },
        { sortField: 'target_coverage', label: 'Target coverage ↑' }
    ];

    $scope.params = {
        searchInProgress: false,
        progress: 0,
        errorMessage: '',
        statusMessage: '',
        showAlignments: true,
        selectedOrdering: $scope.ordering[0],
        textSearchError: false
    };

    var timeout;

    // ########################################################################
    // #                        Data access functions                         #
    // ########################################################################

    /**
     * Retrieve results given a results url.
     */
    $scope.fetchJobResults = function(id, nextPage, query) {
        $scope.params.searchInProgress = true;
        $scope.params.statusMessage = $scope.messages.getResuts;
        id = id || $location.search().id;

        nextPage = nextPage || false;
        if (!nextPage) { $scope.results.start = 0; }

        if (!query) { $scope.results.selectedFacets = {}; }
        query = query || "rna";

        $http({
            url: routes.sequenceSearchResults({ jobId: id }),
            method: 'GET',
            params: {
                ordering: $scope.params.selectedOrdering.sortField,
                start: $scope.results.start,
                size: $scope.results.size,
                query: query
            }
        }).then(
            function(response) {
                $scope.results.hitCount = response.data.hitCount;

                if (nextPage) {
                    $scope.results.entries = $scope.results.entries.concat(response.data.entries);
                } else {
                    $scope.results.entries = response.data.entries;
                }

                $scope.results.start = $scope.results.entries.length;

                $scope.results.facets = response.data.facets;
                $scope.results.textSearchError = response.data.textSearchError;

                $scope.params.searchInProgress = false;
                $scope.params.statusMessage = $scope.messages.done;

                $scope.updateOrdering();
                updatePageTitle();
                updateFacetMetadata();
            },
            function(response) {
                $scope.params.searchInProgress = false;
                $scope.params.statusMessage = $scope.messages.failed;
                if (response.status === 404) {
                    $scope.params.errorMessage = $scope.messages.notFoundFailed;
                } else {
                    $scope.params.errorMessage = $scope.messages.resultsFailed;
                }
                updatePageTitle();
            }
        );
    };

    /**
     * Check job status using REST API.
     */
    function fetchJobStatus(id) {
        return $http({
            url: routes.sequenceSearchJobStatus({ jobId: id }),
            method: 'GET',
            ignoreLoadingBar: true
        }).then(
            function(response) {
                $scope.query.elapsedTime = response.data.elapsedTime;

                if (response.data.description) {
                    $scope.query.sequence = '>' + response.data.description + '\n' + response.data.query;
                } else {
                    $scope.query.sequence = response.data.query;
                }

                if (response.data.status === 'success' || response.data.status === 'partial_success' ) {
                    $scope.params.progress = 100;
                    $scope.fetchJobResults(response.data.id);
                }
                else if (response.data.status === 'error') {
                    $scope.params.searchInProgress = false;
                    $scope.params.statusMessage = $scope.messages.failed;
                    $scope.params.errorMessage = $scope.messages.jobFailed;
                    updatePageTitle();
                }
                else {
                    $scope.params.searchInProgress = true;
                    if (response.data.status === 'pending') {
                        $scope.params.statusMessage = $scope.messages.pending;
                        $scope.params.progress = 0;
                    } else if (response.data.status === 'started') {
                        $scope.params.statusMessage = $scope.messages.started;
                        $scope.params.progress = estimateProgress(response.data.chunks);
                    } else {
                        $scope.params.statusMessage = '';
                    }
                    timeout = setTimeout(function() {
                        fetchJobStatus(id);
                        updatePageTitle();
                    }, $scope.defaults.pollingInterval);
                }
            },
            function(response) {
                $scope.params.statusMessage = $scope.messages.failed;
                if (response.status === 404) {
                    $scope.params.errorMessage = $scope.messages.notFoundFailed;
                } else {
                    $scope.params.errorMessage = $scope.messages.resultsFailed;
                }
            }
        );
    }

    /**
     * If sequenceOrUpi is upi, fetch and return the actual sequence from backend.
     */
    function fetchRnacentralSequence(sequenceOrUpi) {
        var deferred = $q.defer();
        if (sequenceOrUpi.match(/^URS[A-Fa-f0-9]{10}$/i)) {
            $http({ url: routes.apiRnaView({ upi: sequenceOrUpi }) }).then(function(response){
                $scope.query.sequence = '>' + response.data.rnacentral_id + '\n' + response.data.sequence;
                deferred.resolve($scope.query.sequence);
            });
        } else {
            deferred.resolve(sequenceOrUpi);
            return deferred.promise;
        }
        return deferred.promise;
    }

    /**
     * Post query to run a job.
     */
    function submitJob(sequence) {
        return $http.post(
            routes.sequenceSearchSubmitJob({}),
            { query: sequence, databases: []}
        ).then(function(response) {
            var id = response.data.job_id;

            // save job id
            $scope.results.id = id;

            // update url
            $location.search({ 'id': id });

            // begin polling for results
            fetchJobStatus(id);
            updatePageTitle();
        }, function(response) {
            $scope.params.errorMessage = $scope.messages.submitFailed;
            $scope.params.statusMessage = $scope.messages.failed;
            $scope.params.searchInProgress = false;
            updatePageTitle();
        });
    }

    /**
     * Use RNAcentral API to retrieve an exact match
     * to the query sequence.
     */
    function fetchExactMatch(sequence) {
        input = parseInput(sequence);
        var md5Hash = md5(input.sequence.toUpperCase().replace(/U/g, 'T'));
        var url = routes.ebiMd5Lookup({md5: md5Hash, ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT});
        $http({
            url: url,
            method: 'GET',
        }).then(function(response) {
            if (response.data.hitCount > 0) {
                $scope.results.exactMatch = {
                    'description': response.data.entries[0].fields.description[0],
                    'rnacentral_id': response.data.entries[0].id,
                    'count': response.data.hitCount,
                    'urs_id': response.data.entries[0].id.split('_')[0],
                }
            }
        });
    }

    /**
     * Fetch rnacentral databases data for displaying tootips on databases facet.
     */
    function fetchExpertDbs() {
        // retrieve expert_dbs json for display in tooltips
        $http.get(routes.expertDbsApi({ expertDbName: '' })).then(
            function(response) {
                $scope.expertDbs = response.data;

                // expertDbsObject has lowerCase db names as keys
                $scope.expertDbsObject = {};
                for (var i=0; i < $scope.expertDbs.length; i++) {
                    $scope.expertDbsObject[$scope.expertDbs[i].name.toLowerCase()] = $scope.expertDbs[i];
                }
            },
            function(response) {
                $scope.params.errorMessage = $scope.messages.expertDbsError;
                $scope.params.statusMessage = $scope.messages.failed;
                $scope.params.searchInProgress = false;
                updatePageTitle();
            }
        );
    }

    /**
     * Tweak facet labels and values.
     */
    function updateFacetMetadata() {
        $scope.results.facets.forEach(function(facet) {
            if (facet.id === 'qc_warning_found') {
                facet.facetValues.forEach(function(facetValue) {
                    if (facetValue.label === 'True') { facetValue.label = 'Yes'; }
                    else if (facetValue.label === 'False') { facetValue.label = 'No'; }
                });
            }
            if (facet.id === 'has_conserved_structure') {
                facet.label = 'Conserved motifs';
                facet.facetValues.forEach(function(facetValue) {
                    if (facetValue.label === 'True') { facetValue.label = 'Found'; }
                    else if (facetValue.label === 'False') { facetValue.label = 'Not found'; }
                });
            }
            if (facet.id === 'has_go_annotations') {
                facet.label = 'GO annotations';
                facet.facetValues.forEach(function(facetValue) {
                    if (facetValue.label === 'True') { facetValue.label = 'Found'; }
                    else if (facetValue.label === 'False') { facetValue.label = 'Not found'; }
                });
            }
            if (facet.id === 'qc_warning_found') {
                facet.label = 'QC warnings';
                facet.facetValues.forEach(function(facetValue) {
                    if (facetValue.label === 'Yes') { facetValue.label = 'Warnings found'; }
                    else if (facetValue.label === 'No') { facetValue.label = 'No warnings'; }
                });
            }
            if (facet.id === 'has_secondary_structure') {
                facet.label = 'Secondary structure';
                facet.facetValues.forEach(function(facetValue) {
                    if (facetValue.label === 'True') { facetValue.label = 'Available'; }
                    else if (facetValue.label === 'False') { facetValue.label = 'Not available'; }
                });
            }
        });
    }


    // ########################################################################
    // #         Controller functions to be called from html template         #
    // ########################################################################

    /**
     * Add standard Javascript isNaN function to the scope
     * so that it can be used in the template.
     */
    $scope.isNaN = isNaN;

    /**
     * Expose normalizeExpertDbName service to the template.
     */
    $scope.normalizeExpertDbName = normalizeExpertDbName;

    /**
     * Reset the form.
     */
    $scope.reset = function() {
        $location.search({});
        $scope.params.searchInProgress = false;
        $scope.query = {
            sequence: '',
            submitAttempted: false,
            elapsedTime: 0
        };
        $scope.results = {
            id: null,
            entries: [],
            facets: [],
            selectedFacets: {},
            hitCount: null,
            start: 0,
            size: 20,
            exactMatch: {},
            textSearchError: false
        };
        $scope.params.statusMessage = '';
        $scope.params.errorMessage = '';
        $('textarea').focus();
        updatePageTitle();
    };

    /**
     * Launch the search from template.
     */
    $scope.sequenceSearch = function(sequence) {
        $scope.query.sequence = sequence;
        search(sequence);
    };

    /**
     * Format e-value.
     */
    $scope.formatEvalue = function(eValue) {
        return parseFloat(eValue).toExponential(2);
    };

    /**
     * Toggle alignments button.
     */
    $scope.toggleAlignments = function() {
        $scope.params.showAlignments = !$scope.params.showAlignments;
        $('#toggle-alignments').html(function(i, text){
          var icon = '<i class="fa fa-align-justify"></i> ';
          return icon + (text.indexOf("Show alignments") > -1 ? "Hide alignments" : "Show alignments");
        });
    };

    /**
     * Calculate query sequence length
     * (without whitespace and fasta header).
     */
    $scope.getQueryLength = function() {
        var text = document.getElementById("query-sequence").value;
        if (text.match(/^URS[A-Fa-f0-9]{10}$/)) {
            return 0;
        }
        input = parseInput(text);
        return input.sequence.length || 0;
    };

    /**
     * Reverse the query sequence in place and repeat the search.
     * This is helpful when the user accidentally types the sequence in 3' to 5' direction.
     */
    $scope.reverseAndRepeatSearch = function() {
        var input = parseInput($scope.query.sequence);
        var reversedSequence = input.sequence.split("").reverse().join("");
        var descriptionLine = '';
        if (input.description) {
          descriptionLine = '>' + input.description + '\n';
        }
        $scope.query.sequence = descriptionLine + reversedSequence;
        search($scope.query.sequence);
    };

    /**
     * Update the `ordering` url parameter
     * based on the current user selection.
     */
    $scope.updateOrdering = function() {
        $location.search($.extend($location.search(), {
            ordering: $scope.params.selectedOrdering.sortField
        }));
    };

    /**
     * Public method for submitting the query.
     */
    $scope.submitQuery = function() {
        $scope.query.submitAttempted = true;
        if (!$scope.seqQueryForm.$valid) {
            return;
        }
        search($scope.query.sequence);
    };

    /**
     * Load more results.
     */
    $scope.loadMoreResults = function() {
        var nextPage = true;
        $scope.fetchJobResults($scope.results.id, nextPage);
    };

    /**
     * Scroll page to the top.
     */
    $scope.scrollToTop = function() {
        $("html, body").animate({ scrollTop: "0px" });
    };

    /**
     * For each facet checks, if it is applied.
     */
    $scope.isFacetApplied = function(facetId, facetValueValue) {
        return $scope.results.selectedFacets.hasOwnProperty(facetId) && $scope.results.selectedFacets[facetId].indexOf(facetValueValue) !== -1;
    };

    /**
     * Event handler, fired when a facet is toggled/
     */
    $scope.facetToggled = function(facetId, facetValueValue) {
        if ($scope.results.selectedFacets.hasOwnProperty(facetId)) {
            var index = $scope.results.selectedFacets[facetId].indexOf(facetValueValue);
            if (index === -1) {
                $scope.results.selectedFacets[facetId].push(facetValueValue);
            } else {
                $scope.results.selectedFacets[facetId].splice(index, 1);
            }
        } else {
            $scope.results.selectedFacets[facetId] = [ facetValueValue ];
        }

        var query = buildQuery();
        $scope.fetchJobResults($scope.results.id, false, query);
    };

    /**
     * We assign a star only to those expertDbs that have a curated tag and don't have automatic tag at the same time.
     * @param db {String} - name of expertDb as a key in expertDbsObject
     * @returns {boolean}
     */
    $scope.expertDbHasStar = function(db) {
        return $scope.expertDbsObject[db].tags.indexOf('curated') !== -1 && $scope.expertDbsObject[db].tags.indexOf('automatic') === -1;
    };

    // ########################################################################
    // #                         Utility functions                            #
    // ########################################################################

    /**
     * Initiate sequence search.
     */
    function search(sequence) {
        $scope.results = {
            id: null,
            entries: [],
            facets: [],
            selectedFacets: {},
            hitCount: null,
            start: 0,
            size: 20,
            exactMatch: {},
            textSearchError: false
        };

        // set progress to zero
        $scope.params.progress = 0;

        // if sequence contains an rnacental_id/upi/urs, fetch the actual sequence
        fetchRnacentralSequence(sequence).then(function(sequence) {
            // Submit query and begin checking whether the results are ready.
            var input = parseInput(sequence);

            if (input.sequence.length < $scope.defaults.minLength) {
                $scope.params.errorMessage = $scope.messages.tooShort;
                $scope.params.statusMessage = $scope.messages.failed;
            } else {
                $scope.params.errorMessage = '';
                $scope.params.statusMessage = $scope.messages.submitting;
                $scope.params.searchInProgress = true;

                // run md5 fetch and actual job submission concurrently
                fetchExactMatch(sequence);
                submitJob(sequence);
            }
        });
    }

    /**
     * Parse fasta header, remove whitespace characters.
     */
    function parseInput(sequence) {
        var match = /(^>(.+)[\n\r])?([\s\S]+)/.exec(sequence);
        if (match) {
            return { sequence: match[3].replace(/\s/g, ''), description: match[2] || '' };
        } else {
            return { sequence: '', description: '' };
        }
    }

    /**
     * Show progress in page title.
     */
    function updatePageTitle() {
        if ($scope.params.statusMessage === $scope.messages.failed) {
            $window.document.title = 'Search failed';
        } else if ($scope.params.searchInProgress) {
            $window.document.title = 'Searching...';
        } else if ($scope.params.statusMessage === $scope.messages.done) {
            $window.document.title = 'Search done';
        } else {
            $window.document.title = 'Sequence search';
        }
    }

    /**
     * Constructs a text search (! not sequence search) query
     * from facets for EBI text search to use and display facets.
     */
    function buildQuery() {
        var outputText, outputClauses = [];

        Object.keys($scope.results.selectedFacets).map(function(facetId) {
            var facetText, facetClauses = [];
            $scope.results.selectedFacets[facetId].map(function(facetValueValue) {
                facetClauses.push(facetId + ':"' + facetValueValue + '"');
            });
            facetText = facetClauses.join(" OR ");

            if (facetText !== "") outputClauses.push("(" + facetText + ")");
        });

        outputText = outputClauses.join(" AND ");
        return outputText;
    }

    /**
     * Given jobChunks from jobStatus view, estimates the search progress.
     */
    function estimateProgress(chunks) {
        var progress = 0;
        chunks.map(function(chunk) {
            if (chunk.status === 'pending') { ; } // empty statment
            else if (chunk.status === 'started') { progress += 0.5 * (100.0 / chunks.length); }
            else { progress += (100.0 / chunks.length); }
        });

        progress = Math.ceil(progress);
        return progress
    }

    // ########################################################################
    // #                          Initialization                              #
    // ########################################################################

    /**
     * When the controller is first created:
     * - activate Bootstrap tooltips when the controller is created.
     * - retrieve search results if necessary
     */
    (function() {
        fetchExpertDbs();

        if ($location.url().indexOf("id=") > -1) {
            // load results, set their ordering based on the url parameter
            if ($location.search().ordering) {
                var ordering = $location.search().ordering;
                for (var i=0, len=$scope.ordering.length; i < len; i++) {
                    if ($scope.ordering[i].sortField === ordering) {
                        $scope.params.selectedOrdering = $scope.ordering[i];
                    }
                }
            }

            $scope.results.id = $location.search().id;

            fetchJobStatus($location.search().id).then(function() {
                fetchExactMatch($scope.query.sequence);
            });
        } else if ($location.search().q) {
            // start sequence search
            $scope.query.sequence = $location.search().q;
            search($scope.query.sequence);
        }

        $('body').tooltip({
            selector: '.help',
            delay: { show: 200, hide: 100 },
            container: 'body'
        });
    })();
};

angular.module("sequenceSearch", ['chieffancypants.loadingBar', 'ngResource', 'ngAnimate', 'ui.bootstrap', 'expertDatabase'])
    .controller("SequenceSearchController", ['$scope', '$http', '$timeout', '$location', '$q', '$window', 'routes', 'normalizeExpertDbName', sequenceSearchController]);
