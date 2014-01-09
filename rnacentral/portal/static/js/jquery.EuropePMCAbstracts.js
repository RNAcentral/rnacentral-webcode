/*
  jQuery plugin for dynamically retrieving abstracts from EuropePMC
  using Pubmed ids.

  Html markup:
  <div>
    <button class="abstract-btn" data-pubmed-id="19838050">Preview abstract</button>
    <div class="abstract-text"></div>
  </div>

  Initialization:
  $('.abstract-btn').EuropePMCAbstracts({
    'target_class': '.abstract-text',
    'pubmed_id_data_attribute': 'pubmed-id',
  });
 */

;(function($) {

    // http://stackoverflow.com/questions/37684/how-to-replace-plain-urls-with-links
    replace_url_with_html_links = function(text) {
        var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return text.replace(exp,"<a href='$1' target='_blank'>$1</a>");
    };

    show_message = function(element, msg) {
        element.html(msg).slideDown();
    };

    is_valid_result = function(data) {
        return data.resultList.result.length > 0;
    };

    get_abstract_text = function(data) {
        var abstractText = data.resultList.result[0].abstractText;
        abstractText = replace_url_with_html_links(abstractText);
        return abstractText;
    };

    set_button_label = function($button, $abstractText) {
        var button_label = $abstractText.is(':visible') ?
                           $.fn.EuropePMCAbstracts.options.msg.hide_abstract :
                           $.fn.EuropePMCAbstracts.options.msg.show_abstract;
        $button.html(button_label);
    };

    // main toggle function
    $.fn.toggleAbstract = function ( options ) {

      // setup
      var pubmed_id = this.data($.fn.EuropePMCAbstracts.options.pubmed_id_data_attribute);
      var $target = this.siblings($.fn.EuropePMCAbstracts.options.target_class);
      var $this = $(this);

      // do nothing if there is no pubmed id
      if (!pubmed_id) {
          show_message($target, msg.error);
          return this;
      }

      // abstract already loaded
      if ( $target.html().length > 0 ) {
          $target.slideToggle(function(){
              set_button_label($this, $target);
          });
          return this;
      }

      // loading the abstract for the first time
      $target.hide();
      var query = 'ext_id:' + pubmed_id + '&format=json&resulttype=core&callback=callback"';

      $.ajax({
        url: $.fn.EuropePMCAbstracts.options.europepmc_url + query,
        dataType: "jsonp",
        jsonp: false, // prevent jQuery from modifying the callback bit in the url
        jsonpCallback: "callback", // tell what callback function to use
      }).done(function(data){
        if ( is_valid_result(data) ) {
            show_message($target, get_abstract_text(data));
            set_button_label($this, $target);
        } else {
            show_message($target, msg.error);
        }
      }).fail(function(){
          show_message($target, msg.error);
      });

      return this; // for chaining

    };

    // plugin initialization
    $.fn.EuropePMCAbstracts = function(options){
        $.fn.EuropePMCAbstracts.options = $.extend( {}, $.fn.EuropePMCAbstracts.options, options );
        return this.each(function(){
            $(this).on('click', function(){
              $(this).toggleAbstract();
            });
        });
    };

    // default options
    $.fn.EuropePMCAbstracts.options = {
          pubmed_id_data_attribute: 'pubmed-id', // data attribute
          target_class: '.abstract-text', // where to insert the abstract
          msg: {
              error: "Sorry, the abstract could not be retrieved",
              show_abstract: "Show abstract",
              hide_abstract: "Hide abstract",
          },
          europepmc_url: "http://www.ebi.ac.uk/europepmc/webservices/rest/search/query=",
    };

})(jQuery);
