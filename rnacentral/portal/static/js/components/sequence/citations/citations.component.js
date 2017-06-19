var citations = {
    bindings: {
        xref: '<',
        onActivatePublications: '&'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;

        ctrl.onClick = function() {
            $http.get($interpolate('{{citations}}')({citations: ctrl.xref.accession.citations}), {cache: true}).then(
                function(response) {
                    ctrl.citations = response.data;
                    ctrl.status = response.status;
                },
                function(response) {
                    ctrl.status = response.status;
                }
            );
        }

    }],
    template: '<span class="literature-refs">' +
              '  <button ng-click="citationsVisible = !citationsVisible; $ctrl.onClick()" class="literature-refs-retrieve btn btn-default btn-xs pull-right help" title="Literature citations">' +
              '    <i ng-if="citationsVisible" class="fa fa-caret-up"></i><i ng-if="!citationsVisible" class="fa fa-caret-down"></i>' +
              '  </button>' +
              '  <div ng-if="citationsVisible && $ctrl.status >= 200 && $ctrl.status <= 299" class="literature-refs-content slide-down">' +
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