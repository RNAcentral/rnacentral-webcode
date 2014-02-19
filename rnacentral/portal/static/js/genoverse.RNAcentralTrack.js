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
      name      : 'Ensembl Genes',
      info      : 'Ensembl API genes & transcripts, see <a href="http://beta.rest.ensembl.org/" target="_blank">beta.rest.ensembl.org</a> for more details',
      resizable : 'auto',

      // Different settings for different zoom level
      2000000: { // This one applies when > 2M base-pairs per screen
        labels : false
      },
      100000: { // more than 100K but less then 2M
        labels : true,
        model  : Genoverse.Track.Model.Gene.Ensembl,
        view   : Genoverse.Track.View.Gene.Ensembl
      },
      1: { // > 1 base-pair, but less then 100K
        labels : true,
        model  : Genoverse.Track.Model.Transcript.Ensembl,
        view   : Genoverse.Track.View.Transcript.Ensembl
      }
    })
  ]
};


$('body').on("click", '.genoverse-xref', function(e){

    e.preventDefault();
    var $this = $(this);

    // loading genoverse for the first time
    if (typeof window.browser === 'undefined') {
        // create Genoverse object
        genoverseConfig['chr'] = $this.data('chromosome');
        window.browser = new Genoverse(genoverseConfig);
        // load the RNAcentral track
        $.ajax({
            url : "https://dl.dropboxusercontent.com/s/7f2oypttqwzt263/vega_ucsc_sorted.bed",
            dataType: "text",
            success : function (data) {
              var track = Genoverse.Track.File['BED'].extend({
                id        : "RNAcentral",
                name      : "RNAcentral",
                info      : "Unique RNAcentral Sequences",
                resizable : 'auto',
                allData   : true,
                data      : data,
                view      : Genoverse.Track.View.Transcript.Ensembl,
                model     : Genoverse.Track.Model.File.BEDexons,
                getData   : function () {
                  return $.Deferred().done(function () {
                    this.receiveData(this.data, 1, this.browser.chromosomeSize);
                    browser.moveTo($this.data('genomic-start'), $this.data('genomic-end'), false);
                    browser.zoomOut();
                  }).resolveWith(this);
                }
              });
              browser.addTrack(track, browser.tracks.length - 1);
            }
        });
    } else {
        if ( browser.chr != $this.data('chromosome') ) {
          // update chromosome and chromosomeSize
          browser.chr = $this.data('chromosome');
          browser.chromosomeSize = browser.genome[browser.chr].size;
          // reload the data for the current chromosome
          browser.tracksById['RNAcentral'].model.receiveData(browser.tracksById['RNAcentral'].model.data, 1, browser.chromosomeSize);
        }
        // navigate to the region of interest
        browser.moveTo($this.data('genomic-start'), $this.data('genomic-end'), false);
        browser.zoomOut();
    }

});
