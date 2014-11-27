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

var rnaSequenceView = function(upi, taxid) {
	this.upi = upi;
  this.taxid = taxid || undefined;
};

rnaSequenceView.prototype.initialize = function() {

	obj = this;

	load_xrefs();
	activate_tooltips();
	activate_literature_references();
	activate_species_tree();
  activate_abstract_buttons($('.abstract-btn'));
	enable_show_species_tab_action();
  toggle_tabs();

  /**
   * Update url parameter when tab is changed.
   */
  function toggle_tabs() {
      $('.tab-toggle').click(function(){
          var q = queryString.parse(location.search);
          q.tab = $(this).find('a').first().data('target').replace('#', '');
          history.replaceState({}, "", window.location.pathname + '?' + queryString.stringify(q));
      });
  };

	function load_xrefs() {
      xref_loader = new xrefLoader(obj.upi, obj.taxid);
      xref_loader.load_xrefs();
	};

	function activate_tooltips() {
      $('body').tooltip({
          selector: '.help',
          delay: { show: 200, hide: 100 }
      });
	};

	function activate_literature_references() {
      $(document).on('click', '.literature-refs-retrieve', function(){
          var $this = $(this);
          var accession = $this.data('accession');
          var target = $this.siblings('.literature-refs-content');

          toggle_slider_icon = function() {
              var up = '<i class="fa fa-caret-up"></i>';
              var down = '<i class="fa fa-caret-down"></i>';
              if ($this.html() === up) {
                  $this.html(down);
              } else {
                  $this.html(up);
              }
          };

          insert_content = function(data) {
              var source = $("#handlebars-literature-reference-tmpl").html();
              var template = Handlebars.compile(source);
              var wrapper  = {refs: data};
              target.html(template(wrapper));
          };

          toggle_slider_icon();
          if ( target.html().length > 0 ) {
              target.slideToggle();
          } else {
            $.get('/api/v1/accession/' + accession + '/citations', function(data){
                insert_content(data);
                activate_abstract_buttons($this.siblings().find('.abstract-btn'));
                target.slideDown();
            });
          }
      });
	};

	function activate_species_tree() {
      var d3_species_tree = $('#d3-species-tree');
      if(!document.createElement('svg').getAttributeNS){
        d3_species_tree.html('Your browser does not support SVG');
      } else {
        $.ajax({
          url: "/rna/" + obj.upi + "/lineage",
          dataType: "json",
          success: function(data) {
            var tree = $('#d3-species-tree');
            tree.hide().html('');
            d3SpeciesTree(data, obj.upi, '#d3-species-tree');
            tree.fadeIn();
          },
          error: function() {
            var source = $("#handlebars-loading-error-tmpl").html();
            var msg = Handlebars.compile(source);
            d3_species_tree.hide().html(msg).fadeIn();
          }
        });
      }
    };

    function enable_show_species_tab_action() {
      // clicking the species link to view the Species tab
      $(".show-species-tab").click(function(){
        $('#tabs a[data-target="#taxonomy"]').tab('show');
        return false;
      });
    };

    function activate_abstract_buttons(target) {
        target.EuropePMCAbstracts({
          'target_class': '.abstract-text',
          'pubmed_id_data_attribute': 'pubmed-id',
          'msg': {
            'show_abstract': 'Show abstract',
            'hide_abstract': 'Hide abstract',
          }
        });
    };

};
