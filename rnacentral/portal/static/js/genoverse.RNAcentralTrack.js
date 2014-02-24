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

/*
Manage the Genoverse embedded browser.
*/

if (!window.location.origin)
     window.location.origin = window.location.protocol + "//" + window.location.host + '/';

// RNAcentral REST API
Genoverse.Track.Model.Gene.RNAcentral = Genoverse.Track.Model.Gene.Ensembl.extend({
  url: window.location.origin + '/api/v1/feature/region/human/__CHR__:__START__-__END__',
  dataRequestLimit : 5000000,
});

// RNAcentral REST API
Genoverse.Track.Model.Transcript.RNAcentral = Genoverse.Track.Model.Transcript.extend({
  url: window.location.origin + '/api/v1/feature/region/human/__CHR__:__START__-__END__',
  dataRequestLimit : 5000000,

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

// default Genoverse config object
var genoverseConfig = {
  container     : '#genoverse',
  genome        : 'grch37', // see js/genomes/
  chr           : '',
  showUrlCoords : false, // do not show genomic coordinates in the url
  plugins       : [ 'controlPanel', 'karyotype', 'trackControls', 'resizer', 'fileDrop' ],
  tracks        : [
    Genoverse.Track.Scalebar,
    Genoverse.Track.extend({
      name      : 'Sequence',
      model     : Genoverse.Track.Model.Sequence.Ensembl,
      view      : Genoverse.Track.View.Sequence,
      resizable : 'auto',
      100000    : false
    }),
    Genoverse.Track.extend({
      name      : 'Ensembl',
      info      : 'Ensembl API genes & transcripts, see <a href="http://beta.rest.ensembl.org/" target="_blank">beta.rest.ensembl.org</a> for more details',
      resizable : 'auto',
      labels : true,
      model  : Genoverse.Track.Model.Transcript.Ensembl,
      view   : Genoverse.Track.View.Transcript.Ensembl
    }),
    Genoverse.Track.extend({
      name      : 'RNAcentral',
      id        : 'RNAcentral',
      info      : 'Unique RNAcentral Sequences',
      resizable : 'auto',
      labels : true,
      model  : Genoverse.Track.Model.Transcript.RNAcentral,
      view   : Genoverse.Track.View.Transcript.Ensembl
    })
  ]
};

;(function(){

  // genomic coordinates to display
  params = {
    'chromosome': '',
    'start': '',
    'end': ''
  };

  // store the data- values in the internal object
  set_params = function($this) {
    this.params = {
      'chromosome': $this.data('chromosome'),
      'start': $this.data('genomic-start'),
      'end': $this.data('genomic-end'),
    }
  };

  show_genoverse_header = function() {
    $('.genoverse-wrap h2').show();
  };

  // main function
  genoverse_wrapper = function(params) {

    var track_id = 'RNAcentral';

    // loading genoverse for the first time
    if (typeof window.browser === 'undefined') {
        show_genoverse_header();
        // create Genoverse object
        genoverseConfig['chr'] = params['chromosome'];
        window.browser = new Genoverse(genoverseConfig);
        // set track position
        Genoverse.on('afterInit', function () {
          browser.moveTo(params['start'], params['end'], false);
          browser.zoomOut();
        });
    } else {
        if ( browser.chr != this.params['chromosome'] ) {
          // update chromosome and chromosomeSize
          browser.chr = params['chromosome'];
          browser.chromosomeSize = browser.genome[browser.chr].size;
          // reload the data for the current chromosome
          browser.tracksById[track_id].model.receiveData(browser.tracksById[track_id].model.data, 1, browser.chromosomeSize);
        }
        // navigate to the region of interest
        browser.moveTo(params['start'], params['end'], false);
        browser.zoomOut();
    }

  };

  set_genoverse_width = function() {
    $('#genoverse').width($('.container').width());
  };

  resize_genoverse_on_window_resize = function() {
    window.onresize = function() {
      set_genoverse_width();
    }
  };

  genoverse_trigger = function() {
    $('body').on("click", '.genoverse-xref', function(e){
        e.preventDefault();
        set_params($(this));
        genoverse_wrapper(params);
    });
  };

  bind_events = function() {
    resize_genoverse_on_window_resize();
    genoverse_trigger();
  };

  // run
  (function(){
    set_genoverse_width();
    bind_events();
  })();

})();
