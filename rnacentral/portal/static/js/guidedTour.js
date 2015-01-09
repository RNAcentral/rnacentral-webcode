/*
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

var guidedTour = function() {

	// facilitates skipping steps using step names instead of indexes
	var steps = {
		'overview': 0,
		'xref-table': 1,
		'citations': 2,
		'genoverse-button': 3,
		'using-genoverse': 4,
		'sequence': 5,
		'additional-features': 6,
		'thank-you': 7,
	};

	this.tour = {
		id: 'tour-hopscotch',
		showPrevButton: true,
		onStart: function(){
			// make sure we are on the overview tab
			$('*[data-target="#overview"]').tab('show');
		},
		scrollDuration: 700,
		steps: [
			{
				title: 'Overview',
				content: 'Each page describes a unique RNA sequence, grouping together annotations from multiple organisms.',
				target: 'overview',
				placement: 'top',
			},

			{
				title: 'Database annotations',
				content: 'Databases that refer to this sequence are listed here.' +
						 'The table can be <strong>filtered</strong> using the search box on the right.',
				target: '#xrefs-table-div',
				placement: 'top',
				onShow: function() {
					$('#xrefs-table_filter input').focus();
				},
			},

			{
				title: 'Literature citations',
				content: 'All database annotations are linked to the relevant citations.',
				target: '.literature-refs-retrieve',
				placement: 'left',
				onShow: function(){
					$('.literature-refs-retrieve').first().click(); // retrieve citations
				},
				onNext: function(){
					$('.literature-refs-retrieve').first().click(); // slide up
					if ($('.genoverse-xref').length === 0) {
						hopscotch.showStep(steps.sequence); // skip genoverse steps
					}
				},
			},

			//
			// branch: genome annotations present
			//
			{
				title: 'Embedded genome browser',
				content: 'Some annotations are linked to their genomic location and have additional functionality. <br>' +
				     	 'Click <strong>View genomic location</strong> to open a genome browser on this page.',
				target: '.genoverse-xref',
				placement: 'top',
				nextOnTargetClick: true, // go to the next step if the target link is clicked
				onNext: function(){
					$('.genoverse-xref').first().click(); // launch genoverse
				},
			},

			{
				title: 'Using the embedded browser',
				content: 'You can scroll along the genome or click on the entries ' +
						 'to view <strong>popup menus</strong> with additional information. <br>' +
						 '<a href="/help/genomic-mapping" target="_blank">Learn more</a>',
				target: 'genoverse',
				placement: 'top',
			},
			//
			// end of branch
			//


			{
				title: 'RNA sequence',
				content: 'This sequence is uniquely associated with the RNAcentral URS id.',
				target: '.pre-scrollable',
				placement: 'top',
				delay: 400,
				onNext: function(){
					if ($('.genoverse-xref').length > 0) {
						hopscotch.showStep(steps['thank-you']);
					} else {
						hopscotch.showStep(steps['additional-features']);
					}
				},
				onPrev: function(){
					if ($('.genoverse-xref').length > 0) {
						hopscotch.showStep(steps['using-genoverse']);
					} else {
						hopscotch.showStep(steps.citations);
					}
				},
			},

			//
			// branch: no genome annotations present
			// when no genome annotations are available, suggest viewing a page
			//
			{
				title: 'Additional features',
				content: 'More features available for some entries. <br>' +
				         'For example, take a tour <a href="/rna/URS000025784F" target="_blank">here</a> ' +
				         '(opens in a new window).', // XIST/TSIX page
				target: '#xrefs-table-div',
				placement: 'top',
				showSkip: true, // show Skip button instead of Next
			},
			//
			// end of branch
			//

			{
				title: 'Thank you!',
				content: 'Feel free to take the tour again anytime.',
				target: 'guided-tour',
				placement: 'left',
				onPrev: function(){
					if ($('.genoverse-xref').length > 0) {
						hopscotch.showStep(steps.sequence);
					} else {
						hopscotch.showStep(steps['additional-features']);
					}
				},
			},
		],
	};

};

guidedTour.prototype.initialize = function() {

	var obj = this;

    $('#guided-tour').click(function(){
      var startingStep = 0; // first step
      hopscotch.startTour(obj.tour, startingStep);
    });
};
