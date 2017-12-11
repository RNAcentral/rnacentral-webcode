var publication = {
    bindings: {
        publication: '<',
        showFindOtherSequences: '@?'  // true/false - if we should show "Find other sequences from this reference" link
    },
    controller: ['routes', function(routes) {
        var ctrl = this;

        ctrl.routes = routes;
    }],
    template: '<strong ng-if="$ctrl.publication.title">{{ $ctrl.publication.title }}</strong> <span ng-if="$ctrl.publication.expert_db" class="label label-default">expert-database</span>' +
              '<br ng-if="$ctrl.publication.title">' +
              '<small>' +
              '    <div ng-if="$ctrl.publication.authors && $ctrl.publication.authors.length" style="height: 1em; line-height: 1em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin: 5px 0px;">' +
              '        <span ng-repeat="author in $ctrl.publication.authors track by $index">' +
              '            <a href="/search?q=author:&#34;{{ author }}&#34;">{{ author }}</a>{{ $last ? "" : ", " }}' +
              '        </span>' +
              '    </div>' +
              '    <em ng-if="$ctrl.publication.publication">{{ $ctrl.publication.publication }}</em>' +
              '    <em ng-if="$ctrl.publication.journal">{{ $ctrl.publication.journal }}</em>' +
              '    <span ng-if="$ctrl.publication.pubmed_id">' +
              '        <a href="http://www.ncbi.nlm.nih.gov/pubmed/{{ $ctrl.publication.pubmed_id }}" class="margin-left-5px">Pubmed</a>' +
              '        <a href="https://europepmc.org/abstract/MED/{{ $ctrl.publication.pubmed_id }}" class="margin-left-5px">EuropePMC</a>' +
              '        <a ng-if="$ctrl.publication.doi" href="http://dx.doi.org/{{ $ctrl.publication.doi }}" target="_blank" class="abstract-control">Full text</a>' +
              '        <abstract publication="$ctrl.publication"></abstract>' +
              '    </span>' +
              '  <br>' +
              '  <a ng-if="$ctrl.showFindOtherSequences" href="{{ $ctrl.routes.textSearch() }}?q=pub_id:&#34;{{ $ctrl.publication.pub_id }}&#34;" class="margin-left-5px"><i class="fa fa-search"></i> Find other sequences from this reference</a>' +
              '</small>'
};

angular.module("rnaSequence").component("publication", publication);
