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

var xrefLoader = function(upi) {
	this.upi = upi;

	this.config = {
		dom: {
			xref_table_container: '#xrefs-table-div',
			xref_table: '#xrefs-table',
			xref_loading_container: '#xrefs-loading',
			xref_msg: '#xrefs-loading-msg',
			hopscotch_tour: '.tour',
			downloads: '#download-formats'
		},
		templates: {
			delay_msg: '#handlebars-loading-info-tmpl',
			loading_error_msg: '#handlebars-loading-error-tmpl',
		}
	};
};

xrefLoader.prototype.load_xrefs = function() {

	obj = this;
	set_xref_timer();
	get_xrefs();

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
			target.append(msg).slideDown();
		}, delay);
	};

	function get_xrefs() {
		var url = '/rna/' + obj.upi + '/xrefs';
    	$.get(url, function(data){
        	$(obj.config.dom.xref_table_container).html(data);
      	}).fail(function() {
      		show_error();
      	}).done(function(){
      		display_xrefs();
      	});
    };

	function show_error() {
		var error_template = $(obj.config.templates.loading_error_msg);
		var target = $(obj.config.dom.xref_msg);
		var msg = Handlebars.compile(error_template.html());
		target.hide().html(msg).fadeIn();
	};

	function display_xrefs(upi) {
		var oTable = {};

		launch_dataTables();
		show_dataTables();
  		enable_sorting();
  		enable_url_filering();
  		append_download_links();
  		enable_hopscotch_genomic_tour();

		function launch_dataTables() {
			oTable = $(obj.config.dom.xref_table).dataTable(
				{
					"aoColumns": [null, null, null, {"bVisible": false}, {"bVisible": false}], // hide columns, but keep them sortable
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
				"aLengthMenu": [[5, 10, 20, 50, -1], [5, 10, 20, 50, "All"]],
				"fnInitComplete": function(oSettings, json) {
					adjust_dataTables_controls();
				},
			});

			function adjust_dataTables_controls() {
				$('.dataTables_filter input').attr('placeholder', 'Filter table').
				                              attr("tabindex", 1).
				                              attr('type', 'search').
				                              addClass('form-control input-sm');
				$('#xrefs-table_filter').appendTo('#xrefs-datatables-filter').
				                         addClass('pull-right hidden-xs');
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
			};
		};

		function show_dataTables() {
			$(obj.config.dom.xref_loading_container).slideUp();
			$(obj.config.dom.xref_table).fadeIn();
		}

		function enable_sorting() {
			oTable.fnSortListener( document.getElementById('sort-by-first-seen'), 3);
			oTable.fnSortListener( document.getElementById('sort-by-last-seen'), 4);
		};

		function enable_url_filering() {
			// monitor the xref datatables search field to update the hashtag
			var dataTables_search = $('#xrefs-table_filter input');
			dataTables_search.on('input', function(e) {
				window.location.hash = $(this).val();
				return false;
			});
			// if the url hash does not refer to any of the tabs, update the search field
			var hash = window.location.hash.substring(1);
			if (hash != 'species' && hash != 'overview') {
				dataTables_search.val(decodeURIComponent(hash)).focus();
				oTable.fnFilter(decodeURIComponent(hash));
			}
		};

		function _genomic_results_present() {
			return $('.genoverse-xref').length > 0;
		};

		function append_download_links() {
          	// append download links if genomic coordinates are found
          	var url = '/api/v1/rna/' + obj.upi;
         	if ( _genomic_results_present() ) {
		        $(obj.config.dom.downloads).append('<li><a href="' + url + '.bed"  download='  + obj.upi + '.bed>bed</a></li>')
		                                   .append('<li><a href="' + url + '.gff"  download='  + obj.upi + '.gff>gff</a></li>')
		                                   .append('<li><a href="' + url + '.gff3" download='  + obj.upi + '.gff3>gff3</a></li>');
        	}
		};

		function enable_hopscotch_genomic_tour() {
			if ( _genomic_results_present() ) {
	            // create the tour button
	            $('h1').first().append('<small><button type="button" class="btn btn-info pull-right tour help animated pulse" title="Take an interactive tour to see genome integration features in action">Tour genome-related features</button></small>');

	            // Define hopscotch genome location tour
	            var tour = {
	              id: "tour-hopscotch",
	              showPrevButton: true,
	              onStart: function(){
                    $('#tabs a[href="#overview"]').tab('show');
	              },
	              steps: [
	                {
	                  title: "Genome integration",
	                  content: "Some annotations are linked to the <strong>human genome</strong> and have additional functionality.",
	                  target: "xrefs-table-div",
	                  placement: "top"
	                },
	                {
	                  title: "Links to genome browsers",
	                  content: "View this genomic location in <strong>Ensembl</strong> or <strong>UCSC</strong> with the pre-loaded RNAcentral track.",
	                  target: document.querySelector(".ensembl-link"),
	                  placement: "top"
	                },
	                {
	                  title: "Embedded genome browser",
	                  content: "This genomic location can also be visualised right on this page.",
	                  target: document.querySelector(".genoverse-xref"),
	                  placement: "top",
	                  onNext: function(){
	                    $(".genoverse-xref").first().click(); // launch genoverse
	                  }
	                },
	                {
	                  title: "Using the embedded browser",
	                  content: "You can <strong>scroll</strong> the browser or click on the entries to view the <strong>popup menus</strong> with links to Ensembl and other RNAcentral entries.",
	                  target: 'genoverse',
	                  placement: "top",
	                }
	              ]
	            };

	            // initialize the tour
	            $(obj.config.dom.hopscotch_tour).click(function(){
	              var firstStep = 0; // always start at the first step
	              hopscotch.startTour(tour, firstStep);
	            });
			};
		};

	};
};
