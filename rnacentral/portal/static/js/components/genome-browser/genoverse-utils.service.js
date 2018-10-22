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

angular.module("genomeBrowser").factory('GenoverseUtils', ['$filter', function($filter) {

    // Constructor
    // -----------

    function GenoverseUtils($scope) {
        var self = this;

        this.$scope = $scope;

        this.exampleLocations = {};
        this.$scope.genomes.forEach(_.bind(function(genome) {
            this.exampleLocations[genome.ensembl_url] = {
                'chr': genome.example_chromosome,
                'start': genome.example_start,
                'end': genome.example_end
            }
        }, this));

        // Methods below need to be binded to 'this' object,
        // cause otherwise they get passed 'this' from event handler context.
        // We pass the $scope to these methods through 'this'.

        this.urls = {
            sequence: _.bind(function () {  // Sequence track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species, this.$scope.genomes);
                return '__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'
                    .replace('__ENDPOINT__', endpoint)
                    .replace('__SPECIES__', species);
            }, this),
            genes: _.bind(function () {  // Genes track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species, this.$scope.genomes);
                return '__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'
                    .replace('__ENDPOINT__', endpoint)
                    .replace('__SPECIES__', species);
            }, this),
            transcripts: _.bind(function () {  // Transcripts track configuration
                var species = this.$scope.browserLocation.genome;
                var endpoint = this.getEnsemblEndpoint(species, this.$scope.genomes);
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
                result["Symbol"] = feature.external_name;
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
                result["Symbol"] = feature.external_name;
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

            var location;
            if (feature.taxid == 6239) {
                location = '<a href="https://www.wormbase.org/tools/genome/jbrowse-simple/?data=data%2Fc_elegans_PRJNA13758&loc=' + feature.seq_region_name + ':' + feature.start + '..' + feature.end + '&tracks=Classical_alleles%2CPolymorphisms%2CCurated_Genes&highlight=">' + chrStartEnd + '</a>';
            } else {
                location = '<a href="http://' + this.$scope.browserLocation.domain + '/' + this.$scope.browserLocation.genome + '/Location/View?r=' + chrStartEnd + '" id="ensembl-link" target="_blank">' + chrStartEnd + '</a>';
            }

            var strand;
            if (feature.strand == 1) {
                strand = "forward >";
            }
            else if (feature.strand == -1) {
                strand = "< reverse";
            }

            return {
                title: '<a target=_blank href="https://rnacentral.org/rna/' + feature.external_name + '/' + feature.taxid.toString() +'">'+ feature.label + '</a>',
                "RNAcentral id": '<a target=_blank href="https://rnacentral.org/rna/' + feature.external_name + '/' + feature.taxid.toString() +'">' + feature.external_name + '</a>',
                "Description": feature.description || "",
                "RNA type": feature.biotype,
                "Feature type": feature.feature_type,
                "Location": location,
                "Logic name": feature.logic_name,
                "Strand": strand,
                "Databases": feature.databases.join(', ')
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
                    if (typeof self.$scope.selectedLocation !== 'undefined') {
                        if ((feature.start === self.$scope.selectedLocation.start) &&
                            (feature.end === self.$scope.selectedLocation.end) &&
                            (feature.chr === self.$scope.selectedLocation.chr) &&
                            (feature.external_name === self.$scope.upi)) {
                            feature.color = "#FF0000";
                            data.filter(function (datum) { return datum.feature_type === 'exon' && datum.Parent === feature.ID; }).forEach(function (exon) {
                                exon.borderColor = "#FF0000";
                            });
                        }
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

    GenoverseUtils.prototype.RNAcentralParseData = function(data) {
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
            feature.borderColor = '#8B668B';
        });

        ids.forEach(function (id) {
            featuresById[id].subFeatures.sort(function (a, b) { return a.start - b.start; });
        });
    };

     /**
     * Dynamically determine whether to use E! or EG REST API based on species.
     * If species not in E!, use EG.
     * Ensembl species list: http://www.ensembl.org/info/about/species.html
     */
    GenoverseUtils.prototype.getEnsemblEndpoint = function(species, genomes) {
        var genomeObject = GenoverseUtils.prototype.getGenomeObject(species, genomes);
        return genomeObject.division === 'Ensembl' ? 'https://rest.ensembl.org' : 'https://rest.ensemblgenomes.org';
    };

    /**
    * @param genome {String} - e.g. 'homo_sapient'
    * @param genomes {Array} - contents of $scope.genomes
    * @returns {String} element of genomes array
    */
    GenoverseUtils.prototype.getGenomeObject = function(genome, genomes) {
        // get genome object from Genomes
        var genomeObject;
        for (var i = 0; i < genomes.length; i++) {
            if (genome === genomes[i].ensembl_url) {
                genomeObject = genomes[i];
                return genomeObject;
            }
        }

        // if we're here, this is a failure
        console.log("Can't get genomeObject for genome: " + genome);
        return null;
    };

    return GenoverseUtils;
}]);
