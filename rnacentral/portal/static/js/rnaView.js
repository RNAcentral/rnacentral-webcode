/*
Copyright [2009-2015] EMBL-European Bioinformatics Institute
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
 * Update URL query string using Angular $location service.
 */
function update_query_string(q) {
    var angular_scope = angular.element('body');
    var $location = angular_scope.injector().get('$location');
    var url = window.location.pathname + '?' + queryString.stringify(q);
    $location.url(url);
    angular_scope.scope().$apply();
}


var xrefLoader = function (upi, taxid) {
    this.upi = upi;
    this.taxid = taxid || 0;

    this.config = {
        dom: {
            xref_table_container: '#xrefs-table-div',
            xref_table: '#xrefs-table',
            xref_loading_container: '#xrefs-loading',
            xref_msg: '#xrefs-loading-msg',
            downloads: '#download-formats',
        },
        templates: {
            delay_msg: '#handlebars-loading-info-tmpl',
            loading_error_msg: '#handlebars-loading-error-tmpl',
        }
    };

    this.enable_genomic_features = false;
};

xrefLoader.prototype.load_xrefs = function(page) {

    var obj = this,
        initial_load = is_initial_load();
    page = page || 1;
    hide_xref_table();
    show_loading_indicator();
    set_xref_timer();
    get_xrefs();

    /**
     * If the annotations table is empty, then this is the first data load.
     */
    function is_initial_load() {
        return $(obj.config.dom.xref_table + ' tr').length === 0;
    }

    /**
     * Hide the xrefs table.
     */
    function hide_xref_table() {
        $(obj.config.dom.xref_table).hide();
    }

    /**
     * Show loading indicator.
     */
    function show_loading_indicator() {
        $(obj.config.dom.xref_loading_container).show();
    }

    function set_xref_timer() {
        // show an info message if xrefs are taking too long to load
        var target = $(obj.config.dom.xref_msg),
                     delay_template = $(obj.config.templates.delay_msg),
                     delay = 5000;

        var timer = setTimeout(function() {
            // do not update the message if there was an error
            if (target.html().indexOf("alert-danger") != -1) {
                return;
            }
            var msg = Handlebars.compile(delay_template.html());
            target.find(".alert-info").remove();
            target.append(msg).slideDown();
        }, delay);
    }

    function get_xrefs() {
        var url = '/rna/' + obj.upi + '/xrefs';
        if (obj.taxid) {
            url += '/' + obj.taxid;
        }
        url += '?page={PAGE}'.replace('{PAGE}', page);
        $.get(url, function(data){
            $(obj.config.dom.xref_table_container).html(data);
                obj.enable_genomic_features = data.indexOf('View genomic location') > 0;
            }).fail(function() {
                show_error();
            }).done(function(){
                display_xrefs();
            });
        }

        function show_error() {
            var error_template = $(obj.config.templates.loading_error_msg);
            var target = $(obj.config.dom.xref_msg);
            var msg = Handlebars.compile(error_template.html());
            target.hide().html(msg).fadeIn();
        }

        function display_xrefs(upi) {
            var oTable = {};

            launch_dataTables();
            show_dataTables();
            enable_sorting();
            xref_url_filering();
            append_download_links();

            function launch_dataTables() {

                delete_dataTables_controls();

                oTable = $(obj.config.dom.xref_table).dataTable({
                    "aoColumns": [null, null, null, {"bVisible": false}, {"bVisible": false}, {"bVisible": false}], // hide columns, but keep them sortable
                    "bAutoWidth": true, // pre-recalculate column widths
                    "sDom": "ftpil", // filter, table, pagination, information, length
                    "iDisplayLength": 5, // show 5 entries by default
                    "sPaginationType": "bootstrap", // requires dataTables.bootstrap.js
                    "bDeferRender": true, // defer rendering until necessary
                    "oLanguage": {
                        "sSearch": "", // don't display the "Search:" bit
                        "sInfo": "_START_-_END_ of _TOTAL_", // change the informational text
                        "oPaginate": {
                            "sNext": "",
                            "sPrevious": "",
                        },
                    },
                    "aaSorting": [[ 5, "desc" ]], // prioritize entries with genomic coordinates
                    "aLengthMenu": [[5, 10, 20, 50, -1], [5, 10, 20, 50, "All"]],
                    "fnInitComplete": function(oSettings, json) {
                        adjust_dataTables_controls();
                    },
                });

                /**
                 * Remove the old dataTables controls so that they are not duplicated.
                 */
                function delete_dataTables_controls() {
                    if (!initial_load) {
                        $('#overview .dataTables_paginate').remove();
                        $('#overview .dataTables_filter input').remove();
                        $('#xrefs-table_length').remove();
                        $('#xrefs-table_filter').remove();
                    }
                }

                function adjust_dataTables_controls() {
                    $('.dataTables_filter input').attr('placeholder', 'Filter table').
                                                  attr("tabindex", 2).
                                                  attr('type', 'search').
                                                  addClass('form-control input-sm');
                    $('#xrefs-table_filter').appendTo('#xrefs-datatables-filter').
                                             addClass('pull-right hidden-xs');
                    $('#xrefs-datatables-counter').html('');
                    $('#xrefs-table_info').appendTo('#xrefs-datatables-counter');
                    // hide pagination controls for tables with one page
                    if ( $('.dataTables_paginate').find('li').length == 3 ) { // 3 elements: <-, 1, ->
                        $('.dataTables_paginate').hide();
                        $('#xrefs-table_length').hide();
                    } else {
                        $('.dataTables_paginate').addClass('pull-left').
                                                  appendTo('.xref-datatables-controls');
                        $('#xrefs-table_length').addClass('pull-right text-muted small').
                                                 appendTo('.xref-datatables-controls');
                    }
                    $('.table th').css('padding-right','1.5em');
                }
            }

            function show_dataTables() {
                $(obj.config.dom.xref_loading_container).slideUp();
                $(obj.config.dom.xref_table).fadeIn();
            }

            function enable_sorting() {
                oTable.fnSortListener( document.getElementById('sort-by-first-seen'), 3);
                oTable.fnSortListener( document.getElementById('sort-by-last-seen'), 4);
            }

            /**
             * Filter xrefs using url parameter.
             */
            function xref_url_filering() {
                var dataTables_search = $('#xrefs-table_filter input'),
                    q = queryString.parse(location.search),
                    url_param = 'xref-filter';

                dataTables_search.on('input', function(e) {
                    q[url_param] = $(this).val();
                    update_query_string(q);
                    return false;
                });

                if (q[url_param]) {
                    dataTables_search.val(decodeURIComponent(q[url_param])).focus();
                    oTable.fnFilter(decodeURIComponent(q[url_param]));
                }
            }

            /**
             * Append download links for bed/gff/gff3 files if genomic coordinates are found.
             */
            function append_download_links() {
                var url = '/api/v1/rna/' + obj.upi;
                if ( obj.enable_genomic_features ) {
                    $(obj.config.dom.downloads).append('<li><a href="' + url + '.bed"  download="'  + obj.upi + '.bed">BED</a></li>')
                                               .append('<li><a href="' + url + '.gff"  download="'  + obj.upi + '.gff">GFF</a></li>')
                                               .append('<li><a href="' + url + '.gff3" download="'  + obj.upi + '.gff3">GFF3</a></li>');
                }
            }
    }
};


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
Handlebars.registerPartial('publication', $('#publication-partial').html());

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
        url = '/api/v1/rna/__URS__/publications?page_size=__PAGE_SIZE__';
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
    enable_show_publications_tab_action();
    toggle_tabs();
    enable_xref_pagination();
    activate_modified_nucleotides();

    /**
     * Update url parameter when tab is changed.
     */
    function toggle_tabs() {
        $('.tab-toggle').click(function() {
            var q = queryString.parse(location.search);
            q.tab = $(this).find('a').first().data('target').replace('#', '');
            update_query_string(q);
        });
    }

    function enable_xref_pagination() {
      $('.xref-pagination').click(function(){
        var pagination_link = $(this);
        pagination_link.parent().addClass('active').siblings().removeClass('active');
        rna_sequence_view.load_xrefs(pagination_link.data('xref-page'));

        q = queryString.parse(location.search);
        url_param = 'xref-page';

        q[url_param] = pagination_link.data(url_param);
        update_query_string(q);
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

    /**
     * Activate a Bootstrap tab given its id
     * and update the url parameter.
     */
    function activate_tab(tab_id) {
        $('#tabs a[data-target="#' + tab_id + '"]').tab('show');
        var q = queryString.parse(location.search);
        q.tab = tab_id;
        update_query_string(q);
        return false;
    }

    /**
     * Scroll to the top of the page.
     */
    function scroll_to_top() {
        jQuery('html,body').animate({scrollTop:0}, 400);
    }

    /**
     * Click on a link to view the Species tab.
     */
    function enable_show_species_tab_action() {
        $(".show-species-tab").click(function() {
            activate_tab('taxonomy');
        });
    }

    /**
     * Click on a link to view the Publications tab.
     */
    function enable_show_publications_tab_action() {
        $('body').on('click', '.show-publications-tab', function() {
            activate_tab('publications');
            scroll_to_top();
        });
    }

    /**
     * Modified nucleotides visualisation.
     */
    function activate_modified_nucleotides() {
        $('body').on('click', 'button[data-modifications]', function(){
            // destroy any existing popovers before reading in the sequence
            $('.modified-nt').popover('destroy');
            var $pre = $('#rna-sequence'),
                text = $pre.text(),
                modifications = $(this).data('modifications'),
                arrayLength = modifications.length,
                seq_new = '',
                start = 0,
                template = Handlebars.compile($("#handlebars-modified-nt-popover-tmpl").html());

            // loop over modifications and insert span tags with modified nucleotide data
            for (var i = 0; i < arrayLength; i++) {
              seq_new += text.slice(start, modifications[i].position - 1) +
                         template(modifications[i].chem_comp);
              start = modifications[i].position;
            }
            seq_new += text.slice(start, text.length);

            // update the sequence (use `html`, not `text`)
            $pre.html(seq_new);
            // bring sequence in the viewport
            scroll_to_pre();
            // show the entire sequence
            $pre.css({
              'overflow': 'auto',
              'max-height': 'initial',
            });
            // initialize popovers
            $('.modified-nt').popover({
              placement: 'top',
              html: true,
              viewport: '#rna-sequence',
            });
            // activate the first popover
            $('.modified-nt').first().focus().popover('show');

            /**
             * Scroll to the sequence.
             */
            function scroll_to_pre() {
              $('html, body').animate({
                  scrollTop: $('pre').offset().top - 100
              }, 1200);
            }
        });
    }
};
