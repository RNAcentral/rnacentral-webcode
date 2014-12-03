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

/**
 * Register Handlebars helper for conditional operators with comparisons.
 */
Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
    switch (operator) {
        case '==':
            return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===':
            return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '<':
            return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=':
            return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>':
            return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=':
            return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&':
            return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
        default:
            return options.inverse(this);
    }
});

// same template is used for visualizing publications
Handlebars.registerPartial('publication', $('#publication-partial').html())

/**
 * Activate EuropePMC abstract retrieval.
 */
rnaSequenceView.prototype.activate_abstract_buttons = function(target) {
    target.EuropePMCAbstracts({
        'target_class': '.abstract-text',
        'pubmed_id_data_attribute': 'pubmed-id',
        'msg': {
            'show_abstract': 'Show abstract',
            'hide_abstract': 'Hide abstract',
        }
    });
};

/**
 * Retrieve publications associated with an RNAcentral id and display
 * them using a Handlebars template.
 */
rnaSequenceView.prototype.load_publications = function(page_size) {
    var obj = this,
        target = $('#publications'),
        load_more_btn_id = '#load-more-publications',
        template_id = '#handlebars-publications',
        url = '/api/v1/rna/__URS__/publications?page_size=__PAGE_SIZE__',
        page_size = page_size || 25;

    $.get(url.replace('__URS__', obj.upi).replace('__PAGE_SIZE__', page_size), function(data) {
        insert_content(data);
        obj.activate_abstract_buttons(target.find('.abstract-btn'));
    });

    // attach event to the load more button
    target.off('click').on('click', load_more_btn_id, function(){
        new_page_size = target.find('li').length + page_size;
        obj.load_publications(new_page_size);
    });

    function insert_content(data) {
        var source = $(template_id).html();
        var template = Handlebars.compile(source);
        data.total = data.count;
        data.count = data.results.length;
        var wrapper = {
            data: data,
        };
        target.html(template(wrapper));
    }
};

rnaSequenceView.prototype.load_xrefs = function(page) {
  xref_loader = new xrefLoader(this.upi, this.taxid);
  xref_loader.load_xrefs(page || 1);
};

rnaSequenceView.prototype.initialize = function() {

    var obj = this;
    obj.load_publications();
    activate_tooltips();
    activate_literature_references();
    activate_species_tree();
    obj.activate_abstract_buttons($('.abstract-btn'));
    enable_show_species_tab_action();
    toggle_tabs();
    enable_xref_pagination();

    /**
     * Update url parameter when tab is changed.
     */
    function toggle_tabs() {
        $('.tab-toggle').click(function() {
            var q = queryString.parse(location.search);
            q.tab = $(this).find('a').first().data('target').replace('#', '');
            history.replaceState({}, "", window.location.pathname + '?' + queryString.stringify(q));
        });
    }

    function enable_xref_pagination() {
      $('.xref-pagination').click(function(){
          var pagination_link = $(this);
          pagination_link.parent().addClass('active').siblings().removeClass('active');
          rna_sequence_view.load_xrefs(pagination_link.data('xref-page'));

        q = queryString.parse(location.search),
        url_param = 'xref-page';

        q[url_param] = pagination_link.data(url_param);
        history.replaceState({}, "", window.location.pathname + '?' + queryString.stringify(q));
      });
    }

    function activate_tooltips() {
        $('body').tooltip({
            selector: '.help',
            delay: {
                show: 200,
                hide: 100,
            }
        });
    }

    function activate_literature_references() {
        $(document).on('click', '.literature-refs-retrieve', function() {
            var $this = $(this);
            var accession = $this.data('accession');
            var target = $this.siblings('.literature-refs-content');

            toggle_slider_icon();
            if (target.html().length > 0) {
                target.slideToggle();
            } else {
                $.get('/api/v1/accession/' + accession + '/citations', function(data) {
                    insert_content(data);
                    obj.activate_abstract_buttons($this.siblings().find('.abstract-btn'));
                    target.slideDown();
                });
            }

            function toggle_slider_icon() {
                var up = '<i class="fa fa-caret-up"></i>';
                var down = '<i class="fa fa-caret-down"></i>';
                if ($this.html() === up) {
                    $this.html(down);
                } else {
                    $this.html(up);
                }
            }

            function insert_content(data) {
                var source = $("#handlebars-literature-reference-tmpl").html();
                var template = Handlebars.compile(source);
                var wrapper = {
                    refs: data
                };
                target.html(template(wrapper));
            }
        });
    }

    function activate_species_tree() {
        var d3_species_tree = $('#d3-species-tree');
        if (!document.createElement('svg').getAttributeNS) {
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
    }

    function enable_show_species_tab_action() {
        // clicking the species link to view the Species tab
        $(".show-species-tab").click(function() {
            $('#tabs a[data-target="#taxonomy"]').tab('show');
            var q = queryString.parse(location.search);
            q.tab = 'taxonomy';
            history.replaceState({}, "", window.location.pathname + '?' + queryString.stringify(q));
            return false;
        });
    }
};
