(function() {

var xrefResourceFactory = function() {
    return $resource(
        '/rna/:upi/xrefs/:taxid?page=:page',
        {upi: '@upi', taxid: '@taxid', page: '@page'},
        {
            get: {timeout: 5000}
        }
    );
};

var xrefsComponent = {
    bindings: {
        upi: '@',
        taxid: '@?'
    },
    controller: function() {
        var xrefs = xrefResource.get(
            {upi: this.upi, taxid: this.taxid},
            function (data) {

            },
            function () {

            }
        );
    },
    templateUrl: $location
};

angular.module("rnaSequence", [])
    .controller("rnaSequenceController", rnaSequenceController)
    .component("xrefsComponent", xrefsComponent)
    .factory("xrefResource", xrefResourceFactory);

})();
