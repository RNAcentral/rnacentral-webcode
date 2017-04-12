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
                $http({
                    url: $interpolate("/rna/{{upi}}/lineage")({ upi: ctrl.upi }),
                    method: 'GET'
                }).then(
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
    controller: ['publicationResource', function(publicationResource) {
        var ctrl = this;

        ctrl.$onInit = function() {
            var obj = this,
                target = $('#publications'),
                load_more_btn_id = '#load-more-publications',
                template_id = '#handlebars-publications',
                url = '/api/v1/rna/__URS__/publications?page_size=__PAGE_SIZE__';

            var page_size = 25;

            $.get(url.replace('__URS__', ctrl.upi).replace('__PAGE_SIZE__', page_size), function(data) {
                insert_content(data);
                obj.activate_abstract_buttons(target.find('.abstract-btn'));
            });

            // attach event to the load more button
            target.off('click').on('click', load_more_btn_id, function(){
                new_page_size = target.find('li').length + page_size;
                obj.load_publications(new_page_size);
            });

            function insert_content(data) {
                var source = $(template_id).html();
                var template = Handlebars.compile(source);
                data.total = data.count;
                data.count = data.results.length;
                var wrapper = {
                    data: data,
                };
                target.html(template(wrapper));
            }
        };
    }],
    template: '<div id="publications">' +
              '    <h2>Publications <small>{{ $ctrl.publications.count }}</small></h2>' +
              '    <ol ng-repeat="publication in $ctrl.publications"></ol>' +
              '        <div class="col-md-8">' +
              '            <li class="margin-bottom-10px">' +
              '                {{ publication }}' +
              '            </li>' +
              '        </div>' +
              '    </ol>' +
              '    <div class="col-md-8">' +
              '        {{#ifCond count '<' total}}' +
              '        <small class="text-muted">Displaying {{count}} of {{total}} publications</small>' +
              '        <br>' +
              '        <button class="btn btn-default btn-large" id="load-more-publications">Load more</button>' +
              '        {{/ifCond}}' +
              '    </div>' +
              '    <div class="row">' +
              '        <div ng-if="!$ctrl.response" class="col-md-12">' +
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

    $scope.xrefs = $http({
        url: $interpolate('/rna/{{upi}}/xrefs/{{taxid}}', false, null, true)({ upi: $scope.upi, taxid: $scope.taxid }),
        method: 'GET'
    }).then(
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
        },
        function(response) {
            // handle error
        }
    );

};
rnaSequenceController.$inject = ['$scope', '$location', '$http', '$interpolate', 'xrefResource', 'DTOptionsBuilder', 'DTColumnBuilder'];


angular.module("rnaSequence", ['datatables', 'ngResource'])
    .factory("xrefResource", xrefResourceFactory)
    .factory("publicationResource", publicationResourceFactory)
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent)
    .component("taxonomyComponent", taxonomyComponent)
    .component("publicationsComponent", publicationsComponent);

})();
