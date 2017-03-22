(function() {

    function urlencodeSpecies() {
        /**
         * Replaces whitespaces with underscores in input string (assumed to be a scientific name of species)
         * and converts it to lower case.
         *
         * @param input (string} - capitalized scientific name of a species with whitespaces, e.g. Homo sapiens
         * @returns {string} - scientific name of species with whitespaces replaces with underscores
         */
        return function(input) {
            // Canis familiaris is a special case
            if (input == 'Canis familiaris') {
                input = 'Canis lupus familiaris';
            }
            return input.replace(/ /g, '_').toLowerCase();
        }
    }
    urlencodeSpecies.$inject = [];

    function urldecodeSpecies() {
        /**
         * Replaces underscores with whitespaces in input string and capitalizes the first letter in it.
         *
         * @param input {string} - scientific name of a species in lower case with '_', e.g. homo_sapiens
         * @returns {string} - capitalized scientific name of a species with whitespaces, e.g. Homo sapiens
         */
        return function(input) {
            if (input == 'canis_lupus_familiaris') {
                input = 'canis_familiaris';
            }
            var output = input.replace(/_/g, ' ');
            output = output.charAt(0).toUpperCase() + output.slice(1);
            return output;
        }
    }
    urldecodeSpecies.$inject = [];

    function chrToUCSC() {
        /**
         * UCSC nomencalture for chromosomes is slightly different from Ensembl. This is a converter.
         *
         * @param input {string} Ensembl-style chromosome name, e.g. '21', 'X', 'M' or 'D38368'
         * @returns {string} 'chr21', 'chrX', 'chrY' or 'D38368'
         */
        return function(input) {
            return 'chr' + input.toString();
        }
    }
    chrToUCSC.$inject = [];

    function genoverse($filter, $timeout) {
        /**
         * Returns the directive definition object for genoverse directive.
         */
        return {
            restrict: 'E',
            scope: {
                genome: '=',
                chromosome: '=',
                start: '=',
                end: '=',
                tracks: '='
            },
            template:
                "<div class='wrap genoverse-wrap'>" +
                "  <div id='genoverse'></div>" +
                "  <div id='for-tracks'></div>" +
                "</div>",
            transclude: true,
            controller: ['$scope', '$element', '$attrs', function($scope, $element, $attrs) {
                var ctrl = this;

                // Variables
                // ---------
                ctrl.trackConfigs = [];

                // Methods
                // -------
                ctrl.render = function() {
                    // generate (updated) Genoverse config

                    var tracks = [ Genoverse.Track.Scalebar ];
                    ctrl.trackConfigs.forEach(function(trackConfig) {
                        tracks.push(ctrl.parseTrackConfig(trackConfig));
                    });

                    var genoverseConfig = {
                        container: $element.find('#genoverse'),
                        width: $('.container').width(),
                        // if we want Genoverse itself to update url on scroll, say:
                        urlParamTemplate: false, // or set to: "chromosome=__CHR__&start=__START__&end=__END__",
                        chr: $scope.chromosome,
                        start: $scope.start,
                        end: $scope.end,
                        species: $scope.genome.species,
                        genome: $filter('urlencodeSpecies')($scope.genome.species),
                        plugins: ['controlPanel', 'karyotype', 'resizer', 'fileDrop'],
                        tracks: tracks
                    };

                    // create Genoverse browser
                    $scope.browser = new Genoverse(genoverseConfig);

                    // set browser -> Angular data flow
                    $scope.browser.on({
                        afterInit: function() { // when genoverse is already initialized, attach watches to it
                            // set Genoverse -> Angular data flow
                            $scope.genoverseToAngularWatches = ctrl.setGenoverseToAngularWatches();

                            // set Angular -> Genoverse data flow
                            $scope.angularToGenoverseWatches = ctrl.setAngularToGenoverseWatches();

                            $timeout(angular.noop);
                        },

                        // this event is called, whenever the user updates the browser viewport location
                        afterSetRange: function () {
                            // let angular update its model in response to coordinates change
                            // that's an anti-pattern, but no other way to use FRP in angular
                            $timeout(angular.noop);
                        }
                    });
                };

                /**
                 * A function to be called by nested genoverseTrack directives - they should
                 * push their configs into the list of controller's trackConfigs.
                 *
                 * @param trackConfig - object in our internal trackConfig format
                 */
                ctrl.pushTrackConfig = function(trackConfig) {
                    ctrl.trackConfigs.push(trackConfig)
                };

                /**
                 * Creates a Genoverse.Track child (in terms of Base.js) from our internal trackConfig format.
                 * Basically, conversion from our internal format includes:
                 *  - check, if url is a function - then call it
                 *  - apply '-extra' options
                 *
                 * @param trackConfig - our internal trackConfig format
                 * @returns {Genoverse.Track}
                 */
                ctrl.parseTrackConfig = function(trackConfig) {
                    var parsedConfig = angular.element.extend({}, trackConfig); // clone trackConfig

                    // parse model-related part of trackConfig
                    var modelConfig = {};

                    // parse url
                    modelConfig.url = typeof parsedConfig.url === 'function' ? parsedConfig.url() : parsedConfig.url;
                    delete parsedConfig.url;

                    if (parsedConfig.modelExtra) {
                        angular.element.extend(modelConfig, trackConfig.modelExtra);
                        delete parsedConfig.modelExtra;
                    }

                    parsedConfig.model = parsedConfig.model.extend(modelConfig);

                    // parse view
                    if (parsedConfig.viewExtra) {
                        parsedConfig.view = parsedConfig.view.extend(viewExtra);
                        delete parsedConfig.viewExtra;
                    }

                    // parse controller
                    if (parsedConfig.controllerExtra) {
                        parsedConfig.controller = parsedConfig.controller.extend(controllerExtra);
                        delete parsedConfig.controllerExtra;
                    }

                    // parse extra
                    if (parsedConfig.extra) {
                        angular.element.extend(parsedConfig, parsedConfig.extra);
                        delete parsedConfig.extra;
                    }

                    return Genoverse.Track.extend(parsedConfig);
                };

                /**
                 * Creates angular watches, observing Genoverse browser.
                 * Upon any changes in Genoverse, these watches will update this directive's scope variables.
                 *
                 * @returns {Array} - watches as functions - call them to unbind them
                 */
                ctrl.setGenoverseToAngularWatches = function() {
                    var speciesWatch = $scope.$watch('browser.species', function(newValue, oldValue) {
                        $scope.genome = getGenomeByName(newValue);
                    });

                    var chrWatch = $scope.$watch('browser.chr', function(newValue, oldValue) {
                        $scope.chromosome = newValue;
                    });

                    var startWatch = $scope.$watch('browser.start', function(newValue, oldValue) {
                        $scope.start = newValue;
                    });

                    var endWatch = $scope.$watch('browser.end', function(newValue, oldValue) {
                        $scope.end = newValue;
                    });

                    return [speciesWatch, chrWatch, startWatch, endWatch];
                };

                /**
                 * Creates angular watches, observing directive's scope variables.
                 * Upon any changes to those scope variables, Genoverse browser coordinates will be updated.
                 *
                 * @returns {[*,*,*,*]} - watches as functions - call them to unbind them
                 */
                ctrl.setAngularToGenoverseWatches = function() {
                    var startWatch = $scope.$watch('start', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            $scope.browser.moveTo($scope.chromosome, newValue, $scope.end, true);
                        }
                    });

                    var endWatch = $scope.$watch('end', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            $scope.browser.moveTo($scope.chromosome, $scope.start, newValue, true);
                        }
                    });

                    var chrWatch = $scope.$watch('chromosome', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            $scope.browser.moveTo(newValue, $scope.start, $scope.end, true);
                        }
                    });

                    var speciesWatch = $scope.$watch('genome', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            // destroy the old instance of browser and watches
                            $scope.genoverseToAngularWatches.forEach(function (element) { element(); }); // clear old watches
                            $scope.angularToGenoverseWatches.forEach(function (element) { element(); }); // clear old watches
                            $scope.browser.destroy(); // destroy genoverse and all callbacks and ajax requests
                            delete $scope.browser; // clear old instance of browser

                            // set the default location for the browser
                            $scope.chromosome = newValue.example_location.chromosome;
                            $scope.start = newValue.example_location.start;
                            $scope.end = newValue.example_location.end;

                            // create a new instance of browser and set the new watches for it
                            ctrl.render();
                        }
                    });

                    return [speciesWatch, chrWatch, startWatch, endWatch];
                };

                /**
                 * Makes browser "responsive" - if container changes width, so does the browser.
                 */
                ctrl.setGenoverseWidth = function() {
                    var w = $('.container').width();
                    $scope.browser.setWidth(w);

                    // resize might change viewport location - digest these changes
                    $timeout(angular.noop)
                };

                // Helper functions
                // ----------------

                /**
                 * Returns an object from genomes Array by its species name or null, if not found.
                 *
                 * @param name {string} e.g. "Homo sapiens" or "homo_sapiens" (like in url) or "human" (synonym)
                 * @returns {Object || null} element of genomes Array
                 */
                function getGenomeByName(name) {
                    name = name.replace(/_/g, ' '); // if name was urlencoded, replace '_' with whitespaces

                    for (var i = 0; i < genomes.length; i++) {
                        if (name.toLowerCase() == genomes[i].species.toLowerCase()) { // test scientific name
                            return genomes[i];
                        }
                        else { // if name is not a scientific name, may be it's a synonym?
                            var synonyms = []; // convert all synonyms to lower case to make case-insensitive comparison

                            genomes[i].synonyms.forEach(function(synonym) {
                                synonyms.push(synonym.toLowerCase());
                            });

                            if (synonyms.indexOf(name.toLowerCase()) > -1) return genomes[i];
                        }
                    }

                    return null; // if no match found, return null
                }
            }],
            link: function(scope, $element, attrs, ctrl, transcludeFn) {
                // We are going to temporarily add child directive's template to $element
                // so it can be linked to scope, but after it's linked, we detach it. Taken from:
                // http://stackoverflow.com/questions/23345207/transcluded-content-requires-the-controller-of-the-transcluding-directive
                transcludeFn(function(clone) {
                    $element.find('#for-tracks').append(clone);
                }).detach(); // <- Immediately detach it

                ctrl.render();

                // resize genoverse on browser width changes - attach once only
                $(window).on('resize', ctrl.setGenoverseWidth);
            }
        };
    }
    genoverse.$inject = ['$filter', '$timeout'];


    function genoverseTrack() {
        return {
            restrict: 'E',
            require: "^genoverse",
            template: "",
            scope: {
                'model':            '=',
                'modelExtra':       '=?',
                'view':             '=',
                'viewExtra':        '=?',
                'controller':       '=?',
                'controllerExtra':  '=?',
                'extra':            '=?',

                'name':             '=',
                'height':           '=?',
                'resizable':        '=?',
                'autoHeight':       '=?',
                'hideEmpty':        '=?',
                'margin':           '=?',
                'border':           '=?',
                'unsortable':       '=?',

                'url':              '=',
                'urlParams':        '=?',
                'data':             '=?',
                'allData':          '=?',
                'dataRequestLimit': '=?',
                'dataType':         '=?',
                'xhrFields':        '=?',

                'featureHeight':    '=?',
                'featureMargin':    '=?',
                'color':            '=?',
                'fontColor':        '=?',
                'fontWeight':       '=?',
                'fontHeight':       '=?',
                'fontFamily':       '=?',
                'labels':           '=?',
                'repeatLabel':      '=?',
                'bump':             '=?',
                'depth':            '=?',
                'threshold':        '=?',

                'clickTolerance':   '=?',

                'id':               '=?',
            },
            link: function(scope, element, attrs, genoverseCtrl) {
                var trackConfig = {};

                // MVC-related settings and extras
                // -------------------------------

                trackConfig.model          = scope.model;
                trackConfig.view           = scope.view;
                if (scope.controller)      trackConfig.controller = scope.controller;

                if (scope.modelExtra)      trackConfig.modelExtra = scope.modelExtra;
                if (scope.viewExtra)       trackConfig.viewExtra = scope.viewExtra;
                if (scope.controllerExtra) trackConfig.controllerExtra = scope.controllerExtra;

                if (scope.extra)           trackConfig.extra = scope.extra;

                // Display, resizing and reordering
                // --------------------------------

                trackConfig.name             = scope.name;
                trackConfig.height           = scope.height !== undefined           ? scope.height           : 12;
                trackConfig.resizable        = scope.resizable !== undefined        ? scope.resizable        : true;
                trackConfig.autoHeight       = scope.autoHeight !== undefined       ? scope.autoHeight       : undefined;
                trackConfig.hideEmpty        = scope.hideEmpty !== undefined        ? scope.hideEmpty        : undefined;
                trackConfig.margin           = scope.margin !== undefined           ? scope.margin           : 2;
                trackConfig.border           = scope.border !== undefined           ? scope.border           : true;
                trackConfig.unsortable       = scope.unsortable !== undefined       ? scope.unsortable       : false;

                // Fetching data
                // -------------

                trackConfig.url              = scope.url;
                trackConfig.urlParams        = scope.urlParams !== undefined        ? scope.urlParams        : undefined;
                trackConfig.data             = scope.data !== undefined             ? scope.data             : undefined;
                trackConfig.allData          = scope.allData !== undefined          ? scope.allData          : false;
                trackConfig.dataRequestLimit = scope.dataRequestLimit !== undefined ? scope.dataRequestLimit : undefined;
                trackConfig.dataType         = scope.dataType !== undefined         ? scope.dataType         : undefined; // in original Genoverse it is "json", but this breaks Sequence track;
                trackConfig.xhrFields        = scope.xhrFields !== undefined        ? scope.xhrFields        : undefined;

                // Drawing features
                // ----------------

                trackConfig.featureHeight    = scope.featureHeight !== undefined    ? scope.featureHeight    : undefined;
                trackConfig.featureMargin    = scope.featureMargin !== undefined    ? scope.featureMargin    : { top: 3, right: 1, bottom: 1, left: 0 };
                trackConfig.color            = scope.color !== undefined            ? scope.color            : "#000000";
                trackConfig.fontColor        = scope.fontColor !== undefined        ? scope.fontColor        : undefined;
                trackConfig.fontWeight       = scope.fontWeight !== undefined       ? scope.fontWeight       : "normal";
                trackConfig.fontHeight       = scope.fontHeight !== undefined       ? scope.fontHeight       : 10;
                trackConfig.fontFamily       = scope.fontFamily !== undefined       ? scope.fontFamily       : "sans-serif";
                trackConfig.labels           = scope.labels !== undefined           ? scope.labels           : true;
                trackConfig.repeatLabels     = scope.repeatLabels !== undefined     ? scope.repeatLabels     : false;
                if (scope.bump != undefined)               trackConfig.bump         = scope.bump;
                trackConfig.depth            = scope.depth !== undefined            ? scope.depth            : undefined;
                if (scope.threshold !== undefined)         trackConfig.threshold    = scope.threshold;

                // Interaction with features
                // -------------------------
                trackConfig.clickTolerance   = scope.clickTolerance !== undefined   ? scope.clickTolerance   : 0;

                // TODO: remove this in 2.0.0
                if (scope.id !== undefined)              trackConfig.id = scope.id;

                genoverseCtrl.pushTrackConfig(trackConfig);
            }
        }
    }
    genoverseTrack.$inject = [];

    angular.module("Genoverse", [])
        .filter("urlencodeSpecies", urlencodeSpecies)
        .filter("urldecodeSpecies", urldecodeSpecies)
        .filter("chrToUCSC", chrToUCSC)
        .directive("genoverse", genoverse)
        .directive("genoverseTrack", genoverseTrack);
})();
