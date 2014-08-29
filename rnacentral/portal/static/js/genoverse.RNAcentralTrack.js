/*
Copyright [2009-2014] EMBL-European Bioinformatics Institute
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

/**
 * Manage Genoverse embedded browser.
 */

;(function(){

  /**
   * Internal object for storing the browser state.
   */
  params = {
    'chromosome': '',
    'start': '',
    'end': '',
    'species': '',
    '_species': '', // previous species
    'species_label': '',
    'description': '',
  };

  genoverse_container = '#genoverse';

  /**
   * Main function for launching Genoverse.
   */
  display_genomic_location = function() {

    show_genoverse_section_header();
    show_genoverse_section_info();
    initialize_genoverse();
    scroll_to_genoverse();
    navigate_to_feature();

    /**
     * Load Genoverse for the first time or switch to a different species.
     */
    function initialize_genoverse() {
      if (typeof window.browser === 'undefined' || switch_species()) {
          // (re-)create Genoverse object
          delete window.browser;
          $(this.genoverse_container).html('');
          window.browser = new Genoverse(get_genoverse_config_object());
          add_karyotype_placeholder();
      }

      /**
       * Return true if the current and the previous browser states refer to
       * different species.
       */
      function switch_species() {
        return this.params._species !== this.params.species && this.params._species !== '';
      }

      /**
       * Karyotype is supported only for a limited number of species,
       * so a placeholder div is used to replace the karyotype div
       * to keep the display consistent.
       */
      function add_karyotype_placeholder() {
        if (!is_karyotype_available()) {
            $('.gv_wrapper').prepend('<div class="genoverse_karyotype_placeholder">' +
                                     '  <p>Karyotype display is not available</p>' +
                                     '</div>');
        }
      }
    }

    /**
     * Navigate to the region of interest.
     */
    function navigate_to_feature() {
      browser.moveTo(this.params.start, this.params.end, false);
      browser.zoomOut();
    }

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
                 this.params.species_label + ' ' +
                 this.params.chromosome + ':' +
                 number_with_commas(this.params.start) + '-' +
                 number_with_commas(this.params.end) +
                 '</em>';
      $('#genoverse-coordinates').html('').hide().html(text).fadeIn('slow');
      // display xref description
      text = '<p>' + this.params.description + '</p>';
      $('#genoverse-description').html('').hide().html(text).fadeIn('slow');

      /**
       * Format the coordinates with commas as thousands separators.
       * http://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
       */
      function number_with_commas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      }
    }

    /**
     * If Genoverse is not in viewport, scroll to it, otherwise don't do anything.
     */
    function scroll_to_genoverse() {
        if ( !isElementInViewport($(this.genoverse_container))) {
          $('html, body').animate({
              scrollTop: $("#genoverse").offset().top - 100
          }, 1200);
        }

      /**
       * Determine if element is in viewport.
       * Adapted from:
       * http://stackoverflow.com/questions/123999/how-to-tell-if-a-dom-element-is-visible-in-the-current-viewport
       */
      function isElementInViewport (el) {
          if (el instanceof jQuery) {
              el = el[0];
          }
          var rect = el.getBoundingClientRect();
          return (
              rect.top <= (window.innerHeight || document.documentElement.clientHeight)
          );
      }
    }
  };

  /**
   * Configure Genoverse initialization object.
   */
  get_genoverse_config_object = function() {

    var genoverseConfig = {
      container     : this.genoverse_container,
      chr           : this.params.chromosome,
      species       : this.params.species,
      showUrlCoords : false, // do not show genomic coordinates in the url
      plugins       : [ 'controlPanel', 'resizer', 'fileDrop' ],
      tracks        : [
        Genoverse.Track.Scalebar,
        Genoverse.Track.extend({
          name      : 'Sequence',
          model     : configure_genoverse_model('ensembl_sequence'),
          view      : Genoverse.Track.View.Sequence,
          resizable : 'auto',
          100000    : false,
        }),
        Genoverse.Track.extend({
          name      : 'Genes',
          info      : 'Ensembl API genes',
          labels : true,
          model  : configure_genoverse_model('ensembl_gene'),
          view   : Genoverse.Track.View.Gene.Ensembl,
        }),
        Genoverse.Track.extend({
          name      : 'Transcripts',
          info      : 'Ensembl API transcripts',
          labels : true,
          model  : configure_genoverse_model('ensembl_transcript'),
          view   : Genoverse.Track.View.Transcript.Ensembl,
        }),
        Genoverse.Track.extend({
          name      : 'RNAcentral',
          id        : 'RNAcentral',
          info      : 'Unique RNAcentral Sequences',
          labels : true,
          model  : configure_genoverse_model('rnacentral'),
          view   : Genoverse.Track.View.Transcript.Ensembl,
        })
      ]
    };

    genoverseConfig = configure_karyotype_display(genoverseConfig);

    return genoverseConfig;

    /**
     * Determine whether karyotype should be displayed.
     */
    function configure_karyotype_display(genoverseConfig) {
      if (is_karyotype_available()) {
        genoverseConfig.plugins.push('karyotype');
        genoverseConfig.genome = 'grch38'; // determine dynamically when more karyotypes are available
      } else {
        genoverseConfig.chromosomeSize = Math.pow(10, 20); // should be greater than any chromosome size
      }
      return genoverseConfig;
    }

    /**
     * Dynamically choose whether to use E! or EG REST API based on species.
     * If species not in E!, use EG.
     * Ensembl species list: http://www.ensembl.org/info/about/species.html
     */
    function get_ensembl_or_ensemblgenomes_endpoint() {
      var endpoint;
      var ensembl_species = ["ailuropoda_melanoleuca", "anas_platyrhynchos", "anolis_carolinensis", "astyanax_mexicanus",
                             "bos_taurus", "callithrix_jacchus", "canis_lupus_familiaris",
                             "cavia_porcellus", "ceratotherium_simum_simum", "chlorocebus_sabaeus", "choloepus_hoffmanni",
                             "chrysemys_picta_bellii", "ciona_intestinalis", "ciona_savignyi", "cricetulus_griseus", "danio_rerio",
                             "dasypus_novemcinctus", "dipodomys_ordii", "drosophila_melanogaster", "echinops_telfairi",
                             "equus_caballus", "erinaceus_europaeus", "felis_catus", "ficedula_albicollis", "gadus_morhua",
                             "gallus_gallus", "gasterosteus_aculeatus", "gorilla_gorilla_gorilla", "heterocephalus_glaber",
                             "homo_sapiens", "ictidomys_tridecemlineatus", "latimeria_chalumnae", "lepisosteus_oculatus",
                             "loxodonta_africana", "macaca_fascicularis", "macaca_mulatta", "macropus_eugenii", "meleagris_gallopavo",
                             "melopsittacus_undulatus", "microcebus_murinus", "microtus_ochrogaster", "monodelphis_domestica",
                             "mus_musculus", "mustela_putorius_furo", "myotis_lucifugus", "nomascus_leucogenys", "ochotona_princeps",
                             "oreochromis_niloticus", "ornithorhynchus_anatinus", "orycteropus_afer_afer", "oryctolagus_cuniculus",
                             "oryzias_latipes", "otolemur_garnettii", "ovis_aries", "pan_troglodytes", "papio_anubis",
                             "papio_hamadryas", "pelodiscus_sinensis", "petromyzon_marinus", "poecilia_formosa", "pongo_abelii",
                             "procavia_capensis", "pteropus_vampyrus", "rattus_norvegicus",
                             "saimiri_boliviensis", "sarcophilus_harrisii", "sorex_araneus", "sus_scrofa", "sus_scrofa_map",
                             "taeniopygia_guttata", "takifugu_rubripes", "tarsius_syrichta", "tetraodon_nigroviridis", "tupaia_belangeri",
                             "tursiops_truncatus", "vicugna_pacos", "xenopus_tropicalis", "xiphophorus_maculatus"];
                             // "saccharomyces_cerevisiae", "caenorhabditis_elegans"];
                              // "saccharomyces_cerevisiae", "caenorhabditis_elegans" could use either E! or EG
      if (ensembl_species.indexOf(this.params.species) > -1) {
        endpoint = 'rest.ensembl.org';
      } else {
        endpoint = 'rest.ensemblgenomes.org';
      }
      return endpoint;
    }

    /**
     * Each Genoverse model is configured with an organism-specific url.
     * In addition, a new RNAcentral models that's mimicking Ensembl API is defined.
     */
    function configure_genoverse_model(model_type) {

      var model;
      var endpoint = get_ensembl_or_ensemblgenomes_endpoint();

      if (model_type === 'ensembl_gene') {
        // Ensembl Gene track
        new_url = '//__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Gene.Ensembl.extend({
          url: new_url,
        });

      } else if (model_type === 'ensembl_transcript') {
        // Ensembl Transcript track
        new_url = '//__ENDPOINT__/overlap/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Transcript.Ensembl.extend({
          url: new_url,
        });

      } else if (model_type === 'ensembl_sequence') {
        // Ensembl sequence view
        new_url = '//__ENDPOINT__/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'.replace('__ENDPOINT__', endpoint).replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Sequence.Ensembl.extend({
          url: new_url,
        });

      } else if (model_type === 'rnacentral') {
        // custom RNAcentral track
        if (!window.location.origin) {
          window.location.origin = window.location.protocol + "//" + window.location.host + '/';
        }
        new_url = window.location.origin + '/api/v1/overlap/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Gene.Ensembl.extend({
          url: new_url,

          parseData: function (data) {
            for (var i = 0; i < data.length; i++) {
              var feature = data[i];

              if (feature.feature_type === 'transcript' && !this.featuresById[feature.ID]) {
                feature.id    = feature.ID;
                feature.label = feature.external_name;
                feature.exons = [];
                feature.cds   = [];

                this.insertFeature(feature);
              } else if (feature.feature_type === 'exon' && this.featuresById[feature.Parent]) {
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

  };

  /**
   * Maximize Genoverse container width.
   */
  set_genoverse_width = function() {
    var w = $('.container').width();
    $('.wrap').width(w);
    $('#genoverse').width(w);
  };

  /**
   * Determine if karyotype information is available for this species.
   */
  is_karyotype_available = function() {

    return species_supported() && chromosome_size_available();


    function species_supported() {
      var species = ["homo_sapiens"]; // TODO: support more species
      if (species.indexOf(this.params.species) !== -1) {
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
      for(var key in grch38) {
        chromosomes.push(key);
      }
      if ( chromosomes.indexOf(this.params.chromosome.toString()) !== -1) {
        return true;
      } else {
        return false;
      }
    }

  }

  /**
   * Attach all event handlers.
   */
  bind_events = function() {
    resize_genoverse_on_window_resize();
    genoverse_trigger();

    /**
     * Ensure Genoverse is resized when the browser window is resized.
     */
    function resize_genoverse_on_window_resize() {
      window.onresize = function() {
        set_genoverse_width();
      };
    }

    /**
     * Create an event for launching Genoverse.
     */
    function genoverse_trigger()  {
      $('body').on("click", '.genoverse-xref', function(e){
          e.preventDefault();
          set_params($(this));
          display_genomic_location();
      });

      /**
       * Store new parameters in the internal object.
       */
      function set_params($this) {

        var species = $this.data('species');
        if (species !== this.params.species) {
          _species = this.params.species;
        }

        this.params = {
          'chromosome': $this.data('chromosome'),
          'start': $this.data('genomic-start'),
          'end': $this.data('genomic-end'),
          'species': species,
          '_species': _species,
          'species_label': $this.data('species-label'),
          'endpoint': $this.data('endpoint'),
          'description': $this.data('description'),
        };
      }
    }

  };

  /**
   * Run module.
   */
  (function(){
    set_genoverse_width();
    bind_events();
  })();

})();
