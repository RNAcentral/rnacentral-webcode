var genoverse = {
    bindings: {
        genome:           '=',
        chr:              '=',
        start:            '=',
        end:              '=',

        highlights:       '=?',

        genoverseUtils:   '='
    },
    controller: ['$http', '$interpolate', '$timeout', function($http, $interpolate, $timeout) {
        var ctrl = this;

        // Variables
        // ---------
        ctrl.trackConfigs = [];

        // Methods
        // -------
        ctrl.render = function() {
            // <genoverse-track name="'Sequence'" model="Genoverse.Track.Model.Sequence.Ensembl" view="Genoverse.Track.View.Sequence" controller="Genoverse.Track.Controller.Sequence" url="genoverseUtils.urls.sequence" resizable="'auto'" auto-height="true" hide-empty="false" extra="{100000: false}"></genoverse-track>
            // <genoverse-track name="'Genes'" labels="true" info="'Ensembl API genes'" model="Genoverse.Track.Model.Gene.Ensembl" view="Genoverse.Track.View.Gene.Ensembl" url="genoverseUtils.urls.genes" resizable="'auto'" auto-height="true" hide-empty="false" extra="{populateMenu: genoverseUtils.genesPopulateMenu}"></genoverse-track>
            // <genoverse-track name="'Transcripts'" labels="true" info="'Ensembl API transcripts'" model="Genoverse.Track.Model.Transcript.Ensembl" view="Genoverse.Track.View.Transcript.Ensembl" url="genoverseUtils.urls.transcripts" resizable="'auto'" auto-height="true" hide-empty="false" extra="{populateMenu: genoverseUtils.transcriptsPopulateMenu}"></genoverse-track>
            // <genoverse-track name="'RNAcentral'" id="'RNAcentral'" info="'Unique RNAcentral Sequences'" model="Genoverse.Track.Model.Gene.Ensembl" model-extra="{parseData: genoverseUtils.RNAcentralParseData}" view="Genoverse.Track.View.Transcript.Ensembl" url="genoverseUtils.urls.RNAcentral" extra="{populateMenu: genoverseUtils.RNAcentralPopulateMenu}" resizable="'auto'" auto-height="true" hide-empty="false"></genoverse-track>

            // create Genoverse browser
            var genoverseConfig = {
                container: $('#genoverse'),
                width: $('#genoverse').width(),

                chr: ctrl.chr,
                start: ctrl.start,
                end: ctrl.end,
                genome: ctrl.genome,

                urlParamTemplate: false,

                highlights: ctrl.highlights,
                plugins: ['controlPanel', 'karyotype', 'resizer', 'fileDrop'],
                tracks: [
                    Genoverse.Track.Scalebar,
                    Genoverse.Track.extend({
                        name       : 'Sequence',
                        url        : ctrl.genoverseUtils.urls.sequence(),
                        controller : Genoverse.Track.Controller.Sequence,
                        model      : Genoverse.Track.Model.Sequence.Ensembl,
                        view       : Genoverse.Track.View.Sequence,
                        100000     : false,
                        resizable  : 'auto',
                        autoHeight : true,
                        hideEmpty  : false
                    }),
                    Genoverse.Track.extend({
                        name        : 'Genes',
                        labels      : true,
                        info        : 'Ensembl API genes',
                        url         : ctrl.genoverseUtils.urls.genes(),
                        model       : Genoverse.Track.Model.Gene.Ensembl,
                        view        : Genoverse.Track.View.Gene.Ensembl,
                        100000      : false,
                        populateMenu: ctrl.genoverseUtils.genesPopulateMenu,
                        resizable   : 'auto',
                        autoHeight  : true,
                        hideEmpty   : false
                    }),
                    Genoverse.Track.extend({
                        name        : 'Transcripts',
                        labels      : true,
                        info        : 'Ensembl API transcripts',
                        url         : ctrl.genoverseUtils.urls.transcripts(),
                        model       : Genoverse.Track.Model.Transcript.Ensembl,
                        view        : Genoverse.Track.View.Transcript.Ensembl,
                        100000      : false,
                        populateMenu: ctrl.genoverseUtils.transcriptsPopulateMenu,
                        resizable   : 'auto',
                        autoHeight  : true,
                        hideEmpty   : false
                    }),
                    Genoverse.Track.extend({
                        name        : 'RNAcentral',
                        info        : 'Unique RNAcentral Sequences',
                        url         : ctrl.genoverseUtils.urls.RNAcentral(),
                        model       : Genoverse.Track.Model.Gene.Ensembl.extend({parseData: ctrl.genoverseUtils.RNAcentralParseData}),
                        view        : Genoverse.Track.View.Transcript.Ensembl,
                        100000      : false,
                        populateMenu: ctrl.genoverseUtils.RNAcentralPopulateMenu,
                        resizable   : 'auto',
                        autoHeight  : true,
                        hideEmpty   : false
                    })
                ]
            };
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

            // initialize old state for $doCheck hook
            ctrl.oldBrowserStart = ctrl.browser.start;
            ctrl.oldBrowserEnd = ctrl.browser.end;
            ctrl.oldBrowserChr = ctrl.browser.chr;

            ctrl.oldStart = ctrl.start;
            ctrl.oldEnd = ctrl.end;
            ctrl.oldChr = ctrl.chr;
            ctrl.oldGenome = ctrl.genome;
            ctrl.oldHighlights = ctrl.highlights;
        };

        // Hooks
        // -----

        this.$onInit = function() {
            ctrl.render();
        };

        ctrl.$doCheck = function() {
            if (ctrl.browser.start != ctrl.oldBrowserStart) {
                ctrl.start = ctrl.oldStart = ctrl.oldBrowserStart = ctrl.browser.start;
            }
            if (ctrl.browser.end != ctrl.oldBrowserEnd) {
                ctrl.end = ctrl.oldEnd = ctrl.oldBrowserEnd = ctrl.browser.end;
            }
            if (ctrl.browser.chr != ctrl.oldBrowserChr) {
                ctrl.chr = ctrl.oldBrowserChr = ctrl.oldChr = ctrl.browser.chr;
            }

            if (ctrl.genome === ctrl.oldGenome && (ctrl.chr !== ctrl.oldChr || ctrl.start !== ctrl.oldStart || ctrl.end !== ctrl.oldEnd )) {
                ctrl.browser.moveTo(ctrl.chr, ctrl.start, ctrl.end, true);
            }
            if (ctrl.genome !== ctrl.oldGenome) {
                // destroy the old instance of browser and watches
                if (ctrl.browser) {
                    ctrl.browser.destroy(); // destroy genoverse and all callbacks and ajax requests
                    delete ctrl.browser; // clear old instance of browser
                }

                // set the default location for the browser
                if (ctrl.genoverseUtils.exampleLocations[ctrl.genome]) {
                    ctrl.chr = ctrl.genoverseUtils.exampleLocations[ctrl.genome].chr;
                    ctrl.start = ctrl.genoverseUtils.exampleLocations[ctrl.genome].start;
                    ctrl.end = ctrl.genoverseUtils.exampleLocations[ctrl.genome].end;
                } else {
                    alert("Can't find example location for genome ", ctrl.genome);
                }

                ctrl.render(); // create a new instance of browser

                ctrl.oldGenome = ctrl.genome;
                ctrl.oldChr = ctrl.oldBrowserChr = ctrl.chr;
                ctrl.oldStart = ctrl.oldBrowserStart = ctrl.start;
                ctrl.oldEnd = ctrl.oldBrowserEnd = ctrl.end;
            }
            if (ctrl.highlights !== ctrl.oldHighlights) {
                ctrl.browser.addHighlights(ctrl.highlights);
                ctrl.oldHighlights = ctrl.highlights;
            }

        };

    }],
    template: "<div class='wrap genoverse-wrap'>" +
              "  <div id='genoverse'></div>" +
              "</div>",
};

angular.module("genomeBrowser").component("genoverse", genoverse);