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

var xrefLoader = function(upi, taxid) {
	this.upi = upi;
	this.taxid = taxid || 0;

	this.config = {
		dom: {
			xref_table_container: '#xrefs-table-div',
			xref_table: '#xrefs-table',
			xref_loading_container: '#xrefs-loading',
			xref_msg: '#xrefs-loading-msg',
			downloads: '#download-formats'
		},
		templates: {
			delay_msg: '#handlebars-loading-info-tmpl',
			loading_error_msg: '#handlebars-loading-error-tmpl',
		}
	};

	this.enable_genomic_features = false;
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
		if (obj.taxid) {
			url += '/' + obj.taxid;
		}
    	$.get(url, function(data){
        	$(obj.config.dom.xref_table_container).html(data);
			obj.enable_genomic_features = data.indexOf('View genomic location') > 0;
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

		function launch_dataTables() {
			oTable = $(obj.config.dom.xref_table).dataTable(
				{
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

			function adjust_dataTables_controls() {
				$('.dataTables_filter input').attr('placeholder', 'Filter table').
				                              attr("tabindex", 2).
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
			if (hash != 'species' && hash != 'overview' && hash != '') {
				dataTables_search.val(decodeURIComponent(hash)).focus();
				oTable.fnFilter(decodeURIComponent(hash));
			}
		};

		function append_download_links() {
          	// append download links if genomic coordinates are found
          	var url = '/api/v1/rna/' + obj.upi;
			if ( obj.enable_genomic_features ) {
		        $(obj.config.dom.downloads).append('<li><a href="' + url + '.bed"  download="'  + obj.upi + '.bed">bed</a></li>')
		                                   .append('<li><a href="' + url + '.gff"  download="'  + obj.upi + '.gff">gff</a></li>')
		                                   .append('<li><a href="' + url + '.gff3" download="'  + obj.upi + '.gff3">gff3</a></li>');
        	}
		};

	};
};
