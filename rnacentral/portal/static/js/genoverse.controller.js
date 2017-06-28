/*
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

(function() {

angular.module('rnacentralApp').controller('GenoverseGenomeBrowser', ['$scope', '$location', '$filter', function ($scope, $location, $filter) {

    // Method definitions
    // ------------------

    /**
     * Dynamically determine whether to use E! or EG REST API based on species.
     * If species not in E!, use EG.
     * Ensembl species list: http://www.ensembl.org/info/about/species.html
     */
    function getEndpoint(species) {
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
    function getEnsemblSubdomainByDivision(genome) {
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


    // Variables
    // ---------

    $scope.genomes = genomes;
    // from JS standpoint, genome and genomes[i] == genome are different objects, but we want exactly the same, so:
    $scope.genome = genomes.filter(function(element) {
        return element.species.toLowerCase() == genome.species.toLowerCase();
    })[0];
    $scope.chromosome = chromosome;
    $scope.start = start;
    $scope.end = end;

    $scope.Genoverse = Genoverse;

    $scope.urls = {
        sequence: function () { // Sequence track configuration
            var species = $filter('urlencodeSpecies')($scope.genome.species);
            var endpoint = getEndpoint(species);
            return '__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'
                .replace('__ENDPOINT__', endpoint)
                .replace('__SPECIES__', species);
        },
        genes: function() { // Genes track configuration
            var species = $filter('urlencodeSpecies')($scope.genome.species);
            var endpoint = getEndpoint(species);
            return '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'
                .replace('__ENDPOINT__', endpoint)
                .replace('__SPECIES__', species);
        },
        transcripts: function() { // Transcripts track configuration
            var species = $filter('urlencodeSpecies')($scope.genome.species);
            var endpoint = getEndpoint(species);
            return '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'
                .replace('__ENDPOINT__', endpoint)
                .replace('__SPECIES__', species);
        },
        RNAcentral: function () {
            // custom RNAcentral track
            var origin = window.location.origin ? window.location.origin : window.location.protocol + "//" + window.location.host + '/';
            return origin + '/api/v1/overlap/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', $filter('urlencodeSpecies')($scope.genome.species));
        }
    };

    $scope.RNAcentralParseData = function(data) {
        for (var i = 0; i < data.length; i++) {
            var feature = data[i];

            if (feature.feature_type === 'transcript' && !this.featuresById[feature.ID]) {
                feature.id    = feature.ID;
                feature.label = feature.external_name;
                feature.exons = [];
                feature.cds   = [];
                feature.chr   = feature.seq_region_name;

                this.insertFeature(feature);
            }
            else if (feature.feature_type === 'exon' && this.featuresById[feature.Parent]) {
                feature.id  = feature.ID;
                feature.chr = feature.seq_region_name;

                if (!this.featuresById[feature.Parent].exons[feature.id]) {
                    this.featuresById[feature.Parent].exons.push(feature);
                    this.featuresById[feature.Parent].exons[feature.id] = feature;
                }
            }
        }
    };

    $scope.genesPopulateMenu = function(feature) {
        var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
        var location = '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

        var strand;
        if (feature.strand == 1) {
            strand = "forward >";
        }
        else if (feature.strand == -1) {
            strand = "< reverse";
        }

        var result = {
            title: '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Gene/Summary?g=' + feature.gene_id + '">' + feature.gene_id + '</a>',
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
    };

    $scope.transcriptsPopulateMenu = function(feature) {
        var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
        var location = '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

        var strand;
        if (feature.strand == 1) {
            strand = "forward >";
        }
        else if (feature.strand == -1) {
            strand = "< reverse";
        }

        var result = {
            title: '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Transcript/Summary?db=core&t=' + feature.transcript_id + '">' + feature.transcript_id + '</a>',
            "Assembly name": feature.assembly_name,
            "Biotype": feature.biotype,
            "Feature type": feature.feature_type,
            "Location": location,
            "Logic name": feature.logic_name,
            "Parent": '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Gene/Summary?g=' + feature.Parent + '">' + feature.Parent + '</a>',
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
    };

    $scope.RNAcentralPopulateMenu = function(feature) {
        var chrStartEnd = feature.seq_region_name + ':' + feature.start + '-' + feature.end; // string e.g. 'X:1-100000'
        var location = '<a href="http://' + $scope.domain + '/' + $filter('urlencodeSpecies')($scope.genome.species) + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';

        var strand;
        if (feature.strand == 1) {
            strand = "forward >";
        }
        else if (feature.strand == -1) {
            strand = "< reverse";
        }

        return {
            title: '<a target=_blank href="http://rnacentral.org/rna/' + feature.label + '/' + $scope.genome.taxid.toString() +'">'+ feature.label + '</a>',
            "Biotype": feature.biotype,
            "Feature type": feature.feature_type,
            "Description": feature.description || "",
            "Location": location,
            "Logic name": feature.logic_name,
            "Strand": strand
        };
    };

    $scope.$location = $location;

    // Event handlers
    // --------------

    // handle copy to clipboard button
    new Clipboard('#copy-genome-location', {
        "text": function () {
            return document.location.href;
        }
    });

    // initialize a tooltip on the share button
    $('#copy-genome-location').tipsy();

    // reflect any changes in genome in address bar
    $scope.$watch('genome', setUrl);
    $scope.$watch('chromosome', setUrl);
    $scope.$watch('start', setUrl);
    $scope.$watch('end', setUrl);

    $scope.$watch('genome', setDomain);

    /**
     * Sets the url in address bar to reflect the changes in browser location
     */
    function setUrl(newValue, oldValue) {
        // set the full url
        $location.search({
            species: $filter('urlencodeSpecies')($scope.genome.species),  // filter is from Genoverse module
            chromosome: $scope.chromosome,
            start: $scope.start,
            end: $scope.end
        });
        $location.replace();
    }

    /**
     * Change ensembl subdomain upon species change
     */
    function setDomain(newValue, oldValue) {
        $scope.domain = getEnsemblSubdomainByDivision(newValue);
    }
}]);

})();
