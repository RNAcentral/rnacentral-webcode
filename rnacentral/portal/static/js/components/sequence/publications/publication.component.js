var publication = {
    bindings: {
        publication: '<'
    },
    controller: [function() {
        var ctrl = this;

        ctrl.$onChanges = function(changes) {
            ctrl.publication = changes.publication.currentValue;
        }
    }],
    template: '<strong ng-if="$ctrl.publication.title">{{ $ctrl.publication.title }}</strong>' +
              '<br ng-if="$ctrl.publication.title">' +
              '<small>' +
              '    <span ng-repeat="author in $ctrl.publication.authors track by $index"><a href="/search?q=author:&#34;{{ author }}&#34;">{{ author }}</a>{{ $last ? "" : ", " }}</span>' +
              '    <br ng-if="$ctrl.publication.authors && $ctrl.publication.authors.length">' +
              '    <em ng-if="$ctrl.publication.publication">{{ $ctrl.publication.publication }}</em>' +
              '    <em ng-if="$ctrl.publication.journal">{{ $ctrl.publication.journal }}</em>' +
              '    <span ng-if="$ctrl.publication.pubmed_id">' +
              '        <a href="http://www.ncbi.nlm.nih.gov/pubmed/{{ $ctrl.publication.pubmed_id }}" class="margin-left-5px">Pubmed</a>' +
              '        <a ng-if="$ctrl.publication.doi" href="http://dx.doi.org/{{ $ctrl.publication.doi }}" target="_blank" class="abstract-control">Full text</a>' +
              '        <abstract publication="$ctrl.publication"></abstract>' +
              '    </span>' +
              '  <br>' +
              '  <a href="/search?q=pub_id:&#34;{{ $ctrl.publication.pub_id }}&#34;" class="margin-left-5px"><i class="fa fa-search"></i> Find other sequences from this reference</a>' +
              '</small>'
};

angular.module("rnaSequence").component("publication", publication);
