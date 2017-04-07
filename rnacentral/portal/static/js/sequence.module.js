(function() {

var xrefResourceFactory = function($resource) {
    return $resource(
        '/rna/:upi/xrefs/:taxid?page=:page',
        {upi: '@upi', taxid: '@taxid', page: '@page'},
        {
            get: {timeout: 5000}
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

var rnaSequenceController = function($scope, $location, xrefResource, DTOptionsBuilder, DTColumnBuilder) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3]; // TODO: this might not exist!

    $scope.xrefs = [{
        "id": 860,
        "firstName": "Superman",
        "lastName": "Yoda"
    }, {
        "id": 870,
        "firstName": "Foo",
        "lastName": "Whateveryournameis"
    }, {
        "id": 590,
        "firstName": "Toto",
        "lastName": "Titi"
    }, {
        "id": 803,
        "firstName": "Luke",
        "lastName": "Kyle"
    }];
    
    $scope.dtOptions = DTOptionsBuilder
        .fromSource('/api/v1/rna/' + $scope.upi + '/xrefs/')
        .withPaginationType('full_numbers')
        .withDisplayLength(10)
        .withDOM('ftpil');

    $scope.dtColumns = [
        DTColumnBuilder.newColumn('results.database').withTitle('Database'),
        DTColumnBuilder.newColumn('results.description').withTitle('Description'),
        DTColumnBuilder.newColumn('results.species').withTitle('Species')
    ];

};
rnaSequenceController.$inject = ['$scope', '$location', 'xrefResource', 'DTOptionsBuilder', 'DTColumnBuilder'];


angular.module("rnaSequence", ['datatables', 'ngResource'])
    .factory("xrefResource", xrefResourceFactory)
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent);

})();
