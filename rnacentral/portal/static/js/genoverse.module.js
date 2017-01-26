(function() {

angular.module("Genoverse", []).directive("genoverse", genoverse);

    function genoverse() {
        return {
            restrict: 'E',
            scope: false,
            template:
                "<div class='wrap genoverse-wrap' style='overflow-x:auto;'>" +
                "    <p class='text-muted'>" +
                "        <span id='genomic-location' class='margin-right-5px'></span>" +
                "        View in <a href='' id='ensembl-link' target='_blank'>Ensembl</a>" +
                "        <span class='ucsc-link'>|" +
                "            <a href='' target='_blank'>UCSC</a>" +
                "        </span>" +
                "    </p>" +
                "<div id='genoverse'></div>" +
                "</div>",
            link: function(scope, element, attrs) {
                showGenoverseSectionHeader();
                showGenoverseSectionInfo();
                // (re-)create Genoverse object
                scope.browser = new Genoverse(getGenoverseConfigObject());
                addKaryotypePlaceholder();
                registerGenoverseEvents();

                /**
                 * Display Genoverse section header.
                 */
                function showGenoverseSectionHeader() {
                    element.find('.genoverse-wrap h2').show();
                }

                /**
                 * Display xref description in Genoverse section.
                 */
                function showGenoverseSectionInfo() {
                    // display xref coordinates
                    var text = '<em>' +
                        scope.genome.species + ' ' +
                        scope.chromosome + ':' +
                        numberWithCommas(scope.start) + '-' +
                        numberWithCommas(scope.end) + ':' +
                        scope.strand +
                        '</em>';
                    element.find('#genoverse-coordinates').html('').hide().html(text).fadeIn('slow');
                    // display xref description
                    text = '<p>' + scope.description + '</p>';
                    element.find('#genoverse-description').html('').hide().html(text).fadeIn('slow');
                }

                /**
                 * Configure Genoverse initialization object.
                 */
                function getGenoverseConfigObject() {
                    var genoverseConfig = {
                        container: element.find('#genoverse'),
                        chr: scope.chromosome,
                        species: scope.genome.species,
                        showUrlCoords: false, // do not show genomic coordinates in the url
                        plugins: ['controlPanel', 'resizer', 'fileDrop'],
                        tracks: [
                            Genoverse.Track.Scalebar,
                            Genoverse.Track.extend({
                                name: 'Sequence',
                                model: configureGenoverseModel('ensemblSequence'),
                                view: Genoverse.Track.View.Sequence,
                                resizable: 'auto',
                                100000: false,
                            }),
                            Genoverse.Track.extend({
                                name: 'Genes',
                                info: 'Ensembl API genes',
                                labels: true,
                                model: configureGenoverseModel('ensemblGene'),
                                view: Genoverse.Track.View.Gene.Ensembl,
                            }),
                            Genoverse.Track.extend({
                                name: 'Transcripts',
                                info: 'Ensembl API transcripts',
                                labels: true,
                                model: configureGenoverseModel('ensemblTranscript'),
                                view: Genoverse.Track.View.Transcript.Ensembl,
                            }),
                            Genoverse.Track.extend({
                                name: 'RNAcentral',
                                id: 'RNAcentral',
                                info: 'Unique RNAcentral Sequences',
                                labels: true,
                                model: configureGenoverseModel('rnacentral'),
                                view: Genoverse.Track.View.Transcript.Ensembl,
                            })
                        ]
                    };

                    genoverseConfig = configureKaryotypeDisplay(genoverseConfig);

                    return genoverseConfig;
                }

                /**
                 * Each Genoverse model is configured with an organism-specific url.
                 * In addition, a new RNAcentral models that's mimicking Ensembl API is defined.
                 */
                function configureGenoverseModel(modelType) {
                    var model, url;
                    var endpoint = getEnsemblOrEnsemblgenomesEndpoint(urlencodeSpecies(scope.genome.species));

                    if (modelType === 'ensemblGene') {
                        // Ensembl Gene track
                        url = '//__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', urlencodeSpecies(scope.genome.species));
                        model = Genoverse.Track.Model.Gene.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'ensemblTranscript') {
                        // Ensembl Transcript track
                        url = '//__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', urlencodeSpecies(scope.genome.species));
                        model = Genoverse.Track.Model.Transcript.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'ensemblSequence') {
                        // Ensembl sequence view
                        url = '//__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', urlencodeSpecies(scope.genome.species));
                        model = Genoverse.Track.Model.Sequence.Ensembl.extend({ url: url });
                    }
                    else if (modelType === 'rnacentral') {
                        // custom RNAcentral track
                        if (!window.location.origin) { window.location.origin = window.location.protocol + "//" + window.location.host + '/'; }

                        url = window.location.origin + '/api/v1/overlap/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', urlencodeSpecies(scope.genome.species));
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

                    return ensemblSpecies.indexOf(species) > -1 ? 'rest.ensembl.org' : 'rest.ensemblgenomes.org';
                }

                /**
                 * Determine whether karyotype should be displayed.
                 */
                function configureKaryotypeDisplay(genoverseConfig) {
                    if (is_karyotype_available(scope.genome.species)) {
                        genoverseConfig.plugins.push('karyotype');
                        genoverseConfig.genome = 'grch38'; // determine dynamically when more karyotypes are available
                    } else {
                        genoverseConfig.chromosomeSize = Math.pow(10, 20); // should be greater than any chromosome size
                    }
                    return genoverseConfig;
                }

                /**
                 * Karyotype is supported only for a limited number of species,
                 * so a placeholder div is used to replace the karyotype div
                 * to keep the display consistent.
                 */
                function addKaryotypePlaceholder() {
                    if (!isKaryotypeAvailable(urlencodeSpecies(scope.genome.species))) {
                        $(".gv_wrapper").prepend(
                            "<div class='genoverse_karyotype_placeholder'>" +
                            "  <p>Karyotype display is not available</p>" +
                            "</div>"
                        );
                    }
                }

                /**
                 * Determine if karyotype information is available for this species.
                 */
                function isKaryotypeAvailable(species) {
                    return speciesSupported(species) && chromosomeSizeAvailable();
                }

                function speciesSupported(species) {
                    console.log("species = ", species);
                    var supportedSpecies = ["homo_sapiens"]; // TODO: support more species
                    return supportedSpecies.indexOf(species) !== -1;
                }

                /**
                 * Get a list of chromosomes from the karyotype object and determine
                 * whether the size of the displayed region is known.
                 * Some RNAs are defined on scaffolds or other non-chromosomal objects
                 * for which the size is not stored in the karyotype object.
                 */
                function chromosomeSizeAvailable() {
                    var chromosomes = [];
                    for (var key in grch38) { // TODO: WHERE IS THIS grch38 VARIABLE DEFINED? IS IT GLOBAL?
                        chromosomes.push(key);
                    }
                    return chromosomes.indexOf(scope.chromosome.toString())
                }

                /**
                 * Register custom Genoverse events.
                 */
                function registerGenoverseEvents() {
                    // resize tracks after load
                    scope.browser.on({
                        afterSetRange: function () {
                            setTimeout(function() {
                                element.find('.genoverse-wrap .resizer').click();
                            }, 1000);
                        }
                    });
                }

                /**
                 * Format the coordinates with commas as thousands separators.
                 * http://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
                 */
                function numberWithCommas(x) {
                    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                }

                /**
                 * Replaces whitespaces with underscores in scientific names of species.
                 * @param species (string} - scientific name of a speices with whitespaces, e.g. Homo Sapiens
                 * @returns {string} - scientific name of species with whitespaces replaces with underscores
                 */
                function urlencodeSpecies(species) {
                    // Canis familiaris is a special case
                    if (species == 'Canis familiaris') { species = 'Canis lupus familiaris'; }
                    return species.replace(/ /g, '_').toLowerCase();
                }
            }
        };
    }

})();