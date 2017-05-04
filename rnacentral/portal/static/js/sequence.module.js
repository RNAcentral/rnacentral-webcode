(function() {

var xrefsComponent = {
    bindings: {
        upi: '<',
        taxid: '<?',
        onActivatePublications: '&'
    },
    controller: ['$http', '$interpolate', '$timeout', function($http, $interpolate, $timeout) {
        var ctrl = this;

        ctrl.$onInit = function() {
            $http.get($interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi}), {timeout: 5000}).then(
                function(response) {
                    // set ctrl.xrefs (filtering by taxid, if given)
                    if (ctrl.taxid) {
                        ctrl.xrefs = response.data.results;
                        console.log(ctrl.xrefs);
                    }
                    else {
                        ctrl.xrefs = _.filter(response.data.results, function(result) {
                            return result.taxid == ctrl.taxid;
                        });
                    }

                    // ensure that xrefs data is rendered into the DOM
                    // before initializing DataTables
                    $timeout(function() {
                        var table = $("#annotations-table").DataTable({
                            "columnDefs": [
                                { targets: [0, 1, 2], visible: true },
                                { targets: [3, 4, 5], visible: false}
                            ], // hide columns, but keep them sortable
                            "autoWidth": true, // pre-recalculate column widths
                            "dom": "ftpil", // filter, table, pagination, information, length
                            //"paginationType": "bootstrap", // requires dataTables.bootstrap.js
                            "deferRender": false, // defer rendering until necessary
                            "language": {
                                "search": "", // don't display the "Search:" bit
                                "info": "_START_-_END_ of _TOTAL_", // change the informational text
                                "paginate": {
                                    "next": "",
                                    "previous": "",
                                }
                            },
                            "order": [[ 5, "desc" ]], // prioritize entries with genomic coordinates
                            "lengthMenu": [[5, 10, 20, 50, -1], [5, 10, 20, 50, "All"]],
                            "initComplete": function(settings, json) {
                                console.log("init complete");
                            }
                        });
                    });

                },
                function(response) {
                    // TODO: display an error message in template!
                }
            );
        }
    }],
    templateUrl: '/static/js/sequence-xrefs.html'
};


var citationsComponent = {
    bindings: {
        xref: '<',
        onActivatePublications: '&'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;

        ctrl.$onChanges = function(changes) {
            $http.get($interpolate('{{accession}}')({accession: ctrl.xref.accession.citations})).then(
                function(response) {
                    ctrl.citations = response.data;
                    ctrl.status = response.status;
                },
                function(response) {
                    ctrl.status = response.status;
                }
            );
        };

    }],
    template: '<span class="literature-refs">' +
              '  <button ng-click="citationsVisible = !citationsVisible" class="literature-refs-retrieve btn btn-default btn-xs pull-right help" title="Literature citations">' +
              '    <i ng-if="citationsVisible" class="fa fa-caret-up"></i><i ng-if="!citationsVisible" class="fa fa-caret-down"></i>' +
              '  </button>' +
              '  <div ng-if="citationsVisible && $ctrl.status >= 200 && $ctrl.status <= 299" class="literature-refs-content">' +
              '    <blockquote ng-repeat="citation in $ctrl.citations">' +
              '      <publication-component publication="citation"></publication-component>' +
              '    </blockquote>' +
              '    <button ng-click="$ctrl.onActivatePublications()" class="btn btn-default btn-sm show-publications-tab"><i class="fa fa-book"></i> All publications</button>' +
              '  </div>' +
              '  <div ng-if="citationsVisible && ($ctrl.status < 200 || $ctrl.status > 299)">' +
              '    Failed to load citations from server.' +
              '  </div>' +
              '</span>'
};


var taxonomyComponent = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate',  function($http, $interpolate) {
        var ctrl = this;

        ctrl.$onInit = function() {
            var d3_species_tree = $('#d3-species-tree');

            if (!document.createElement('svg').getAttributeNS) {
                d3_species_tree.html('Your browser does not support SVG');
            }
            else {
                $http.get($interpolate("/rna/{{upi}}/lineage")({ upi: ctrl.upi })).then(
                    function(response) {
                        ctrl.response = response;
                        d3SpeciesTree(response.data, ctrl.upi, '#d3-species-tree');
                    },
                    function(response) {
                        ctrl.response = response;
                    }
                )
            }
        };
    }],
    template: '<div id="d3-species-tree">' +
              '    <div ng-if="!$ctrl.response">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading taxonomic tree...</span>' +
              '    </div>' +
              '    <div ng-if="$ctrl.response.status >= 400" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
              '    </div>' +
              '</div>'
};


var publicationsComponent = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['publicationResource', function(publicationResource) {
        var ctrl = this;

        ctrl.$onInit = function() {
            ctrl.abstracts = {};
            ctrl.publications = ctrl.fetchPublications(25);
        };

        /**
         * Asynchronously downloads <pageSize> (e.g. 25) publications
         * on this sequences and stores in ctrl.publications.
         *
         * @param {int} [25] pageSize - how many publications to load
         * @returns {publicationResource promise} - Array-like of publications
         */
        ctrl.fetchPublications = function(pageSize) {
            pageSize = pageSize || 25;
            return publicationResource.get({ upi: this.upi, page_size: pageSize });
        };

        ctrl.loadMore = function(pageSize) {
            pageSize = pageSize || 25;
            var newPageSize = ctrl.publications.data.length + pageSize;
            ctrl.publications = fetchPublications(newPageSize);
        };
    }],
    template: '<div id="publications">' +
              '    <h2>Publications <small>{{ $ctrl.publications.count }} total</small></h2>' +
              '    <ol>' +
              '        <div ng-repeat="publication in $ctrl.publications.results" class="col-md-8">' +
              '            <li class="margin-bottom-10px">' +
              '                <publication-component publication="publication"></publication-component>' +
              '            </li>' +
              '        </div>' +
              '    </ol>' +
              '    <div ng-if="$ctrl.publications.count < $ctrl.publications.total" class="col-md-8">' +
              '        <small class="text-muted">Displaying {{ $ctrl.publication.count }} of {{ $ctrl.publications.total }} publications</small>' +
              '        <br>' +
              '        <button class="btn btn-default btn-large" id="load-more-publications" ng-click="$ctrl.loadMore">Load more</button>' +
              '    </div>' +
              '    <div class="row">' +
              '        <div ng-if="!$ctrl.publications" class="col-md-12">' +
              '            <i class="fa fa-spinner fa-spin fa-2x"></i>' +
              '            <span class="margin-left-5px">Loading publications...</span>' +
              '        </div>' +
              '    ' +
              '    </div>' +
              '</div>'
};


var publicationResourceFactory = function($resource) {
    return $resource(
        '/api/v1/rna/:upi/publications?page_size=:page',
        {upi: '@upi', page: '@page'},
        {
            get: {timeout: 5000, isArray: false}
        }
    );
};
publicationResourceFactory.$inject = ['$resource'];


var publicationComponent = {
    bindings: {
        publication: '<'
    },
    controller: [function() {
        var ctrl = this;

        ctrl.$onChanges = function(changes) {
            ctrl.publication = changes.publication.currentValue;
        }
    }],
    template: '<strong ng-if="$ctrl.publication.title">{{ $ctrl.publication.title }}</strong>' +
              '<br ng-if="$ctrl.publication.title">' +
              '<small>' +
              '    <span ng-repeat="author in $ctrl.publication.authors track by $index"><a href="/search?q=author:&#34;{{ author }}&#34;">{{ author }}</a>{{ $last ? "" : ", " }}</span>' +
              '    <br ng-if="$ctrl.publication.authors && $ctrl.publication.authors.length">' +
              '    <em ng-if="$ctrl.publication.publication">{{ $ctrl.publication.publication }}</em>' +
              '    <span ng-if="$ctrl.publication.pubmed_id">' +
              '        <a href="http://www.ncbi.nlm.nih.gov/pubmed/{{ $ctrl.publication.pubmed_id }}" class="margin-left-5px">Pubmed</a>' +
              '        <a ng-if="$ctrl.publication.doi" href="http://dx.doi.org/{{ $ctrl.publication.doi }}" target="_blank" class="abstract-control">Full text</a>' +
              '        <abstract-component publication="$ctrl.publication"></abstract-component>' +
              '    </span>' +
              '  <br>' +
              '  <a href="/search?q=pub_id:&#34;{{ $ctrl.publication.pubmed_id }}&#34;" class="margin-left-5px"><i class="fa fa-search"></i> Find other sequences from this reference</a>' +
              '</small>'
};


var abstractComponent = {
    bindings: {
        publication: '<'
    },
    require: {
        parent: '^publicationComponent'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;

        ctrl.$onChanges = function(changes) {
            ctrl.publication = changes.publication.currentValue;
            ctrl.fetchAbstract(ctrl.publication.pubmed_id);
        };

        /**
         * Asynchronously downloads abstract for paper with given
         * pubmed_id (if available) and adds it to ctrl.abstracts.
         * Due to ugly JSONP syntax, we use raw $http instead of
         * resources here.
         *
         * @param {int|null|undefined} pubmed_id - paper's PubMed id
         * @return {HttpPromise|null}
         */
        ctrl.fetchAbstract = function(pubmed_id) {
            if (pubmed_id) {
                return $http.jsonp(
                    $interpolate('http://www.ebi.ac.uk/europepmc/webservices/rest/search?query=ext_id:{{ pubmed_id }}&format=json&resulttype=core')({pubmed_id: pubmed_id})
                ).then(
                    function(response) {
                        ctrl.abstract = response.data.resultList.result[0].abstractText;
                    },
                    function(response) {
                        ctrl.abstract = "Failed to download abstract";
                    }
                );
            }
            else {
                ctrl.abstract = "Abstract is not available";
                return null;
            }
        };

    }],
    template: '<button class="btn btn-xs btn-default abstract-btn abstract-control" ng-click="abstractVisible = !abstractVisible"><span ng-if="abstractVisible">Hide abstract</span><span ng-if="!abstractVisible">Show abstract</span></button>' +
              '<div ng-if="abstractVisible" class="abstract-text slide-down">{{ $ctrl.abstract }}</div>'
};


var rnaSequenceController = function($scope, $location) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3]; // TODO: this might not exist!

    // programmatically switch tabs
    $scope.activeTab = 0;
    $scope.activateTab = function(index) {
        $scope.activeTab = parseInt(index); // have to convery index to string
    };

    activateCopyToClipboardButtons();
    activateModifiedNucleotides();

    /**
     * Modified nucleotides visualisation.
     */
    function activateModifiedNucleotides() {
        $('body').on('click', 'button[data-modifications]', function() {
            // destroy any existing popovers before reading in the sequence
            $('.modified-nt').popover('destroy');
            var $pre = $('#rna-sequence'),
                text = $pre.text(),
                modifications = $(this).data('modifications'),
                arrayLength = modifications.length,
                seq_new = '',
                start = 0,
                template = Handlebars.compile($("#handlebars-modified-nt-popover-tmpl").html());

            // loop over modifications and insert span tags with modified nucleotide data
            for (var i = 0; i < arrayLength; i++) {
              seq_new += text.slice(start, modifications[i].position - 1) +
                         template(modifications[i].chem_comp);
              start = modifications[i].position;
            }
            seq_new += text.slice(start, text.length);

            // update the sequence (use `html`, not `text`)
            $pre.html(seq_new);
            // bring sequence in the viewport
            scroll_to_pre();
            // show the entire sequence
            $pre.css({
              'overflow': 'auto',
              'max-height': 'initial',
            });
            // initialize popovers
            $('.modified-nt').popover({
              placement: 'top',
              html: true,
              container: 'body',
              viewport: '#rna-sequence',
            });
            // activate the first popover
            $('.modified-nt').first().focus().popover('show');

            /**
             * Scroll to the sequence.
             */
            function scroll_to_pre() {
              $('html, body').animate({
                  scrollTop: $('pre').offset().top - 100
              }, 1200);
            }
        });
    }

    /**
     * Copy to clipboard buttons allow the user to copy an RNA sequence as RNA or DNA into
     * the clipboard by clicking on them. Buttons are located near the Sequence header.
     */
    function activateCopyToClipboardButtons() {
        /**
         * Returns DNA sequence, corresponding to input RNA sequence. =)
         */
        function reverseTranscriptase(rna) {
            // case-insensitive, global replacement of U's with T's
            return rna.replace(/U/ig, 'T');
        }

        var rnaClipboard = new Clipboard('#copy-as-rna', {
            "text": function() {
                var rna = $('#rna-sequence').text();
                rna = rna.replace(/\s/g, ''); // remove whitespace chars (arising due to colored <spans> in sequence)
                return rna;
            }
        });

        var dnaClipbaord = new Clipboard('#copy-as-dna', {
            "text": function() {
                var rna = $('#rna-sequence').text();
                rna = rna.replace(/\s/g, ''); // remove whitespace chars (arising due to colored <spans> in sequence)
                var dna = reverseTranscriptase(rna);
                return dna;
            }
        });
    };
};
rnaSequenceController.$inject = ['$scope', '$location'];


/**
 * Configuration function that allows this module to load data
 * from white-listed domains (required for JSONP from ebi.ac.uk).
 * @param $sceDelegateProvider
 */
var sceWhitelist = function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        'self',
        // Allow loading from EBI
        'http://www.ebi.ac.uk/**'
    ]);
};
sceWhitelist.$inject = ['$sceDelegateProvider'];


angular.module("rnaSequence", ['datatables', 'ngResource', 'ngAnimate'])
    .config(sceWhitelist)
    .factory("publicationResource", publicationResourceFactory)
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent)
    .component("citationsComponent", citationsComponent)
    .component("taxonomyComponent", taxonomyComponent)
    .component("publicationsComponent", publicationsComponent)
    .component("publicationComponent", publicationComponent)
    .component("abstractComponent", abstractComponent);

})();
