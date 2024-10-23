var rnaSequenceController = function($scope, $location, $window, $rootScope, $compile, $http, $q, $filter, $timeout, $interpolate, routes) {
    // Take upi and taxid from url. Note that $location.path() always starts with slash
    $scope.upi = $location.path().split('/')[2].toUpperCase();
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
    $scope.activate2dTab = function() {
	document.querySelector('#secondary-structures > a').click();
    }

    $scope.activateTaxonomyTab = function () {
	document.querySelector('#taxonomy > a').click();
    }

    // Downloads tab shouldn't be clickable
    $scope.checkTab = function ($event, $selectedIndex) {
	let getUrl = window.location.href.split("?");
	let getTab = getUrl[1];
	if ($selectedIndex == 5) {
	    // don't call $event.stopPropagation() - we need the link on the tab to open a dropdown;
	    $event.preventDefault();
	} else if ($selectedIndex == 0) {
	    // reload to avoid Genome Locations error when a page is initially opened in the 2D structure tab
	    window.location = getUrl[0];
	} else if ($selectedIndex == 1 && typeof getTab !== "undefined") {
	    // remove tab paremeter
	    $location.search('tab', null);
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
	    $http.get(routes.genomesApi({ ensemblAssembly: "" }), { params: { page: 1, page_size: 100 } }).then(
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
	return $http.get(routes.apiRfamHitsView({upi: $scope.upi, taxid: $scope.taxid}), {params: {page_size: 100}})
    };

    $scope.fetchQcStatus = function() {
	return $http.get(routes.qcStatusApi({upi: $scope.upi, taxid: $scope.taxid}), {params: {page_size: 100}})
    };

    $scope.fetchSequenceFeatures = function() {
	return $http.get(
	    routes.apiSequenceFeaturesView({upi: $scope.upi, taxid: $scope.taxid}),
	    {params: {page_size: 100}}
	)
    };

    // View functionality
    // ------------------

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
	    $('.selectedRect').hide();
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
	    /**
		* If featureViewer was already initialized, add feature to it - otherwise, give it a second and try again.
		*/
		var addModifications = function() {
		    if ($scope.featureViewer && !$scope.featureViewer.hasFeature(accession, "id")) {  // if feature track's already there, don't duplicate it
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

				$scope.featureViewer.addFeature({
					id: accession,
					data: data,
					name: "Modifications",
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

// function that creates the feature object for tmRNA
	$scope.tmRNAFeature = function(id, name) {
		return {
			features: [],
			normalize: function (feature) {
				return {
					x: feature.start >= 0 ? feature.start : 1,
					y: feature.stop < $scope.rna.length ? feature.stop : $scope.rna.length - 1,
					description: feature.metadata.coding_sequence ? 'Coding sequence: ' + feature.metadata.coding_sequence : '',
				}
			},
			addFeature: function (data) {
				$scope.featureViewer.addFeature({
					id: id,
					data: data,
					name: name,
					className: id + "Features",
					color: "#8d8a8a",
					type: "rect",
					filter: "type1",
					height: 16,
				});

				$('svg .tmRNAFeaturesGroup text').css('fill', 'white').css('font-size', 'small');
			},
		};
	}

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

		$('svg g.rfamModelsGroup').on('click', function() {
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
	var features = {
	    conserved_rna_structure: {
		features: [],
		normalize: function(feature) {
		    return {
			x: feature.start >= 0 ? feature.start : 1,
			y: feature.stop < $scope.rna.length ? feature.stop : $scope.rna.length - 1,
			description: 'Conserved feature ' + feature.metadata.crs_id
		    }
		},
		addFeature: function(data) {
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

		    $('svg g.crsFeaturesGroup').on('click', function() {
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
			content += '    <li><i class="fa fa-question-circle"></i> <a href="/help/sequence-features">What are conserved features?</a></li>';
			content += '    <li><i class="fa fa-book"></i> <a href="https://doi.org/10.1101/gr.208652.116" target="_blank">Paper by <i>Seemann et al</i> about the method</a></li>';
			content += '  </ul>';
			content += '</div>';
			content += '</div>';

			$scope.createFeatureViewerModal('feature-viewer-modal', 'Conserved feature ' + crs_id, content);
		    });
		},
	    },
	    mature_product: {
		features: [],
		normalize: function(feature) {
		    return {
			x: feature.start >= 0 ? feature.start + 1 : 1,
			y: feature.stop < $scope.rna.length ? feature.stop + 1 : $scope.rna.length,
			description: 'Mature miRNA ' + feature.metadata.related.replace('MIRBASE:', '')
		    };
		},
		addFeature: function(data) {
		    $scope.featureViewer.addFeature({
			id: "mature-mirna",
			data: data,
			name: "Mature miRNA",
			className: "matureMirnaFeatures",
			color: "#660099", // one of University of Manchester colors
			type: "rect",
			filter: "type1",
			height: 16,
		    });

		    $('svg .matureMirnaFeaturesGroup text').css('fill', 'white').css('font-size', 'small');

		    $('svg g.matureMirnaFeaturesGroup').on('click', function(){
			var text = $(this).find('text').text().split(" ");
			var mature_product_id = text[text.length-1];
			window.open('/link/mirbase:' + mature_product_id, '_blank');
		    });
		},
	    },
	    cpat_orf: {
		features: [],
		normalize: function(feature) {
		    var prob = feature.metadata.coding_probability.toLocaleString(undefined, {minimumFractionDigits: 2});
		    var cutoff = feature.metadata.cutoff;
		    return {
			x: feature.start >= 0 ? feature.start + 1 : 1,
			y: feature.stop < $scope.rna.length ? feature.stop + 1 : $scope.rna.length,
			description: 'ORF predicted by CPAT (Coding Probability: ' + prob + ', Min Cuttoff: ' + cutoff + ')',
		    };
		},
		addFeature: function(data) {
		    $scope.featureViewer.addFeature({
			id: 'cpat-orf',
			data: data,
			name: "CPAT ORF",
			className: "cpatOrfFeatures",
			color: "#e0c653",
			type: "rect",
			filter: "type1",
			height: 16,
		    });

		    $('svg .cpatOrfFeaturesGroup text').css('fill', 'white').css('font-size', 'small');
		},
	    },
		rna_editing_event: {
		features: [],
		normalize: function(feature) {
		    return {
			x: feature.start >= 0 ? feature.start : 1,
			y: feature.stop < $scope.rna.length ? feature.stop : $scope.rna.length - 1,
				description: 'REDIportal editing events (Edit: ' + feature.metadata.edit + ', Reference: ' + feature.metadata.reference + ')' + '<span hidden>' + feature.metadata.url + '</span>',
		    }
		},
		addFeature: function(data) {
		    $scope.featureViewer.addFeature({
			id: 'rediportal',
			data: data,
			name: "RNA editing events",
			className: "rediPortalFeatures",
			color: "#337ab7",
			type: "rect",
			filter: "type1",
			height: 16,
		    });

		    $('svg .rediPortalFeaturesGroup text').css('fill', 'white').css('font-size', 'small');

			$('svg g.rediPortalFeaturesGroup').on('click', function(){
			var rediPortalUrl = $(this).find('text').text().split("<span hidden>")[1].split("</span>")[0];
			window.open(rediPortalUrl, '_blank');
		    });
		},
		},
		anticodon: {
		features: [],
		normalize: function(feature) {
		    return {
			x: feature.start >= 0 ? feature.start : 1,
			y: feature.stop < $scope.rna.length ? feature.stop : $scope.rna.length - 1,
				description: 'Anticodon (Isotype: ' + feature.metadata.isotype + ', Sequence: ' + feature.metadata.sequence + ')',
		    }
		},
		addFeature: function(data) {
		    $scope.featureViewer.addFeature({
			id: 'anticodon',
			data: data,
			name: "Anticodon",
			className: "anticodonFeatures",
			color: "#267431",
			type: "rect",
			filter: "type1",
			height: 16,
		    });

		    $('svg .anticodonFeaturesGroup text').css('fill', 'white').css('font-size', 'small');
		},
		},
		tmrna_ccaequiv: $scope.tmRNAFeature('tmrna_ccaequiv', 'tmRNA CCAequiv'),
    	tmrna_body: $scope.tmRNAFeature('tmrna_body', 'tmRNA Body'),
		tmrna_ivs: $scope.tmRNAFeature('tmrna_ivs', 'tmRNA IVS'),
		tmrna_acceptor: $scope.tmRNAFeature('tmrna_acceptor', 'tmRNA Acceptor St'),
		tmrna_tagcds: $scope.tmRNAFeature('tmrna_tagcds', 'tmRNA TagCDS'),
		tmrna_exon: $scope.tmRNAFeature('tmrna_exon', 'tmRNA Exon'),
		tmrna_gpi: $scope.tmRNAFeature('tmrna_gpi', 'tmRNA Group I Intr'),
		tmrna_coding_region: $scope.tmRNAFeature('tmrna_coding_region', 'tmRNA Coding Reg'),
	};

	$scope.features = "pending";
	$scope.fetchSequenceFeatures().then(function(response){
	    response.data.results
		.sort(function(a, b) {return a.start - b.start})
		.filter(f => features.hasOwnProperty(f.feature_name))
		.forEach(function (feature) {
		    var obj = features[feature.feature_name];
		    obj.features.push(obj.normalize(feature));
		});

	    $scope.features = features;
	    Object.keys(features)
		.map(feature_type => features[feature_type])
		.filter(features => features.features.length > 0)
		.forEach(function(feature) {
		    if ($scope.featureViewer) {
			feature.addFeature(feature.features);
		    } else {
			$timeout(function() {
			    feature.addFeature(feature.features)
			}, 1000);
		    }
		});

	}, function() {
	    $scope.features = "failed";
	})
    }

    if ($scope.taxid) {
	$scope.qcStatus = "pending";
	$scope.fetchQcStatus().then(function(response) {
	    $scope.qcStatus = response.data;
	}, function(error) {
	    $scope.qcStatus = "failed";
	});
    }

    // adjust feature viewer css
    $('.header-position').css('margin-top', 0);
    $('.header-zoom').css('margin-top', 0);
});

if ($scope.taxid) {
    $scope.fetchGenomeLocations().then(function() {
	// if any locations, activate genome browser
	if ($scope.locations.length > 0) {
	    var location = $scope.locations[0];
	    $scope.fetchGenomes().then(function() {
		$scope.activateGenomeBrowser(location.start, location.end, location.chromosome, location.species);
	    });
	}
	$scope.fetchGenomeLocationsStatus = 'success';
    }, function() {
	$scope.fetchGenomeLocationsStatus = 'error';
    });
}
};

rnaSequenceController.$inject = ['$scope', '$location', '$window', '$rootScope', '$compile', '$http', '$q', '$filter', '$timeout', '$interpolate', 'routes'];


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
