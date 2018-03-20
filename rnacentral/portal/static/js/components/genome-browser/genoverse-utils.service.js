/**
 * This service contains utility function that are used in RNAcentral to pass data to angularjs-genoverse.
 *
 * Contains re-used functions. Those functions access data from surrounding controller's scope.
 * Thus, the intended use for this factory is as follows:
 *
 * sampleController.controller.js:
 * -------------------------------
 *
 * angular.module('sampleModule').controller('SampleController', function($scope, GenoverseUtils) {
 *     $scope.genoverseUtils = new GenoverseUtils($scope);
 * });
 *
 *
 *
 * sample.html:
 * ------------
 *
 * <genoverse genome="genome" chromosome="chromosome" start="start" end="end">
 *     <genoverse-track url="genoverseUtils.urls.sequence" name="'Sequence'" model="Genoverse.Track.Model.Sequence.Ensembl" view="Genoverse.Track.View.Sequence" controller="Genoverse.Track.Controller.Sequence" resizable="'auto'" auto-height="true" hide-empty="false" extra="{100000: false}"></genoverse-track>
 * </genoverse>
 */

angular.module("rnacentralApp").factory('GenoverseUtils', ['$filter', function($filter) {

    // Constructor
    // -----------

    function GenoverseUtils($scope) {
        var self = this;

        this.$scope = $scope;

        // Methods below need to be binded to 'this' object,
        // cause otherwise they get passed 'this' from event handler context.
        // We pass the $scope to these methods through 'this'.

        this.urls = {
            sequence: _.bind(function () {  // Sequence track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species);
                return '__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'
                    .replace('__ENDPOINT__', endpoint)
                    .replace('__SPECIES__', species);
            }, this),
            genes: _.bind(function () {  // Genes track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species);
                return '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'
                    .replace('__ENDPOINT__', endpoint)
                    .replace('__SPECIES__', species);
            }, this),
            transcripts: _.bind(function () {  // Transcripts track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species);
                return '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'
                    .replace('__ENDPOINT__', endpoint)
                    .replace('__SPECIES__', species);
            }, this),
            RNAcentral: _.bind(function () {  // custom RNAcentral track
                var origin = window.location.origin ? window.location.origin : window.location.protocol + "//" + window.location.host + '/';
                return origin + '/api/v1/overlap/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', this.$scope.browserLocation.genome);
            }, this)
        };


        this.genesPopulateMenu = _.bind(function(feature) {
            var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
            var location = '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

            var strand;
            if (feature.strand == 1) {
                strand = "forward >";
            }
            else if (feature.strand == -1) {
                strand = "< reverse";
            }

            var result = {
                title: '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Gene/Summary?g=' + feature.gene_id + '">' + feature.gene_id + '</a>',
                "Assembly name": feature.assembly_name,
                "Biotype": feature.biotype,
                "Description": feature.description,
                "Feature type": feature.feature_type,
                "Gene id": feature.gene_id,
                "Location": location,
                "Logic name": feature.logic_name,
                "Source": feature.source,
                "Strand": strand,
                "Version": feature.version
            };

            if (feature.havana_gene && feature.havana_version) {
                result["Havana gene"] = feature.havana_gene;
                result["Havana version"] = feature.havana_version;
            }

            if (feature.external_name) {
                result["HGNC symbol"] = feature.external_name;
            }

            return result;
        }, this);


        this.transcriptsPopulateMenu = _.bind(function(feature) {
            var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
            var location = '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

            var strand;
            if (feature.strand == 1) {
                strand = "forward >";
            }
            else if (feature.strand == -1) {
                strand = "< reverse";
            }

            var result = {
                title: '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Transcript/Summary?db=core&t=' + feature.transcript_id + '">' + feature.transcript_id + '</a>',
                "Assembly name": feature.assembly_name,
                "Biotype": feature.biotype,
                "Feature type": feature.feature_type,
                "Location": location,
                "Logic name": feature.logic_name,
                "Parent": '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Gene/Summary?g=' + feature.Parent + '">' + feature.Parent + '</a>',
                "Source": feature.source,
                "Strand": strand,
                "Transcript id": feature.transcript_id,
                "Version": feature.version
            };

            if (feature.havana_transcript && feature.havana_version) {
                result["Havana transcript"] = feature.havana_transcript;
                result["Havana version"] = feature.havana_version;
            }

            if (feature.external_name) {
                result["HGNC symbol"] = feature.external_name;
            }

            if (feature.transcript_support_level) {
                result["Transcript support level"] = '<a href="http://www.ensembl.org/Help/Glossary?id=492">' + feature.transcript_support_level + '</a>';
            }

            if (feature.tag) {
                result["Tag"] = feature.tag;
            }

            if (feature.version) { result["Version"] = feature.version; }

            return result;
        }, this);


        this.RNAcentralPopulateMenu = _.bind(function(feature) {
            var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
            var location = '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

            var strand;
            if (feature.strand == 1) {
                strand = "forward >";
            }
            else if (feature.strand == -1) {
                strand = "< reverse";
            }

            return {
                title: '<a target=_blank href="http://rnacentral.org/rna/' + feature.external_name + '/' + feature.taxid.toString() +'">'+ feature.label + '</a>',
                "RNAcentral id": '<a target=_blank href="http://rnacentral.org/rna/' + feature.external_name + '/' + feature.taxid.toString() +'">' + feature.external_name + '</a>',
                "Description": feature.description || "",
                "RNA type": feature.biotype,
                "Feature type": feature.feature_type,
                "Location": location,
                "Logic name": feature.logic_name,
                "Strand": strand
            };
        }, this);


        this.RNAcentralParseData = function(data) {
            var model = this;
            var featuresById = this.featuresById;
            var ids = [];

            data.filter(function (d) { return d.feature_type === 'transcript'; }).forEach(function (feature, i) {
                if (!featuresById[feature.id]) {
                    // prepare a label
                    var label = feature.description || feature.external_name;
                    if (label.length > 50) {
                        label = label.substr(0, 47) + "...";
                    }
                    if (feature.strand == 1) {
                        label = label + " >";
                    }
                    else if (feature.strand == -1) {
                        label = "< " + label;
                    }

                    feature.id = feature.ID;
                    feature.label = label; // used to be feature.external_name
                    feature.exons = {};
                    feature.subFeatures = [];
                    feature.cdsStart = Infinity;
                    feature.cdsEnd = -Infinity;
                    feature.chr = feature.seq_region_name;
                    feature.color = '#8B668B';

                    // Make currently selected feature red
                    if ((feature.start === self.$scope.selectedLocation.start) && (feature.end === self.$scope.selectedLocation.end) && (feature.chr === self.$scope.selectedLocation.chr)) {
                        feature.color = "#FF0000";
                        data.filter(function (datum) { return datum.feature_type === 'exon' && datum.Parent === feature.ID; }).forEach(function (exon) {
                            exon.borderColor = "#FF0000";
                        })
                    }

                    model.insertFeature(feature);

                    ids.push(feature.id);
                }
            });

            data.filter(function (d) { return d.feature_type === 'exon' && featuresById[d.Parent] && !featuresById[d.Parent].exons[d.id]; }).forEach(function (feature) {
                feature.id  = feature.ID;
                feature.chr = feature.seq_region_name;

                if (feature.end < featuresById[feature.Parent].cdsStart || feature.start > featuresById[feature.Parent].cdsEnd) {
                    feature.utr = true;
                } else if (feature.start < featuresById[feature.Parent].cdsStart) {
                    featuresById[feature.Parent].subFeatures.push($.extend({ utr: true }, feature, { end: featuresById[feature.Parent].cdsStart }));

                    feature.start = featuresById[feature.Parent].cdsStart;
                } else if (feature.end > featuresById[feature.Parent].cdsEnd) {
                    featuresById[feature.Parent].subFeatures.push($.extend({ utr: true }, feature, { start: featuresById[feature.Parent].cdsEnd }));

                    feature.end = featuresById[feature.Parent].cdsEnd;
                }

                featuresById[feature.Parent].subFeatures.push(feature);
                featuresById[feature.Parent].exons[feature.id] = feature;

                // set colors
                feature.color = false;
                if (!feature.borderColor) feature.borderColor = '#8B668B';  // this exon might've been colored already, if it's currently selected
            });

            ids.forEach(function (id) {
                featuresById[id].subFeatures.sort(function (a, b) { return a.start - b.start; });
            });
        };

    }


    // Methods
    // -------

    GenoverseUtils.prototype.Genoverse = Genoverse;

    GenoverseUtils.prototype.genomes = [
        // Ensembl
        {
            'ensemblSpecies': 'homo_sapiens',
            'species': 'Homo sapiens',
            'synonyms': ['human'],
            'assembly': 'GRCh38',
            'assembly_ucsc': 'hg38',
            'taxid': 9606,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 'X',
                'start': 73819307,
                'end': 73856333
            }
        },
        {
            'ensemblSpecies': 'mus_musculus',
            'species': 'Mus musculus',
            'synonyms': ['mouse'],
            'assembly': 'GRCm38',
            'assembly_ucsc': 'mm10',
            'taxid': 10090,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 1,
                'start': 86351908,
                'end': 86352200
            }
        },
        {
            'ensemblSpecies': 'danio_rerio',
            'species': 'Danio rerio',
            'synonyms': ['zebrafish'],
            'assembly': 'GRCz10',
            'assembly_ucsc': 'danRer10',
            'taxid': 7955,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 9,
                'start': 7633910,
                'end': 7634210
            }
        },
        {
            'ensemblSpecies': 'bos_taurus',
            'species': 'Bos taurus',
            'synonyms': ['cow'],
            'assembly': 'UMD3.1',
            'assembly_ucsc': 'bosTau6',
            'taxid': 9913,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 15,
                'start': 82197673,
                'end': 82197837
            }
        },
        {
            'ensemblSpecies': 'rattus_norvegicus',
            'species': 'Rattus norvegicus',
            'synonyms': ['rat'],
            'assembly': 'Rnor_6.0',
            'assembly_ucsc': 'rn6',
            'taxid': 10116,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 'X',
                'start': 118277628,
                'end': 118277850
            }
        },
        // {
        //     'ensemblSpecies': 'felis_catus',
        //     'species': 'Felis catus',
        //     'synonyms': ['cat'],
        //     'assembly': 'Felis_catus_6.2',
        //     'assembly_ucsc': 'felCat5',
        //     'taxid': 9685,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 'X',
        //         'start': 18058223,
        //         'end': 18058546
        //     }
        // },
        // {
        //     'ensemblSpecies': 'macaca_mulatta',
        //     'species': 'Macaca mulatta',
        //     'synonyms': ['macaque'],
        //     'assembly': 'MMUL_1',
        //     'assembly_ucsc': '', # no matching assembly
        //     'taxid': 9544,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 1,
        //         'start': 146238837,
        //         'end': 146238946
        //     }
        // },
        {
            'ensemblSpecies': 'pan_troglodytes',
            'species': 'Pan troglodytes',
            'synonyms': ['chimp'],
            'assembly': 'CHIMP2.1.4',
            'assembly_ucsc': 'panTro4',
            'taxid': 9598,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 11,
                'start': 78369004,
                'end': 78369219
            }
        },
        {
            'ensemblSpecies': 'canis_lupus_familiaris',
            'species': 'Canis familiaris',
            'synonyms': ['dog', 'Canis lupus familiaris'],
            'assembly': 'CanFam3.1',
            'assembly_ucsc': 'canFam3',
            'taxid': 9615,
            'division': 'Ensembl',
            'example_location': {
                'chromosome': 19,
                'start': 22006909,
                'end': 22007119
            }
        },
        // {
        //     'ensemblSpecies': 'gallus_gallus',
        //     'species': 'Gallus gallus',
        //     'synonyms': ['chicken'],
        //     'assembly': 'Galgal4',
        //     'assembly_ucsc': 'galGal4',
        //     'taxid': 9031,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 9,
        //         'start': 15676031,
        //         'end': 15676160
        //     }
        // },
        // {
        //     'ensemblSpecies': 'xenopus_tropicalis',
        //     'species': 'Xenopus tropicalis',
        //     'synonyms': ['frog'],
        //     'assembly': 'JGI_4.2',
        //     'assembly_ucsc': 'xenTro3',
        //     'taxid': 8364,
        //     'division': 'Ensembl',
        //     'example_location': {
        //         'chromosome': 'NC_006839',
        //         'start': 11649,
        //         'end': 11717
        //     }
        // },
        // Ensembl Fungi
        // {
        //     'ensemblSpecies': 'saccharomyces_cerevisiae',
        //     'species': 'Saccharomyces cerevisiae',
        //     'synonyms': ['budding yeast', 'Saccharomyces cerevisiae S288c'],
        //     'assembly': 'R64-1-1',
        //     'assembly_ucsc': '',
        //     'taxid': 559292,
        //     'division': 'Ensembl Fungi',
        //     'example_location': {
        //         'chromosome': 'XII',
        //         'start': 856709,
        //         'end': 856919
        //     }
        // },
        {
            'ensemblSpecies': 'schizosaccharomyces_pombe',
            'species': 'Schizosaccharomyces pombe',
            'synonyms': ['fission yeast'],
            'assembly': 'ASM294v2',
            'assembly_ucsc': '',
            'taxid': 4896,
            'division': 'Ensembl Fungi',
            'example_location': {
                'chromosome': 'I',
                'start': 540951,
                'end': 544327
            }
        },
        // Ensembl Metazoa
        {
            'ensemblSpecies': 'caenorhabditis_elegans',
            'species': 'Caenorhabditis elegans',
            'synonyms': ['worm'],
            'assembly': 'WBcel235',
            'assembly_ucsc': 'ce11',
            'taxid': 6239,
            'division': 'Ensembl Metazoa',
            'example_location': {
                'chromosome': 'III',
                'start': 11467363,
                'end': 11467705
            }
        },
        {
            'ensemblSpecies': 'drosophila_melanogaster',
            'species': 'Drosophila melanogaster',
            'synonyms': ['fly'],
            'assembly': 'BDGP6',
            'assembly_ucsc': 'dm6',
            'taxid': 7227,
            'division': 'Ensembl Metazoa',
            'example_location': {
                'chromosome': '3R',
                'start': 7474331,
                'end': 7475217
            }
        },
        {
            'ensemblSpecies': 'bombyx_mori',
            'species': 'Bombyx mori',
            'synonyms': ['silkworm'],
            'assembly': 'GCA_000151625.1',
            'assembly_ucsc': '',
            'taxid': 7091,
            'division': 'Ensembl Metazoa',
            'example_location': {
                'chromosome': 'scaf16',
                'start': 6180018,
                'end': 6180422
            }
        },
        // {
        //     'ensemblSpecies': 'anopheles_gambiae',
        //     'species': 'Anopheles gambiae',
        //     'synonyms': [],
        //     'assembly': 'AgamP4',
        //     'assembly_ucsc': '',
        //     'taxid': 7165,
        //     'division': 'Ensembl Metazoa',
        //     'example_location': {
        //         'chromosome': '2R',
        //         'start': 34644956,
        //         'end': 34645131
        //     }
        // },

        // Ensembl Protists
        {
            'ensemblSpecies': 'dictyostelium_discoideum',
            'species': 'Dictyostelium discoideum',
            'synonyms': [],
            'assembly': 'dictybase.01',
            'assembly_ucsc': '',
            'taxid': 44689,
            'division': 'Ensembl Protists',
            'example_location': {
                'chromosome': 2,
                'start': 7874546,
                'end': 7876498
            }
        },
        // {
        //     'ensemblSpecies': 'plasmodium_falciparum',
        //     'species': 'Plasmodium falciparum',
        //     'synonyms': [],
        //     'assembly': 'ASM276v1',
        //     'assembly_ucsc': '',
        //     'taxid': 5833,
        //     'division': 'Ensembl Protists',
        //     'example_location': {
        //         'chromosome': 13,
        //         'start': 2796339,
        //         'end': 2798488
        //     }
        // },

        // Ensembl Plants
        {
            'ensemblSpecies': 'arabidopsis_thaliana',
            'species': 'Arabidopsis thaliana',
            'synonyms': [],
            'assembly': 'TAIR10',
            'assembly_ucsc': '',
            'taxid': 3702,
            'division': 'Ensembl Plants',
            'example_location': {
                'chromosome': 2,
                'start': 18819643,
                'end': 18822629
            }
        }
    ];

    GenoverseUtils.prototype.genomeNames = [];
    for (var i = 0; i < GenoverseUtils.prototype.genomes.length; i++) {
        GenoverseUtils.prototype.genomeNames.push(GenoverseUtils.prototype.genomes[i].ensemblSpecies);
    }

    GenoverseUtils.prototype.exampleLocations = {};
    for (i = 0; i < GenoverseUtils.prototype.genomes.length; i++) {
        GenoverseUtils.prototype.exampleLocations[GenoverseUtils.prototype.genomes[i].ensemblSpecies] = {
            'chr': GenoverseUtils.prototype.genomes[i].example_location.chromosome,
            'start': GenoverseUtils.prototype.genomes[i].example_location.start,
            'end': GenoverseUtils.prototype.genomes[i].example_location.end
        }
    }

     /**
     * Dynamically determine whether to use E! or EG REST API based on species.
     * If species not in E!, use EG.
     * Ensembl species list: http://www.ensembl.org/info/about/species.html
     */
    GenoverseUtils.prototype.getEnsemblEndpoint = function(species) {
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
        return ensemblSpecies.indexOf(encoded) > -1 ? 'https://rest.ensembl.org' : 'https://rest.ensemblgenomes.org';
    };

    /**
    * @param genome {String} - e.g. 'homo_sapient'
    * @param genomes {Array} - contents of $scope.genomes
    * @returns {String} element of genomes array
    */
    GenoverseUtils.prototype.getGenomeObject = function(genome, genomes) {
        // get genome object from Genomes
        var genomeObject;
        for (var i = 0; i < GenoverseUtils.prototype.genomes.length; i++) {
            if (genome === GenoverseUtils.prototype.genomes[i].ensemblSpecies) {
                genomeObject = GenoverseUtils.prototype.genomes[i];
                return genomeObject;
            }
        }

        // if we're here, this is a failure
        console.log("Can't get genomeObject for genome: " + genome);
        return null;
    };

    /**
     * Takes a genome on input, looks into its division attribute and returns the corresponding Ensembl
     * subdomain
     *
     * @param genome {String}
     * @param genomes {Array} e.g.
     * [{
     *     'ensemblSpecies': 'mus_musculus', 'species': 'Mus musculus', 'synonyms': ['mouse'],
     *     'assembly': 'GRCm38', 'assembly_ucsc': 'mm10',
     *     'taxid': 10090, 'division': 'Ensembl',
     *     'example_location': {'chromosome': 1, 'start': 86351981, 'end': 86352127,}
     * }, ...]
     * @returns {String} domain name without protocol or slashes or trailing dots
     */
    GenoverseUtils.prototype.getEnsemblSubdomainByDivision = function(genome, genomes) {
        var subdomain;

        // get genome object from Genomes
        var genomeObject = GenoverseUtils.prototype.getGenomeObject(genome, genomes);
        if (!genomeObject) return null;

        if (genomeObject.division == 'Ensembl') {
            subdomain = 'ensembl.org';
        } else if (genomeObject.division == 'Ensembl Plants') {
            subdomain = 'plants.ensembl.org';
        } else if (genomeObject.division == 'Ensembl Metazoa') {
            subdomain = 'metazoa.ensembl.org';
        } else if (genomeObject.division == 'Ensembl Bacteria') {
            subdomain = 'bacteria.ensembl.org';
        } else if (genomeObject.division == 'Ensembl Fungi') {
            subdomain = 'fungi.ensembl.org';
        } else if (genomeObject.division == 'Ensembl Protists') {
            subdomain = 'protists.ensembl.org';
        }

        return subdomain;
    };

    return GenoverseUtils;
}]);
