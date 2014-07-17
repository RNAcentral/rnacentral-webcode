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
  };

  /**
   * Main function for launching Genoverse.
   */
  display_genomic_location = function() {

    show_genoverse_section_header();
    initialize_genoverse();
    navigate_to_feature();

    /**
     * Load Genoverse for the first time or switch to a different species.
     */
    function initialize_genoverse() {
      if (typeof window.browser === 'undefined' || switch_species()) {
          // (re-)create Genoverse object
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
            $('.gv_wrapper').prepend('<div class="genoverse_karyotype_placeholder"><p>Karyotype display not available for this species</p></div>');
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

  };

  /**
   * Configure Genoverse initialization object.
   */
  get_genoverse_config_object = function() {

    var genoverseConfig = {
      container     : '#genoverse',
      chr           : this.params.chromosome,
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
          name      : 'Ensembl genes',
          info      : 'Ensembl API genes',
          resizable : 'auto',
          labels : true,
          model  : configure_genoverse_model('ensembl_gene'),
          view   : Genoverse.Track.View.Gene.Ensembl,
        }),
        Genoverse.Track.extend({
          name      : 'Ensembl transcripts',
          info      : 'Ensembl API transcripts',
          resizable : 'auto',
          labels : true,
          model  : configure_genoverse_model('ensembl_transcript'),
          view   : Genoverse.Track.View.Transcript.Ensembl,
        }),
        Genoverse.Track.extend({
          name      : 'RNAcentral',
          id        : 'RNAcentral',
          info      : 'Unique RNAcentral Sequences',
          resizable : 'auto',
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
        genoverseConfig.genome = 'grch37'; // determine dynamically when more karyotypes are available
      } else {
        genoverseConfig.chromosomeSize = Math.pow(10, 20); // should be greater than any chromosome size
      }
      return genoverseConfig;
    }

    /**
     * Each Genoverse model is configured with an organism-specific url.
     * In addition, a new RNAcentral models that's mimicking Ensembl API is defined.
     */
    function configure_genoverse_model(model_type) {

      var model;

      if (model_type === 'ensembl_gene') {
        // Ensembl Gene track
        new_url = '//beta.rest.ensembl.org/feature/region/__SPECIES__/__CHR__:__START__-__END__?feature=gene;content-type=application/json'.replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Gene.Ensembl.extend({
          url: new_url,
        });
      } else if (model_type === 'ensembl_transcript') {
        // Ensembl Transcript track
        new_url = '//beta.rest.ensembl.org/feature/region/__SPECIES__/__CHR__:__START__-__END__?feature=transcript;feature=exon;feature=cds;content-type=application/json'.replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Transcript.Ensembl.extend({
          url: new_url,
        });
      } else if (model_type === 'ensembl_sequence') {
        // Ensembl sequence view
        new_url = '//beta.rest.ensembl.org/sequence/region/__SPECIES__/__CHR__:__START__-__END__?content-type=text/plain'.replace('__SPECIES__', this.params.species);
        model = Genoverse.Track.Model.Sequence.Ensembl.extend({
          url: new_url,
        });
      } else if (model_type === 'rnacentral') {
        // custom RNAcentral track
        if (!window.location.origin) {
          window.location.origin = window.location.protocol + "//" + window.location.host + '/';
        }
        new_url = window.location.origin + '/api/v1/feature/region/__SPECIES__/__CHR__:__START__-__END__'.replace('__SPECIES__', this.params.species);
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
    var karyotype_available = ["homo_sapiens"]; // TODO: support more species
    if (karyotype_available.indexOf(this.params.species) === -1) {
      return false;
    } else {
      return true;
    }
  };

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
          'endpoint': $this.data('endpoint'),
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
