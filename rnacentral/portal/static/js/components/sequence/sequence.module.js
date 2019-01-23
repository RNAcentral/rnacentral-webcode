var rnaSequenceController = function($scope, $location, $window, $rootScope, $compile, $http, $q, $filter, $timeout, $interpolate, routes, GenoverseUtils) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2];
    $scope.taxid = $location.path().split('/')[3];  // TODO: this might not exist!
    $scope.hide2dTab = true;
    $scope.hideGoAnnotations = true;

    $scope.fetchRnaError = false; // hide content and display error, if we fail to download rna from server
    $scope.fetchGenomeLocationsStatus = 'loading'; // 'loading' or 'error' or 'success'

    // avoid a terrible bug with intercepted 2-way binding: https://github.com/RNAcentral/rnacentral-webcode/issues/308
    $scope.browserLocation = {start: undefined, end: undefined, chr: undefined, genome: undefined, domain: undefined};

    // go modal handling
    $scope.goTermId = null;
    $scope.goChartData = '';
    $scope.goModalStatus = '';

    // Tab controls
    // ------------

    // programmatically switch tabs
    $scope.activeTab = 0;
    $scope.activateTab = function (index) {
        $scope.activeTab = parseInt(index);  // have to convert index to string
    };

    // Downloads tab shouldn't be clickable
    $scope.checkTab = function ($event, $selectedIndex) {
        if ($selectedIndex == 3) {
            // don't call $event.stopPropagation() - we need the link on the tab to open a dropdown;
            $event.preventDefault();
        }
    };

    // This is terribly annoying quirk of ui-bootstrap that costed me a whole day of debugging.
    // When it transcludes uib-tab-heading, it creates the following link:
    //
    // <a href ng-click="select($event)" class="nav-link ng-binding" uib-tab-heading-transclude>.
    //
    // Unfortunately, htmlAnchorDirective.compile attaches an event handler to links with empty
    // href attribute: if (!element.attr(href)) {event.preventDefault();}, which intercepts
    // the default action of our download links in Download tab.
    //
    // Thus we have to manually open files for download by ng-click.
    $scope.download = function (format) {
        $window.open('/api/v1/rna/' + $scope.upi + '.' + format, '_blank');
    };

    // function passed to the 2D component in order to show the 2D tab
    // if there are any 2D structures
    $scope.show2dTab = function () {
        $scope.hide2dTab = false;
    };

    $scope.showGOAnnotations = function () {
        $scope.hideGoAnnotations = false;
    };


    // Hopscotch tour
    // --------------

    // hopscotch guided tour (currently disabled)
    $scope.activateTour = function () {
        // hopscotch_tour = new guidedTour;
        // hopscotch_tour.initialize();
        hopscotch.startTour($rootScope.tour, 4);  // start from step 4
    };

    // Publications
    // ------------

    $scope.activatePublications = function () {
        $('html, body').animate({ scrollTop: $('#publications').offset().top }, 1200);
    };

    // Data fetch functions
    // --------------------

    $scope.fetchGenomes = function() {
        return $q(function(resolve, reject) {
            $http.get(routes.genomesApi({ ensemblAssembly: "" }), { params: { page: 1, page_size: 1000000 } }).then(
                function (response) {
                    $scope.genomes = response.data.results;
                    resolve(response.data);
                },
                function () {
                    $scope.fetchGenomeLocationsStatus = 'error';
                    reject();
                }
            )
        });
    };

    $scope.fetchGenomeLocations = function () {
        return $q(function (resolve, reject) {
            $http.get(routes.apiGenomeLocationsView({ upi: $scope.upi, taxid: $scope.taxid })).then(
                function (response) {
                    // sort genome locations in a biologically relevant way
                    $scope.locations = response.data.sort(function(a, b) {
                        if (a.chromosome !== b.chromosome) {  // sort by chromosome first
                            if (isNaN(a.chromosome) && (!isNaN(b.chromosome))) return 1;
                            else if (isNaN(b.chromosome) && (!isNaN(a.chromosome))) return -1;
                            else if (isNaN(a.chromosome) && (isNaN(b.chromosome))) return a.chromosome > b.chromosome ? 1 : -1;
                            else return (parseInt(a.chromosome) - parseInt(b.chromosome));
                        } else {
                            return a.start - b.start;  // sort by start within chromosome
                        }
                    });

                    resolve($scope.locations);
                },
                function () {
                    $scope.fetchGenomeLocationsStatus = 'error';
                    reject();
                }
            );
        });
    };

    $scope.fetchRna = function () {
        return $q(function (resolve, reject) {
            $http.get(routes.apiRnaView({upi: $scope.upi})).then(
                function (response) {
                    $scope.rna = response.data;
                    resolve();
                },
                function () {
                    $scope.fetchRnaError = true;
                    reject();
                }
            );
        });
    };

    $scope.fetchRfamHits = function () {
        return $http.get(routes.apiRfamHitsView({upi: $scope.upi, taxid: $scope.taxid}), {params: {page_size: 10000000000}})
    };

    $scope.fetchSequenceFeatures = function() {
        return $http.get(
            routes.apiSequenceFeaturesView({upi: $scope.upi, taxid: $scope.taxid}),
            {params: {page_size: 10000000000}}
        )
    };

    // View functionality
    // ------------------

    // populate data for angular-genoverse instance
    $scope.activateGenomeBrowser = function (start, end, chr, genome) {
        if (!$scope.Genoverse) $scope.Genoverse = Genoverse;
        if (!$scope.genoverseUtils) $scope.genoverseUtils = new GenoverseUtils($scope);
        if (!$scope.exampleLocations) $scope.exampleLocations = $scope.genoverseUtils.exampleLocations;

        // add some padding to both sides of feature
        var length = end - start;
        $scope.browserLocation.start = start - length < 0 ? 1 : start - length;
        $scope.browserLocation.end = end + length > $scope.chromosomeSize ? $scope.chromosomeSize : end + length;
        $scope.browserLocation.chr = chr;
        $scope.browserLocation.genome = genome;
        $scope.browserLocation.domain = $scope.genoverseUtils.getGenomeObject($scope.browserLocation.genome, $scope.genomes).subdomain;
        $scope.browserLocation.highlights = [{
            start: start,
            end: end,
            chr: chr,
            label: "Selected location (" + $filter('number')(start) + " - " + $filter('number')(end) + ")",
            removable: true
        }];

        // cache selectedLocation to highlight it in table, ignore start/end padding
        $scope.selectedLocation = {
            genome: genome,
            chr: chr,
            start: start,
            end: end,
            domain: $scope.browserLocation.domain
        };
    };

    $scope.scrollToGenomeBrowser = function () {
        // if '#genoverse' is already rendered, scroll to it
        if ($('#genoverse').length) {
            $('html, body').animate({scrollTop: $('#genoverse').offset().top - 200}, 800);
            if ($scope.scrollToGenomeBrowserAttempts) delete $scope.scrollToGenomeBrowserAttempts;
        }
        else { // if '#genoverse' not rendered, wait 0.5 sec and another 0.5 sec... but no more than 5 attempts total;
            // first attempt
            if (!$scope.scrollToGenomeBrowserAttempts) {
                $scope.scrollToGenomeBrowserAttempts = 1;
                $timeout($scope.scrollToGenomeBrowser, 500);
            } else { // not first
                if ($scope.scrollToGenomeBrowserAttempts < 6) { // more attempts remaining
                    $scope.scrollToGenomeBrowserAttempts++;
                    $timeout($scope.scrollToGenomeBrowser, 500);
                } else { // no more attempts
                    delete $scope.scrollToGenomeBrowserAttempts;
                }
            }
        }
    };

    $scope.isSelectedLocation = function (location) {
        var isSelected = location.species === $scope.selectedLocation.genome &&
                         location.chromosome === $scope.selectedLocation.chr &&
                         location.start === $scope.selectedLocation.start &&
                         location.end === $scope.selectedLocation.end;

        return isSelected;
    };

    /**
     * Pass non-null termId to open Go modal and null to close
     */
    $scope.toggleGoModal = function(termId) {
        $scope.goTermId = termId;

        if (termId != null) {
            var ontology = termId.split(':')[0].toLowerCase();

            $('#go-annotation-chart-modal').detach().appendTo("body");

            $('#go-annotation-chart-modal').modal();

            $scope.goModalStatus = 'loading';
            $http.get(routes.quickGoChart({ ontology: ontology, term_ids: termId }), { timeout: 5000 }).then(
                function(response) {
                    $scope.goModalStatus = 'loaded';
                    $scope.goChartData = 'data:image/png;charset=utf-8;base64,' + response.data;
                },
                function(error) {
                    $scope.goModalStatus = 'failed';
                }
            );
        } else {
            $('#go-annotation-chart-modal').modal('toggle');
        }
    };

    /**
     * Copy to clipboard buttons allow the user to copy an RNA sequence as RNA or DNA into
     * the clipboard by clicking on them. Buttons are located near the Sequence header.
     */
    $scope.activateCopyToClipboardButtons = function () {
        /**
         * Returns DNA sequence, corresponding to input RNA sequence. =)
         */
        function reverseTranscriptase(rna) {
            return rna.replace(/U/ig, 'T'); // case-insensitive, global replacement of U's with T's
        }

        var rnaClipboard = new Clipboard('#copy-as-rna', {
            "text": function () { return $scope.rna.sequence; }
        });

        var dnaClipbaord = new Clipboard('#copy-as-dna', {
            "text": function () { return reverseTranscriptase($scope.rna.sequence); }
        });
    };

    /**
     * Creates feature viewer d3 plugin, that displays RNA sequence graphically
     * and annotates it with features, such as Rfam models, modified or
     * non-canonical nucleotides.
     */
    $scope.activateFeatureViewer = function () {
        //Create a new Feature Viewer and add some rendering options
        $scope.featureViewer = new FeatureViewer(
            $scope.rna.sequence,
            "#feature-viewer",
            {
                showAxis: true,
                showSequence: true,
                brushActive: true,
                toolbar: true,
                // bubbleHelp: true,
                zoomMax: 20,
                tooltipFontSize: '14px',
            }
        );

        // if any non-canonical nucleotides found, show them on a separate track
        nonCanonicalNucleotides = [];
        for (var i = 0; i < $scope.rna.sequence.length; i++) {
            if (['A', 'U', 'G', 'C'].indexOf($scope.rna.sequence[i]) === -1) {
                // careful with indexes here: people start counting from 1, computers - from 0
                nonCanonicalNucleotides.push({x: i+1, y: i+1, description: $scope.rna.sequence[i]})
            }
        }
        if (nonCanonicalNucleotides.length > 0) {
            $scope.featureViewer.addFeature({
                data: nonCanonicalNucleotides,
                name: "Non-canonical",
                className: "nonCanonical",
                color: "#b94a48",
                type: "rect",
                filter: "type1"
            });
        }
    };

    /**
     * Reset featureViewer
     */
    $scope.resetFeatureViewerZoom = function() {
        if ($scope.featureViewer) {
            $scope.featureViewer.resetZoom();
        }
    };

    /**
     * featureViewer is rendered into $('#feature-viewer'),
     * which might not be present, if its tab was not initialized.
     */
    $scope.featureViewerContainerReady = function () {
        return $q(function (resolve, reject) {
            var timeout = function () {
                if ($('#feature-viewer').length) resolve();
                else $timeout(timeout, 500);
            };
            $timeout(timeout, 500);
        });
    };

    /**
     * Modified nucleotides visualisation.
     *
     * Can be invoked upon changing Xrefs page, if server-side pagination's on.
     */
    $scope.createModificationsFeature = function(modifications, accession) {
        if (!$scope.featureViewer.hasFeature(accession, "id")) { // if feature track's already there, don't duplicate it
            // sort modifications by position
            modifications.sort(function(a, b) {return a.position - b.position});

            // loop over modifications and insert span tags with modified nucleotide data
            var data = [];
            for (var i = 0; i < modifications.length; i++) {
                data.push({
                    x: modifications[i].position,
                    y: modifications[i].position,
                    description: 'Modified nucleotide ' + modifications[i].chem_comp.id + modifications[i].chem_comp.one_letter_code + ' <br> ' + modifications[i].chem_comp.description
                });
            }

            /**
             * If featureViewer was already initialized, add feature to it - otherwise, give it a second and try again.
             */
            var addModifications = function() {
                if ($scope.featureViewer) {
                    $scope.featureViewer.addFeature({
                        id: accession,
                        data: data,
                        name: "Modified",  // in " + accession.substr(0, 8),
                        className: "modification",
                        color: "#005572",
                        type: "rect",
                        filter: "type1"
                    });
                } else {
                    $timeout(addModifications, 1000);
                }
            };

            addModifications()
        }
    };

    $scope.createFeatureViewerModal = function(targetId, heading, content) {
        var html =  '<div id="modalWindow" class="modal fade" style="display:none; top: 20%" tabindex="-1">';
        html += '<div class="modal-dialog" role="document">';
        html += '<div class="modal-content">';
        html += '<div class="modal-header">';
        html += '<a class="close" data-dismiss="modal">×</a>';
        html += '<h2>' + heading + '</h2>'
        html += '</div>'; // modal-header
        html += '<div class="modal-body">';
        html += '<p>';
        html += content;
        html += '</p>';
        html += '</div>'; // modal-body
        html += '</div>'; // modal-content
        html += '</div>'; // modal-dialog
        html += '</div>';  // modalWindow
        $("#" + targetId).html(html);
        $("#modalWindow").modal('toggle');
    };

    // Initialization
    //---------------

    $scope.activateCopyToClipboardButtons();

    // featureViewer requires its tab to be open - container ready - and $scope.rna
    $q.all([$scope.fetchRna(), $scope.featureViewerContainerReady()]).then(function() {
        $scope.activateFeatureViewer();

        // show Rfam models, found in this RNA
        $scope.fetchRfamHits().then(
            function(response) {
                $scope.rfamHits = response.data.results;

                // wrap hit.rfam_model.thumbnail_url into our proxy to suppress http/https mixed content warning
                $scope.rfamHits.forEach(function(hit) {
                    hit.rfam_model.thumbnail_url = routes.proxy({url: encodeURIComponent(hit.rfam_model.thumbnail_url)});
                });

                data = [];
                for (var i = 0; i < response.data.results.length; i++) {
                    var direction, x, y;
                    if (response.data.results[i].sequence_start <= response.data.results[i].sequence_stop) {
                        direction = '>';
                        x = response.data.results[i].sequence_start;
                        y = response.data.results[i].sequence_stop;
                    } else {
                        direction = '<';
                        x = response.data.results[i].sequence_stop;
                        y = response.data.results[i].sequence_start;
                    }

                    data.push({
                        x: x + 1,
                        y: y,
                        description: direction + " " + response.data.results[i].rfam_model.rfam_model_id + " " + response.data.results[i].rfam_model.long_name
                    })
                }

                if (data.length > 0) { // add Rfam feature track, only if there are any data
                    $scope.featureViewer.addFeature({
                        data: data,
                        name: "Rfam families",
                        className: "rfamModels",
                        color: "#d28068",
                        type: "rect",
                        filter: "type1",
                        height: 16,
                    });

                    $('svg .rfamModelsGroup text').css('fill', 'white').css('font-size', 'small');

                    $('svg g.rfamModelsGroup').on('click', function(){
                        var text = $(this).find('text').text().split(" ");
                        var rfam_id = text[1];
                        var description = text.slice(2).join(' ');

                        var content = '<div class="media">';
                        content += '<div class="media-left style="padding-left: 0;">';
                        content += '  <a href="http://rfam.org/family/' + rfam_id + '" class="no-icon">';
                        content += '    <img class="media-object thumbnail"';
                        content += '      src="/api/internal/proxy?url=http%3A%2F%2Frfam.org%2Ffamily%2F' + rfam_id + '%2Fthumbnail"';
                        content += '      style="max-width: 350px; max-height: 350px;"';
                        content += '      title="Consensus secondary structure"';
                        content += '      alt="' + rfam_id + ' secondary structure">';
                        content += '  </a>';
                        content += '</div>';
                        content += '<div class="media-body">';
                        content += '  <p>' + description + '<br>';
                        content += '    <a href="http://rfam.org/family/' + rfam_id + '" class="no-icon" target="_blank">';
                        content += '      Learn more in Rfam &rarr; ';
                        content += '    </a>';
                        content += '  </p>';
                        content += '</div>';
                        content += '</div>';

                        $scope.createFeatureViewerModal('feature-viewer-modal', 'Rfam family ' + rfam_id, content);
                    });
                }
            },
            function() {
                console.log('failed to fetch Rfam hits');
            }
        );

        // for taxid-specific pages, show CRS features, found in this RNA
        if ($scope.taxid) {
            $scope.fetchSequenceFeatures().then(
                function(response){
                    $scope.features = response.data.results.sort(function(a, b) {return a.start - b.start});

                    // trim start/stop of each feature to make sure it's not out of sequence bounds
                    var data = $scope.features.map(function(feature) {
                        var datum = {
                            x: feature.start >= 0 ? feature.start : 1,
                            y: feature.stop < $scope.rna.length ? feature.stop : $scope.rna.length - 1,
                            description: 'Conserved feature ' + feature.metadata.crs_id
                        };

                        // if (feature.metadata.should_highlight) { datum.color = "#86A5B9"; }

                        return datum;
                    });

                    var addFeature = function() {
                        if ($scope.featureViewer) {
                            $scope.featureViewer.addFeature({
                                id: "crs",
                                data: data,
                                name: "Conserved features",
                                className: "crsFeatures",
                                color: "#365569",
                                type: "rect",
                                filter: "type1",
                                height: 16,
                            });

                            $('svg .crsFeaturesGroup text').css('fill', 'white').css('font-size', 'small');

                            $('svg g.crsFeaturesGroup').on('click', function(){
                                var text = $(this).find('text').text().split(" ");
                                var crs_id = text[text.length-1];
                                var content = '<div class="media">';
                                content += '<div class="media style="padding-left: 0;">';
                                content += ' <img class="media-object thumbnail"';
                                content += '   src="https://rth.dk/resources/rnannotator/crs/vert/data/figure/alignment/hg38_17way/' + crs_id.slice(0,2) + '/' + crs_id + '_ext_liftover_17way.aln.png"';
                                content += '   style="max-width: 550px; max-height: 550px;">';
                                content += '</div>';
                                content += '<div class="media-body">';
                                content += '  <ul class="list-unstyled">';
                                content += '    <li><a href="https://rth.dk/resources/rnannotator/crs/vert/pages/cmf.data.collection.openallmenus.php?crs=' + crs_id + '" class="no-icon" style="font-size:larger;" target="_blank">';
                                content += '      Learn more in CRS database &rarr; ';
                                content += '    </a></li>';
                                content += '    <li><i class="fa fa-search"></i> <a href="/search?q=conserved_structure:%22' + crs_id + '%22">Find other sequences with this feature</a></li>'
                                content += '    <li><i class="fa fa-question-circle"></i> <a href="/help/conserved-motifs">What are conserved features?</a></li>';
                                content += '  </ul>';
                                content += '</div>';
                                content += '</div>';

                                $scope.createFeatureViewerModal('feature-viewer-modal', 'Conserved feature ' + crs_id, content);
                            });
                        } else {
                            $timeout(addFeature, 1000)
                        }
                    };

                    // for non-empty tracks, add CRS feature track
                    if ($scope.features.length > 0) { addFeature(); }
                }
            )
        }

        // adjust feature viewer css
        $('.header-position').css('margin-top', 0);
        $('.header-zoom').css('margin-top', 0);
    });

    if ($scope.taxid) {
        $scope.fetchGenomeLocations().then(function() {
            $scope.fetchGenomeLocationsStatus = 'success';

            // if any locations, activate genome browser
            if ($scope.locations.length > 0) {
                var location = $scope.locations[0];
                $scope.fetchGenomes().then(function() {
                    $scope.activateGenomeBrowser(location.start, location.end, location.chromosome, location.species);
                });
            }

        }, function() {
            $scope.fetchGenomeLocationsStatus = 'error';
        });
    }
};

rnaSequenceController.$inject = ['$scope', '$location', '$window', '$rootScope', '$compile', '$http', '$q', '$filter', '$timeout', '$interpolate', 'routes', 'GenoverseUtils'];


/**
 * Configuration function that allows this module to load data
 * from white-listed domains (required for JSONP from ebi.ac.uk).
 * @param $sceDelegateProvider
 */
var sceWhitelist = function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        'self',
        // Allow loading from EBI
        'http://www.ebi.ac.uk/**'
    ]);
};
sceWhitelist.$inject = ['$sceDelegateProvider'];


angular.module("rnaSequence", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'routes'])
    .config(sceWhitelist)
    .controller("rnaSequenceController", rnaSequenceController);
