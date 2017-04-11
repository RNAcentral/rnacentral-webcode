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
                    console.log(response);
                    ctrl.response = response;
                    d3SpeciesTree(response.data, ctrl.upi, '#d3-species-tree');
                },
                function(response) {
                    console.log(response);
                    ctrl.response = response;
                }
            )
        }
    }],
    template: '<div id="d3-species-tree">' +
              '    <div ng-hide="ctrl.response.status">' +
              '        <i class="fa fa-spinner fa-spin fa-2x"></i><span class="margin-left-5px">Loading taxonomic tree...</span>' +
              '    </div>' +
              '    <div ng-show="ctrl.response.status" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
              '    </div>' +
              '    <div ng-show="ctrl.response.status" class="alert alert-danger fade">' +
              '        <i class="fa fa-exclamation-triangle"></i>Sorry, there was a problem loading the data. Please try again and contact us if the problem persists.' +
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
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent)
    .component("taxonomyComponent", taxonomyComponent);

})();
