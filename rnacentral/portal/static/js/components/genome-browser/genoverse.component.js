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
                        populateMenu: ctrl.genoverseUtils.RNAcentralPopulateMenu,
                        resizable   : 'auto',
                        autoHeight  : true,
                        hideEmpty   : false
                    })
                ],
                loadGenome: function () {
                    if (typeof this.genome === 'string') {
                        var genomeName = this.genome;

                        return $.ajax({
                            url      : '/api/v1/karyotypes/' + genomeName,
                            dataType : 'json',
                            context  : this,
                            success  : function (result) {
                                Genoverse.Genomes[genomeName] = result;
                                this.genome = Genoverse.Genomes[genomeName];

                                if (!this.genome) {
                                    this.die('Unable to load genome ' + genomeName);
                                }
                            }
                        });
                    }
                },
                /**
                 * Override loadPlugins to hard-code genoverse location, so that Genoverse survives minification.
                 */
                loadPlugins: function (plugins) {
                    var browser         = this;
                    var loadPluginsTask = $.Deferred();

                    plugins = plugins || this.plugins;

                    this.loadedPlugins = this.loadedPlugins || {};

                    for (var i in Genoverse.Plugins) {
                      this.loadedPlugins[i] = this.loadedPlugins[i] || 'script';
                    }

                    if (typeof plugins === 'string') {
                      plugins = [ plugins ];
                    }

                    function loadPlugin(plugin) {
                      var css      = '/static/node_modules/@rnacentral/genoverse/dist/' + 'css/'        + plugin + '.css';
                      var js       = '/static/node_modules/@rnacentral/genoverse/dist/' + 'js/plugins/' + plugin + '.js';
                      var deferred = $.Deferred();

                      function getCSS() {
                        function done() {
                          browser.loadedPlugins[plugin] = browser.loadedPlugins[plugin] || 'script';
                          deferred.resolve(plugin);
                        }

                        if (Genoverse.Plugins[plugin].noCSS || $('link[href="' + css + '"]').length) {
                          return done();
                        }

                        $('<link href="' + css + '" rel="stylesheet">').on('load', done).appendTo('body');
                      }

                      if (browser.loadedPlugins[plugin] || $('script[src="' + js + '"]').length) {
                        getCSS();
                      } else {
                        $.getScript(js, getCSS);
                      }

                      return deferred;
                    }

                    function initializePlugin(plugin) {
                      if (typeof Genoverse.Plugins[plugin] !== 'function' || browser.loadedPlugins[plugin] === true) {
                        return [];
                      }

                      var requires = Genoverse.Plugins[plugin].requires;
                      var deferred = $.Deferred();

                      function init() {
                        if (browser.loadedPlugins[plugin] !== true) {
                          Genoverse.Plugins[plugin].call(browser);
                          browser.container.addClass('gv-' + plugin.replace(/([A-Z])/g, '-$1').toLowerCase() + '-plugin');
                          browser.loadedPlugins[plugin] = true;
                        }

                        deferred.resolve();
                      }

                      if (requires) {
                        $.when(browser.loadPlugins(requires)).done(init);
                      } else {
                        init();
                      }

                      return deferred;
                    }

                    // Load plugins css file
                    $.when.apply($, $.map(plugins, loadPlugin)).done(function () {
                      var pluginsLoaded = [];
                      var plugin;

                      for (var i = 0; i < arguments.length; i++) {
                        plugin = arguments[i];

                        if (browser.loadedPlugins[plugin] !== true) {
                          pluginsLoaded.push(initializePlugin(plugin));
                        }
                      }

                      $.when.apply($, pluginsLoaded).always(loadPluginsTask.resolve);
                    });

                    return loadPluginsTask;
                  },

            };

            ctrl.browser = new Genoverse(genoverseConfig);
            // catch (e) {
            //     if (e instanceof TypeError) {
            //         ctrl.browser.destroy();
            //         delete ctrl.browser;
            //         genoverseConfig.plugins = ['controlPanel', 'resizer', 'fileDrop'];
            //         ctrl.browser = new Genoverse(genoverseConfig);
            //     }
            // }

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

            // resize genoverse on browser width changes, if container passed - attach once only
            $(window).on('resize', ctrl.setGenoverseWidth);
        };

        /**
         * Makes browser "responsive" - if container changes width, so does the browser.
         */
        ctrl.setGenoverseWidth = function() {
            // if $scope.container passed, makes browser width responsive
            var width = $('.genoverse-wrap').width();
            ctrl.browser.setWidth(width);

            // resize might change viewport location - digest these changes
            $timeout(angular.noop)
        };

        // Hooks
        // -----

        this.$onInit = function() {
            ctrl.render();
            setTimeout(function() {
                ctrl.setGenoverseWidth();
            }, 1000);
        };

        ctrl.$doCheck = function() {
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
                    console.log("Can't find example location for genome ", ctrl.genome);
                }

                ctrl.render(); // create a new instance of browser

                ctrl.oldGenome = ctrl.genome;
                ctrl.oldChr = ctrl.oldBrowserChr = ctrl.chr;
                ctrl.oldStart = ctrl.oldBrowserStart = ctrl.start;
                ctrl.oldEnd = ctrl.oldBrowserEnd = ctrl.end;
            }
            else if (ctrl.genome === ctrl.oldGenome && (ctrl.chr !== ctrl.oldChr || ctrl.start !== ctrl.oldStart || ctrl.end !== ctrl.oldEnd )) {
                ctrl.browser.moveTo(ctrl.chr, ctrl.start, ctrl.end, true);
            }
            else if (ctrl.browser.start != ctrl.oldBrowserStart) {
                ctrl.start = ctrl.oldStart = ctrl.oldBrowserStart = ctrl.browser.start;
            }
            else if (ctrl.browser.end != ctrl.oldBrowserEnd) {
                ctrl.end = ctrl.oldEnd = ctrl.oldBrowserEnd = ctrl.browser.end;
            }
            else if (ctrl.browser.chr != ctrl.oldBrowserChr) {
                ctrl.chr = ctrl.oldBrowserChr = ctrl.oldChr = ctrl.browser.chr;
            }
            else if (ctrl.highlights !== ctrl.oldHighlights) {
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
