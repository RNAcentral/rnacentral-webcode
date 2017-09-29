var xrefs = {
    bindings: {
        upi: '<',
        timeout: '<?',
        page: '<?',
        pageSize: '<?',
        taxid: '<?',
        onActivatePublications: '&'
    },
    controller: ['routes', '$http', '$interpolate', '$timeout', function(routes, $http, $interpolate, $timeout) {
        var ctrl = this;

        ctrl.serverSidePagination = function(page) {
            ctrl.page = page;
            $http.get(ctrl.dataEndpoint, {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.xrefs = response.data.results;

                    $timeout(function() {
                        $('#annotations-table').DataTable({
                            "columnDefs": [
                                { targets: [0, 1, 2], visible: true },
                                { targets: [3, 4, 5], visible: false}
                            ], // hide columns, but keep them sortable
                            "autoWidth": true, // pre-recalculate column widths
                            "dom": "ftpil", // filter, table, pagination, information, length
                            //"paginationType": "bootstrap", // requires dataTables.bootstrap.js
                            "deferRender": false, // defer rendering until necessary
                            "language": {
                                "search": "", // don't display the "Search:" bit
                                "info": "_START_-_END_ of _TOTAL_", // change the informational text
                                "paginate": {
                                    "next": "",
                                    "previous": "",
                                }
                            },
                            "order": [[ 5, "desc" ]], // prioritize entries with genomic coordinates
                            "lengthMenu": [[5, 10, 20, 50, -1], [5, 10, 20, 50, "All"]],
                            "initComplete": function(settings, json) {
                                // some weird scripts sets width smaller than it should be
                                $("#annotations-table").css("width",  "100%");

                                // modify filter field and move it up
                                $('.dataTables_filter input').attr('placeholder', 'Filter table')
                                                             .attr('tabindex', 2)
                                                             .attr('type', 'search')
                                                             .addClass('form-control input-sm');

                                $('#annotations-table_filter').appendTo('#annotations-datatables-filter')
                                                              .addClass('pull-right hidden-xs');

                                // replace angular row counter with datatables one
                                $('#annotations-datatables-counter').html('');
                                $('#annotations-table_info').appendTo('#annotations-datatables-counter');

                                // create our own pagination that makes requests to the server side
                                var totalPages = Math.floor(reponse.data.count, ctrl.pageSize);
                                var pagination = $('ul').addClass('pagination pagination-sm');
                                for (var page = 0; page < totalPages; page++) {
                                    var page = $('li');
                                    if (page == ctrl.page) page.addClass('active');
                                    pagination.append(page);
                                }
                                pagination.on('click', ctrl.serverSidePagination);
                                pagination.appendTo('.annotations-datatables-controls');
                                pagination.addClass('pull-left');

                                $('.table th').css('padding-right','1.5em');
                            }
                        });
                    });
                },
                function(response) {
                    // TODO: display an error message in template!
                    console.log("Error happened while downloading data");
                }
            );
        };

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.timeout = parseInt(ctrl.timeout) || 50000;
            ctrl.page = ctrl.page || 1;
            ctrl.pageSize = ctrl.pageSize || 5;

            // Request xrefs from server (with taxid, if necessary)
            ctrl.dataEndpoint;
            if (ctrl.taxid) ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            $http.get(ctrl.dataEndpoint, {timeout: ctrl.timeout}).then(
                function(response) {
                    ctrl.xrefs = response.data.results;

                    ctrl.displayedXrefs = ctrl.xrefs.slice();

                    // $timeout() call is to ensure that xrefs data is rendered
                    // into the DOM before initializing DataTables
                    $timeout(function() {
                        $("#annotations-table").DataTable({
                            "columnDefs": [
                                { targets: [0, 1, 2], visible: true },
                                { targets: [3, 4, 5], visible: false}
                            ], // hide columns, but keep them sortable
                            "autoWidth": true, // pre-recalculate column widths
                            "dom": "ftpil", // filter, table, pagination, information, length
                            //"paginationType": "bootstrap", // requires dataTables.bootstrap.js
                            "deferRender": false, // defer rendering until necessary
                            "language": {
                                "search": "", // don't display the "Search:" bit
                                "info": "_START_-_END_ of _TOTAL_", // change the informational text
                                "paginate": {
                                    "next": "",
                                    "previous": "",
                                }
                            },
                            "order": [[ 5, "desc" ]], // prioritize entries with genomic coordinates
                            "lengthMenu": [[5, 10, 20, 50, -1], [5, 10, 20, 50, "All"]],
                            "initComplete": function(settings, json) {

                                // some weird scripts sets width smaller than it should be
                                $("#annotations-table").css("width",  "100%");

                                // modify filter field and move it up
                                $('.dataTables_filter input').attr('placeholder', 'Filter table')
                                                             .attr("tabindex", 2)
                                                             .attr('type', 'search')
                                                             .addClass('form-control input-sm');

                                $('#annotations-table_filter').appendTo('#annotations-datatables-filter')
                                                              .addClass('pull-right hidden-xs');

                                // replace angular row counter with datatables one
                                $('#annotations-datatables-counter').html('');
                                $('#annotations-table_info').appendTo('#annotations-datatables-counter');

                                // tweak pagination controls
                                if ( $('.dataTables_paginate').find('li').length == 1 ) {
                                    // hide pagination controls for tables with one page
                                    $('.dataTables_paginate').hide();
                                    $('#annotations-table_length').hide();
                                }
                                else {
                                    // move pagination
                                    $('.dataTables_paginate').addClass('pull-left')
                                                             .appendTo('.annotations-datatables-controls');
                                    $('#annotations-table_length').addClass('pull-right text-muted small')
                                                                  .appendTo('.annotations-datatables-controls');
                                }

                                $('.table th').css('padding-right','1.5em');
                            }
                        });
                    });

                },
                function(response) {
                    // if it took server too long to respond and request was aborted by timeout
                    // send a paginated request instead and fallback to server-side processing
                    if (response.status === -1) {  // for timeout response.status is -1
                        ctrl.serverSidePagination();
                    }
                    else {
                        // TODO: display an error message in template!
                        console.log("Error happened while downloading data");
                    }


                }
            );
        }
    }],
    templateUrl: '/static/js/components/sequence/xrefs/xrefs.html'
};

angular.module("rnaSequence").component("xrefs", xrefs);
