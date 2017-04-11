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
        $scope.xrefs = xrefResource.get(
            {upi: this.upi, taxid: this.taxid},
            function (data) {
                // hide loading spinner
            },
            function () {
                // display error
            }
        );
    },
    templateUrl: "/static/js/xrefs.html"
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

        xrefResource.get(
            { upi: $scope.upi, taxid: $scope.taxid },
            function(data) {
                console.log($scope.xrefs);
            }
        );

};
rnaSequenceController.$inject = ['$scope', '$location', '$http', '$interpolate', 'xrefResource', 'DTOptionsBuilder', 'DTColumnBuilder'];


angular.module("rnaSequence", ['datatables', 'ngResource'])
    .factory("xrefResource", xrefResourceFactory)
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent);

})();
