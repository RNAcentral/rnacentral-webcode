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
              '<div ng-if="abstractVisible" class="abstract-text slide-down"><span ng-bind-html="$ctrl.abstract | linky"></span></div>'
};
