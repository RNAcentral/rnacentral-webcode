(function() {

    angular.module("Genoverse", [])
        .filter("urlencodeSpecies", urlencodeSpecies)
        .filter("urldecodeSpecies", urldecodeSpecies)
        .filter("chrToUCSC", chrToUCSC)
        .directive("genoverse", genoverse);


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

    function chrToUCSC() {
        /**
         * UCSC nomencalture for chromosomes is slightly different from Ensembl. This is a converter.
         *
         * @param input {string} Ensembl-style chromosome name, e.g. '21', 'X', 'M' or 'D38368'
         * @returns {string} 'chr21', 'chrX', 'chrY' or 'D38368'
         */
        return function(input) {
            if (input.toString().match(/^\d+$|^[XYM]$/)) {
                return 'chr' + input.toString();
            } else {
                return input.toString();
            }
        }
    }

    function genoverse($filter) {
        /**
         * Returns the directive definition object for genoverse directive.
         * It is meant to be used as follows:
         *
         * <genoverse genome={} chromosome="X" start="1" stop="1000000">
         *     <genoverse-track id="" name="Sequence" info="" label="true"
         *      url-template="{{protocol}}//{{endpoint}}/overlap/region/{{species}}/{{chromosome}}:{{start}}-{{end}}?feature=gene;content-type=application/json"
         *      url-variables="{protocol: 'https', endpoint: 'rest.ensembl.org'">
         *     </genoverse-track>
         * </genoverse>
         */
        return {
            restrict: 'E',
            scope: false,
            template:
                "<div class='wrap genoverse-wrap' style='overflow-x:auto;'>" +
                "    <p class='text-muted'>" +
                "        <span id='genomic-location' class='margin-right-5px'></span>" +
                "        View in <a href='http://{{domain}}/{{genome.species | urlencodeSpecies}}/Location/View?r={{chromosome}}:{{start}}-{{end}}' id='ensembl-link' target='_blank'>Ensembl</a>" +
                "        <span ng-show='genome.assembly_ucsc' class='ucsc-link'>|" +
                "            <a href='http://genome.ucsc.edu/cgi-bin/hgTracks?db={{genome.assembly_ucsc}}&position={{chromosome | chrToUCSC}}%3A{{start}}-{{end}}' target='_blank'>UCSC</a>" +
                "        </span>" +
                "    </p>" +
                "<div id='genoverse'></div>" +
                "</div>",
            link: function(scope, element, attrs) {

                // Initialization
                // --------------

                render();

                // resize genoverse on browser width changes - attach once only
                $('window').resize(setGenoverseWidth);

                // Functions/methods
                // -----------------

                function render() {
                    var genoverseConfig = {
                        container: element.find('#genoverse'),
                        // if we want Genoverse itself to update url on scroll, say:
                        urlParamTemplate: false, // or set to: "chromosome=__CHR__&start=__START__&end=__END__",
                        chr: scope.chromosome,
                        start: scope.start,
                        end: scope.end,
                        species: scope.genome.species,
                        genome: $filter('urlencodeSpecies')(scope.genome.species),
                        plugins: ['controlPanel', 'karyotype', 'resizer', 'fileDrop'],
                        tracks: [
                            Genoverse.Track.Scalebar,
                            Genoverse.Track.extend({
                                name: 'Sequence',
                                model: configureGenoverseModel('ensemblSequence'),
                                view: Genoverse.Track.View.Sequence,
                                controller: Genoverse.Track.Controller.Sequence,
                                resizable: 'auto',
                                autoHeight: true,
                                100000: false
                            }),
                            Genoverse.Track.extend({
                                name: 'Genes',
                                info: 'Ensembl API genes',
                                labels: true,
                                model: configureGenoverseModel('ensemblGene'),
                                view: Genoverse.Track.View.Gene.Ensembl,
                                controller: Genoverse.Track.Controller.Ensembl,
                                autoHeight: true
                            }),
                            Genoverse.Track.extend({
                                name: 'Transcripts',
                                info: 'Ensembl API transcripts',
                                labels: true,
                                model: configureGenoverseModel('ensemblTranscript'),
                                view: Genoverse.Track.View.Transcript.Ensembl,
                                controller: Genoverse.Track.Controller.Ensembl,
                                autoHeight: true
                            }),
                            Genoverse.Track.extend({
                                name: 'RNAcentral',
                                id: 'RNAcentral',
                                info: 'Unique RNAcentral Sequences',
                                labels: true,
                                model: configureGenoverseModel('rnacentral'),
                                view: Genoverse.Track.View.Transcript.Ensembl,
                                controller: Genoverse.Track.Controller.Ensembl,
                                autoHeight: true
                            })
                        ]
                    };

                    // get domain for Ensembl links
                    scope.domain = getEnsebmlSubdomainByDivision(scope.genome);

                    // create Genoverse browser
                    scope.browser = new Genoverse(genoverseConfig);

                    // set browser -> Angular data flow
                    scope.browser.on({
                        afterInit: function() { // when genoverse is already initialized, attach watches to it
                            // set Genoverse -> Angular data flow
                            scope.genoverseToAngularWatches = setGenoverseToAngularWatches();

                            // set Angular -> Genoverse data flow
                            scope.angularToGenoverseWatches = setAngularToGenoverseWatches();

                            // imperatively set the initial width of Genoverse
                            setGenoverseWidth();

                            if (!scope.$$phase) scope.$apply();
                        },

                        // this event is called, whenever the user updates the browser viewport location
                        afterSetRange: function () {
                            // let angular update its model in response to coordinates change
                            // that's an anti-pattern, but no other way to use FRP in angular
                            if (!scope.$$phase) scope.$apply();
                        }
                    });
                }

                function setGenoverseToAngularWatches() {
                    var speciesWatch = scope.$watch('browser.species', function(newValue, oldValue) {
                        scope.genome = getGenomeByName(newValue);
                        scope.domain = getEnsebmlSubdomainByDivision(scope.genome);
                    });

                    var chrWatch = scope.$watch('browser.chr', function(newValue, oldValue) {
                        scope.chromosome = newValue;
                    });

                    var startWatch = scope.$watch('browser.start', function(newValue, oldValue) {
                        scope.start = newValue;
                    });

                    var endWatch = scope.$watch('browser.end', function(newValue, oldValue) {
                        scope.end = newValue;
                    });

                    return [speciesWatch, chrWatch, startWatch, endWatch];
                }

                function setAngularToGenoverseWatches() {
                    var startWatch = scope.$watch('start', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            scope.browser.moveTo(scope.chromosome, newValue, scope.end, true);
                        }
                    });

                    var endWatch = scope.$watch('end', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            scope.browser.moveTo(scope.chromosome, scope.start, newValue, true);
                        }
                    });

                    var chrWatch = scope.$watch('chromosome', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            scope.browser.moveTo(newValue, scope.start, scope.end, true);
                        }
                    });

                    var speciesWatch = scope.$watch('genome', function(newValue, oldValue) {
                        if (!angular.equals(newValue, oldValue)) {
                            // destroy the old instance of browser and watches
                            scope.genoverseToAngularWatches.forEach(function (element) { element(); }); // clear old watches
                            scope.angularToGenoverseWatches.forEach(function (element) { element(); }); // clear old watches
                            scope.browser.destroy(); // destroy genoverse and all callbacks and ajax requests
                            delete scope.browser; // clear old instance of browser

                            // set the default location for the browser
                            scope.chromosome = newValue.example_location.chromosome;
                            scope.start = newValue.example_location.start;
                            scope.end = newValue.example_location.end;

                            // create a new instance of browser and set the new watches for it
                            render();
                        }
                    });

                    return [speciesWatch, chrWatch, startWatch, endWatch];
                }

                /**
                 * Each Genoverse model is configured with an organism-specific url.
                 * In addition, a new RNAcentral models that's mimicking Ensembl API is defined.
                 */
                function configureGenoverseModel(modelType) {
                    var model, url;
                    var endpoint = getEnsemblOrEnsemblgenomesEndpoint(scope.genome.species);

                    if (modelType === 'ensemblGene') {
                        // Ensembl Gene track
                        url = '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', $filter('urlencodeSpecies')(scope.genome.species));
                        model = Genoverse.Track.Model.Gene.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'ensemblTranscript') {
                        // Ensembl Transcript track
                        url = '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', $filter('urlencodeSpecies')(scope.genome.species));
                        model = Genoverse.Track.Model.Transcript.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'ensemblSequence') {
                        // Ensembl sequence view
                        url = '__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', $filter('urlencodeSpecies')(scope.genome.species));
                        model = Genoverse.Track.Model.Sequence.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'rnacentral') {
                        // custom RNAcentral track
                        if (!window.location.origin) { window.location.origin = window.location.protocol + "//" + window.location.host + '/'; }

                        url = window.location.origin + '/api/v1/overlap/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', $filter('urlencodeSpecies')(scope.genome.species));
                        model = Genoverse.Track.Model.Gene.Ensembl.extend({
                            url: url,
                            parseData: function (data) {
                                for (var i = 0; i < data.length; i++) {
                                    var feature = data[i];

                                    if (feature.feature_type === 'transcript' && !this.featuresById[feature.ID]) {
                                        feature.id    = feature.ID;
                                        feature.label = feature.external_name;
                                        feature.exons = [];
                                        feature.cds   = [];

                                        this.insertFeature(feature);
                                    }
                                    else if (feature.feature_type === 'exon' && this.featuresById[feature.Parent]) {
                                        feature.id = feature.ID;

                                        if (!this.featuresById[feature.Parent].exons[feature.id]) {
                                            this.featuresById[feature.Parent].exons.push(feature);
                                            this.featuresById[feature.Parent].exons[feature.id] = feature;
                                        }
                                    }
                                }
                            }
                        });
                    }

                  return model;
                }

                /**
                 * Dynamically choose whether to use E! or EG REST API based on species.
                 * If species not in E!, use EG.
                 * Ensembl species list: http://www.ensembl.org/info/about/species.html
                 */
                function getEnsemblOrEnsemblgenomesEndpoint(species) {
                    var ensemblSpecies = [
                        "ailuropoda_melanoleuca",
                        "anas_platyrhynchos",
                        "anolis_carolinensis",
                        "astyanax_mexicanus",
                        "bos_taurus",
                        "callithrix_jacchus",
                        "canis_lupus_familiaris",
                        "cavia_porcellus",
                        "ceratotherium_simum_simum",
                        "chlorocebus_sabaeus",
                        "choloepus_hoffmanni",
                        "chrysemys_picta_bellii",
                        "ciona_intestinalis",
                        "ciona_savignyi",
                        "cricetulus_griseus",
                        "danio_rerio",
                        "dasypus_novemcinctus",
                        "dipodomys_ordii",
                        "drosophila_melanogaster",
                        "echinops_telfairi",
                        "equus_caballus",
                        "erinaceus_europaeus",
                        "felis_catus",
                        "ficedula_albicollis",
                        "gadus_morhua",
                        "gallus_gallus",
                        "gasterosteus_aculeatus",
                        "gorilla_gorilla_gorilla",
                        "heterocephalus_glaber",
                        "homo_sapiens",
                        "ictidomys_tridecemlineatus",
                        "latimeria_chalumnae",
                        "lepisosteus_oculatus",
                        "loxodonta_africana",
                        "macaca_fascicularis",
                        "macaca_mulatta",
                        "macropus_eugenii",
                        "meleagris_gallopavo",
                        "melopsittacus_undulatus",
                        "microcebus_murinus",
                        "microtus_ochrogaster",
                        "monodelphis_domestica",
                        "mus_musculus",
                        "mustela_putorius_furo",
                        "myotis_lucifugus",
                        "nomascus_leucogenys",
                        "ochotona_princeps",
                        "oreochromis_niloticus",
                        "ornithorhynchus_anatinus",
                        "orycteropus_afer_afer",
                        "oryctolagus_cuniculus",
                        "oryzias_latipes",
                        "otolemur_garnettii",
                        "ovis_aries",
                        "pan_troglodytes",
                        "papio_anubis",
                        "papio_hamadryas",
                        "pelodiscus_sinensis",
                        "petromyzon_marinus",
                        "poecilia_formosa",
                        "pongo_abelii",
                        "procavia_capensis",
                        "pteropus_vampyrus",
                        "rattus_norvegicus",
                        "saimiri_boliviensis",
                        "sarcophilus_harrisii",
                        "sorex_araneus",
                        "sus_scrofa",
                        "sus_scrofa_map",
                        "taeniopygia_guttata",
                        "takifugu_rubripes",
                        "tarsius_syrichta",
                        "tetraodon_nigroviridis",
                        "tupaia_belangeri",
                        "tursiops_truncatus",
                        "vicugna_pacos",
                        "xenopus_tropicalis",
                        "xiphophorus_maculatus"
                    ];
                    // "saccharomyces_cerevisiae", "caenorhabditis_elegans"];
                    // "saccharomyces_cerevisiae", "caenorhabditis_elegans" could use either E! or EG

                    var encoded = $filter('urlencodeSpecies')(species); // urlencoded species name
                    return ensemblSpecies.indexOf(encoded) > -1 ? 'https://rest.ensembl.org' : 'http://rest.ensemblgenomes.org';
                }

                /**
                 * Maximize Genoverse container width.
                 */
                function setGenoverseWidth() {
                    var w = element.find('.container').width();
                    element.find('.wrap').width(w);
                    element.find('#genoverse').width(w);
                }


                // Helper functions
                // ----------------

                /**
                 * Returns an object from genomes Array by its species name or null, if not found.
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

                /**
                 * Takes a genome on input, looks into its division attribute and returns the corresponding Ensembl
                 * subdomain
                 *
                 * @param genome {Object} e.g.
                 * {
                 *     'species': 'Mus musculus', 'synonyms': ['mouse'], 'assembly': 'GRCm38', 'assembly_ucsc': 'mm10',
                 *     'taxid': 10090, 'division': 'Ensembl',
                 *     'example_location': {'chromosome': 1, 'start': 86351981, 'end': 86352127,}
                 * }
                 * @returns {String} domain name without protocol or slashes or trailing dots
                 */
                function getEnsebmlSubdomainByDivision(genome) {
                    var subdomain;

                    if (genome.division == 'Ensembl') {
                        subdomain = 'ensembl.org';
                    } else if (genome.division == 'Ensembl Plants') {
                        subdomain = 'plants.ensembl.org';
                    } else if (genome.division == 'Ensembl Metazoa') {
                        subdomain = 'metazoa.ensembl.org';
                    } else if (genome.division == 'Ensembl Bacteria') {
                        subdomain = 'bacteria.ensembl.org';
                    } else if (genome.division == 'Ensembl Fungi') {
                        subdomain = 'fungi.ensembl.org';
                    } else if (genome.division == 'Ensembl Protists') {
                        subdomain = 'protists.ensembl.org';
                    }

                    return subdomain;
                }
            }
        };
    }

})();
