var xrefPublications = {
    bindings: {
        xref: '<',
        onActivatePublications: '&'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;

        ctrl.onClick = function() {
            $http.get($interpolate('{{publications}}')({publications: ctrl.xref.accession.citations}), {cache: true}).then(
                function(response) {
                    ctrl.publications = response.data.results;  // response is paginated
                    ctrl.status = response.status;
                },
                function(response) {
                    ctrl.status = response.status;
                }
            );
        }

    }],
    template: '<span class="literature-refs">' +
              '  <button ng-click="publicationsVisible = !publicationsVisible; $ctrl.onClick()" class="literature-refs-retrieve btn btn-default btn-xs pull-right help" title="Literature publications">' +
              '    <i ng-if="publicationsVisible" class="fa fa-caret-up"></i><i ng-if="!publicationsVisible" class="fa fa-caret-down"></i>' +
              '  </button>' +
              '  <div ng-if="publicationsVisible && $ctrl.status >= 200 && $ctrl.status <= 299" class="literature-refs-content slide-down">' +
              '    <blockquote ng-repeat="publication in $ctrl.publications">' +
              '      <publication publication="publication" show-find-other-sequences="true"></publication>' +
              '    </blockquote>' +
              '    <button ng-click="$ctrl.onActivatePublications()" class="btn btn-default btn-sm show-publications-tab"><i class="fa fa-book"></i> All publications</button>' +
              '  </div>' +
              '  <div ng-if="publicationsVisible && ($ctrl.status < 200 || $ctrl.status > 299)">' +
              '    Failed to load publications from server.' +
              '  </div>' +
              '</span>'
};

angular.module("rnaSequence").component("xrefPublications", xrefPublications);
