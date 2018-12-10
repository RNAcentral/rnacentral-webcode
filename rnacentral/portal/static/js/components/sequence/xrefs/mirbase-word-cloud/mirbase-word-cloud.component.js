var mirbaseWordCloud = {
    bindings: {
        mirbaseId: '<'
    },
    controller: ['$http', '$interpolate', function($http, $interpolate) {
        var ctrl = this;

        /**
         * Launch a modal showing miRBase word cloud
         */
        ctrl.openMirbaseModal = function() {
            var mirbase_url = ctrl.getMirbaseWordCloudUrl(ctrl.mirbaseId);
            var html = '<img src="' + mirbase_url + '">' +
                       '<p>' +
                          '<a target="_blank" href="http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc='+ ctrl.mirbaseId + '">' +
                          'View ' + ctrl.mirbaseId + ' in miRBase</a>' +
                       '</p>';
            $('#modal-mirbase-word-cloud-image').html(html);
            $('#mirbase-modal-parent').detach().appendTo('body');
            $('#mirbase-modal-parent').modal();
        };

        /**
         * Get miRBase word cloud URL. Example ID: MI0006423.
         */
        ctrl.getMirbaseWordCloudUrl = function() {
          return '/api/internal/proxy?url=http://www.mirbase.org/images/wordcloud/' +
                 ctrl.mirbaseId.slice(2,4) + '/' + ctrl.mirbaseId.slice(4,6) + '/' +
                 ctrl.mirbaseId.slice(6,8) + '/' + ctrl.mirbaseId + '.png';
        }

    }],
    templateUrl: '/static/js/components/sequence/xrefs/mirbase-word-cloud/mirbase-word-cloud.html',
};

angular.module("rnaSequence").component("mirbaseWordCloud", mirbaseWordCloud);
