(function() {

angular.module("Genoverse", []).directive("genoverse", genoverse);

    function genoverse() {
        return {
            restrict: 'E',
            scope: {
                genome: "=",
                chromosome: "=",
                start: "=",
                end: "=",
                strand: 1,
                species: "=",
                description: "=",
                speciesLabel: "="
            },
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
                    // (re-)create Genoverse object
                    $scope.browser = new Genoverse(get_genoverse_config_object());
                    add_karyotype_placeholder();
                    register_genoverse_events();

  /**
   * Configure Genoverse initialization object.
   */
    function get_genoverse_config_object() {
        var genoverseConfig = {
            container: this.genoverse_container,
            chr: this.params.chromosome,
            species: this.params.species,
            showUrlCoords: false, // do not show genomic coordinates in the url
            plugins: ['controlPanel', 'resizer', 'fileDrop'],
            tracks: [
                Genoverse.Track.Scalebar,
                Genoverse.Track.extend({
                    name: 'Sequence',
                    model: configure_genoverse_model('ensembl_sequence'),
                    view: Genoverse.Track.View.Sequence,
                    resizable: 'auto',
                    100000: false,
                }),
                Genoverse.Track.extend({
                    name: 'Genes',
                    info: 'Ensembl API genes',
                    labels: true,
                    model: configure_genoverse_model('ensembl_gene'),
                    view: Genoverse.Track.View.Gene.Ensembl,
                }),
                Genoverse.Track.extend({
                    name: 'Transcripts',
                    info: 'Ensembl API transcripts',
                    labels: true,
                    model: configure_genoverse_model('ensembl_transcript'),
                    view: Genoverse.Track.View.Transcript.Ensembl,
                }),
                Genoverse.Track.extend({
                    name: 'RNAcentral',
                    id: 'RNAcentral',
                    info: 'Unique RNAcentral Sequences',
                    labels: true,
                    model: configure_genoverse_model('rnacentral'),
                    view: Genoverse.Track.View.Transcript.Ensembl,
                })
            ]
        };

        genoverseConfig = configure_karyotype_display(genoverseConfig);

        return genoverseConfig;
    }





                /**
                 * Determine if karyotype information is available for this species.
                 */
                is_karyotype_available = function() {

                    return species_supported() && chromosome_size_available();

                    function species_supported() {
                        var species = ["homo_sapiens"]; // TODO: support more species
                        if (species.indexOf(scope.species) !== -1) {
                            return true;
                        } else {
                            return false;
                        }
                    }

                    /**
                     * Get a list of chromosomes from the karyotype object and determine
                     * whether the size of the displayed region is known.
                     * Some RNAs are defined on scaffolds or other non-chromosomal objects
                     * for which the size is not stored in the karyotype object.
                     */
                    function chromosome_size_available() {
                        var chromosomes = [];
                        for (var key in grch38) {
                            chromosomes.push(key);
                        }
                        if ( chromosomes.indexOf(scope.chromosome.toString()) !== -1) {
                            return true;
                        } else {
                            return false;
                        }
                    }

                  };


                /**
                 * Display Genoverse section header.
                 */
                function show_genoverse_section_header() {
                    $('.genoverse-wrap h2').show();
                }

                /**
                 * Display xref description in Genoverse section.
                 */
                function show_genoverse_section_info() {
                    // display xref coordinates
                    var text = '<em>' +
                        scope.species_label + ' ' +
                        scope.chromosome + ':' +
                        number_with_commas(scope.start) + '-' +
                        number_with_commas(scope.end) + ':' +
                        scope.strand +
                        '</em>';
                    $('#genoverse-coordinates').html('').hide().html(text).fadeIn('slow');
                    // display xref description
                    text = '<p>' + scope.description + '</p>';
                    $('#genoverse-description').html('').hide().html(text).fadeIn('slow');

                    /**
                     * Format the coordinates with commas as thousands separators.
                     * http://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
                     */
                    function number_with_commas(x) {
                        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                    }
                }
            }
        };
    }

})();