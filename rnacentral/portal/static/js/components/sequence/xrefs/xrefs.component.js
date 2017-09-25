var xrefs = {
    bindings: {
        upi: '<',
        timeout: '<?',
        taxid: '<?',
        onActivatePublications: '&'
    },
    controller: ['routes', '$http', '$interpolate', '$timeout', function(routes, $http, $interpolate, $timeout) {
        var ctrl = this;

        ctrl.$onInit = function() {

            // Request xrefs from server (with taxid, if necessary)
            var dataEndpoint;
            if (ctrl.taxid) dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            // set default for ctrl.timeout, if not given
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;

            $http.get(dataEndpoint, {timeout: ctrl.timeout}).then(
                function(response) {
                    ctrl.xrefs = response.data.results;

                    // $timeout is to ensure that xrefs data is rendered into the DOM
                    // before initializing DataTables
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
                    // TODO: display an error message in template!
                    console.log("Error happened while downloading data");
                }
            );
        }
    }],
    templateUrl: '/static/js/components/sequence/xrefs/xrefs.html'
};

angular.module("rnaSequence").component("xrefs", xrefs);
