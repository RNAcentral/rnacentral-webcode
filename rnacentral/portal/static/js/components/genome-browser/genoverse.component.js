var genoverse = {
    bindings: {
        genome:           '=',
        chr:              '=',
        start:            '=',
        end:              '=',

        exampleLocations: '=?', // our addition, allows to switch species

        highlights:       '=?'
    },
    require: {
        parent: '^publication'
    },
    controller: ['$http', '$interpolate', '', function($http, $interpolate) {
        var ctrl = this;

        // Variables
        // ---------
        ctrl.trackConfigs = [];

        // Methods
        // -------
        ctrl.render = function() {
            // create Genoverse browser
            var genoverseConfig = ctrl.parseConfig();
            ctrl.browser = new Genoverse(genoverseConfig);

            // set browser -> Angular data flow
            ctrl.browser.on({
                // this event is called, whenever the user updates the browser viewport location
                afterSetRange: function () {
                    // let angular update its model in response to coordinates change
                    // that's an anti-pattern, but no other way to use FRP in angular
                    $timeout(angular.noop);
                }
            });
        };

        /**
         * Parses $scope variables and applies defaults, where necessary, constructing genoverseConfig
         * @returns {Object} - config, suitable for calling new Genoverse(genoverseConfig);
         */
        ctrl.parseConfig = function() {
            // Required + hard-coded
            // ---------------------
            var genoverseConfig = {
                container: $('#genoverse'),
                width: $('#genoverse').width(),

                chr: ctrl.chr,
                start: ctrl.start,
                end: ctrl.end,
                genome: ctrl.genome,

                highlights: ctrl.highlights,
                plugins: ['controlPanel', 'karyotype', 'resizer', 'fileDrop'],
                tracks: [
                    Genoverse.Track.Scalebar,
                    Genoverse.Track.extend({
                        name       : 'Sequence',
                        controller : Genoverse.Track.Controller.Sequence,
                        model      : Genoverse.Track.Model.Sequence.Ensembl,
                        view       : Genoverse.Track.View.Sequence,
                        100000     : false,
                        url        : genoverseUtils.urls.sequence,
                        resizable  : 'auto',
                        autoHeight : true,
                        hideEmpty  : false
                    }),
                    Genoverse.Track.extend({
                        name        : 'Genes',
                        labels      : true,
                        info        : 'Ensembl API genes',
                        url         : genoverseUtils.urls.genes,
                        model       : Genoverse.Track.Model.Sequence.Ensembl,
                        view        : Genoverse.Track.View.Sequence,
                        100000      : false,
                        populateMenu: genoverseUtils.genesPopulateMenu,
                        resizable   : 'auto',
                        autoHeight : true,
                        hideEmpty  : false
                    }),
                    Genoverse.Track.extend({
                        name       : 'Transcripts',
                        labels     : true,
                        info       : 'Ensembl API transcripts',
                        url        : genoverseUtils.urls.transcripts,
                        model      : Genoverse.Track.Model.Transcript.Ensembl,
                        view       : Genoverse.Track.View.Transcript.Ensembl,
                        100000     : false,
                        resizable  : 'auto',
                        autoHeight : true,
                        hideEmpty  : false
                    }),
                    Genoverse.Track.extend({
                        name        : 'RNAcentral',
                        info        : 'Unique RNAcentral Sequences',
                        url         : genoverseUtils.urls.RNAcentral,
                        controller  : Genoverse.Track.Controller.Sequence,
                        model       : Genoverse.Track.Model.Gene.Ensembl({parseData: genoverseUtils.RNAcentralParseData}),
                        view        : Genoverse.Track.View.Transcript.Ensembl,
                        100000      : false,
                        resizable   : 'auto',
                        populateMenu: genoverseUtils.RNAcentralPopulateMenu,
                        autoHeight  : true,
                        hideEmpty   : false
                    })
                ]
            };

            return genoverseConfig;
        };

        // <genoverse-track name="'Sequence'" model="Genoverse.Track.Model.Sequence.Ensembl" view="Genoverse.Track.View.Sequence" controller="Genoverse.Track.Controller.Sequence" url="genoverseUtils.urls.sequence" resizable="'auto'" auto-height="true" hide-empty="false" extra="{100000: false}"></genoverse-track>
        // <genoverse-track name="'Genes'" labels="true" info="'Ensembl API genes'" model="Genoverse.Track.Model.Gene.Ensembl" view="Genoverse.Track.View.Gene.Ensembl" url="genoverseUtils.urls.genes" resizable="'auto'" auto-height="true" hide-empty="false" extra="{populateMenu: genoverseUtils.genesPopulateMenu}"></genoverse-track>
        // <genoverse-track name="'Transcripts'" labels="true" info="'Ensembl API transcripts'" model="Genoverse.Track.Model.Transcript.Ensembl" view="Genoverse.Track.View.Transcript.Ensembl" url="genoverseUtils.urls.transcripts" resizable="'auto'" auto-height="true" hide-empty="false" extra="{populateMenu: genoverseUtils.transcriptsPopulateMenu}"></genoverse-track>
        // <genoverse-track name="'RNAcentral'" id="'RNAcentral'" info="'Unique RNAcentral Sequences'" model="Genoverse.Track.Model.Gene.Ensembl" model-extra="{parseData: genoverseUtils.RNAcentralParseData}" view="Genoverse.Track.View.Transcript.Ensembl" url="genoverseUtils.urls.RNAcentral" extra="{populateMenu: genoverseUtils.RNAcentralPopulateMenu}" resizable="'auto'" auto-height="true" hide-empty="false"></genoverse-track>

        ctrl.$onChanges = function(changes) {
            // ctrl.publication = changes.publication.currentValue;
            // ctrl.fetchAbstract(ctrl.publication.pubmed_id);
        };

        ctrl.render();
    }],
    template: "<div class='wrap genoverse-wrap'>" +
              "  <div id='genoverse'></div>" +
              "</div>",
};

angular.module("genomeBrowser").component("genoverse", genoverse);