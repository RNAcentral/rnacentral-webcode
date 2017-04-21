(function() {

var xrefResourceFactory = function($resource) {
    return $resource(
        '/api/v1/rna/:upi/xrefs/',
        {upi: '@upi', taxid: '@taxid', page: '@page'},
        {
            get: {timeout: 5000, isArray: false}
        }
    );
};
xrefResourceFactory.$inject = ['$resource'];


var xrefsComponent = {
    bindings: {
        upi: '@',
        taxid: '@?'
    },
    controller: function() {
        var ctrl = this;

        $scope.xrefs = xrefResource.get(
            {upi: this.upi, taxid: this.taxid},
            function (data) {
                // hide loading spinner
            },
            function () {
                // display error
            }
        );

        xrefResource.get(
            { upi: $scope.upi, taxid: $scope.taxid },
            function(data) {
                console.log($scope.xrefs);
            }
        );

    },
    templateUrl: "/static/js/xrefs.html"
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


var publicationsComponent = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['publicationResource', '$http', '$interpolate', function(publicationResource, $http, $interpolate) {
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

            return publicationResource.get(
                { upi: this.upi, page_size: pageSize },
                function(publications) {
                    // retrieve corresponding abstracts
                    for (var i=0; i < publications.results.length; i++) {
                        var pubmed_id = publications.results[i].pubmed_id;
                        ctrl.fetchAbstract(pubmed_id);
                    }
                }
            );
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
                        ctrl.abstracts[pubmed_id] = response.data.resultList.result[0].abstractText;
                    },
                    function(response) {
                        ctrl.abstracts[pubmed_id] = "Failed to download abstract";
                    }
                );
            }
            else {
                ctrl.abstracts[pubmed_id] = "Abstract is not available";
                return null;
            }
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
              '                <strong ng-if="publication.title">{{ publication.title }}</strong>' +
              '                <br ng-if="publication.title">' +
              '                <small>' +
              '                    <span ng-repeat="author in publication.authors track by $index"><a href="/search?q=author:&#34;{{ author }}&#34;">{{ author }}</a>{{ $last ? "" : ", " }}</span>' +
              '                    <br ng-if="publication.authors && publication.authors.length">' +
              '                    <em ng-if="publication.publication">{{ publication.publication }}</em>' +
              '                    <span ng-if="publication.pubmed_id">' +
              '                        <a href="http://www.ncbi.nlm.nih.gov/pubmed/{{ publication.pubmed_id }}" class="margin-left-5px">Pubmed</a>' +
              '                        <a ng-if="publication.doi" href="http://dx.doi.org/{{ publication.doi }}" target="_blank" class="abstract-control">Full text</a>' +
              '                        <button class="btn btn-xs btn-default abstract-btn abstract-control" ng-click="abstractVisible = !abstractVisible"><span ng-if="abstractVisible">Hide abstract</span><span ng-if="!abstractVisible">Show abstract</span></button>' +
              '                        <div ng-if="abstractVisible" class="abstract-text slide-down">{{ $ctrl.abstracts[publication.pubmed_id] }}</div>' +
              '                    </span>' +
              '                  <br>' +
              '                  <a href="/search?q=pub_id:&#34;{{ publication.pubmed_id }}&#34;" class="margin-left-5px"><i class="fa fa-search"></i> Find other sequences from this reference</a>' +
              '                </small>' +
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


var rnaSequenceController = function($scope, $location, $http, $interpolate, xrefResource, DTOptionsBuilder, DTColumnBuilder) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3]; // TODO: this might not exist!

    var xrefsUrl;
    if ($scope.taxid !== undefined) {
        xrefsUrl = $interpolate('/rna/{{upi}}/xrefs/{{taxid}}')({ upi: $scope.upi, taxid: $scope.taxid });
    } else {
        xrefsUrl = $interpolate('/rna/{{upi}}/xrefs')({ upi: $scope.upi});
    }

    $scope.xrefs = $http.get(xrefsUrl).then(
        function(response) {
            $("#annotations-table").html(response.data);
            $("#annotations-table").DataTable({
                "columns": [null, null, null, {"bVisible": false}, {"bVisible": false}, {"bVisible": false}], // hide columns, but keep them sortable
                "autoWidth": true, // pre-recalculate column widths
                "dom": "ftpil", // filter, table, pagination, information, length
                //"paginationType": "bootstrap", // requires dataTables.bootstrap.js
                "deferRender": true, // defer rendering until necessary
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
            $scope.enableGenomicFeatures = response.data.indexOf('View genomic location') > 0;
        },
        function(response) {
            // handle error
        }
    );

};
rnaSequenceController.$inject = ['$scope', '$location', '$http', '$interpolate', 'xrefResource', 'DTOptionsBuilder', 'DTColumnBuilder'];


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
    .factory("xrefResource", xrefResourceFactory)
    .factory("publicationResource", publicationResourceFactory)
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent)
    .component("taxonomyComponent", taxonomyComponent)
    .component("publicationsComponent", publicationsComponent);

})();
