var HomepageController = function($scope) {
    // detect if a multi-page tour is already in progress
    if (hopscotch.getState() === "homepage-tour:4") {
        hopscotch.startTour(obj.tour, 0);
    }

    $('#expert-databases').slick({
        draggable: true,
        rows: 1,
        dots: true,
        adaptiveHeight: true,
        infinite: true,
        lazyLoad: 'ondemand',
        slidesToShow: 5,
        slidesToScroll: 5,
        arrows: true,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 5,
                    slidesToScroll: 5,
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 4,
                    slidesToScroll: 4
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 320,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            }
        ],
    });
};
HomepageController.$inject = ['$scope'];


angular.module("homepage", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap'])
    .controller("HomepageController", HomepageController)
    .run(['$rootScope', '$window', 'routes', function($rootScope, $window, routes) {

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

        /**
        * Hopscotch guided tour.
        */
        $rootScope.tour = {
            id: 'homepage-tour',
            showPrevButton: true,
            scrollDuration: 700,
            steps: [
                {
                    title: 'Search by anything',
                    content: "You can search by <em>gene name</em>, <em>species</em>, <em>accession</em> or any other keyword. <a href={% url 'help-text-search' %} target=&quot;_blank&quot;>Explore examples</a>",
                    target: 'query-text',
                    placement: 'bottom',
                },
                {
                    title: 'Use search facets to explore the data',
                    content: 'Browse all RNAcentral sequences using <strong>faceted search</strong>',
                    target: 'btn-browse-sequences',
                    placement: 'top',
                },
                {
                    title: 'Search for similar sequences across databases',
                    content: 'For the first time, you can search data from multiple RNA databases in one go',
                    target: 'btn-sequence-search',
                    placement: 'top',
                },
                {
                    title: 'Navigate to your favourite genome region',
                    content: 'View RNAcentral sequences alongside genes and transcripts from <a href="http://ensembl.org">Ensembl</a> and <a href="http://ensemblgenomes.org">Ensembl Genomes</a>',
                    target: 'btn-genome-browser',
                    placement: 'top',
                    multipage: true,
                    onNext: function() {
                        window.location = '/rna/URS000025784F';
                    }
                },
                {
                    title: 'Overview',
                    content: 'Each page describes a unique RNA sequence, grouping together annotations from multiple organisms.',
                    target: 'overview',
                    placement: 'top',
                    onShow: function() {
                        // make sure we are on the overview tab
                        $('*[data-target="#overview"]').tab('show');
                    }
                },

                {
                    title: 'Database annotations',
                    content: 'Databases that refer to this sequence are listed here.' +
                             'The table can be <strong>filtered</strong> using the search box on the right.',
                    target: '#xrefs-table-div',
                    placement: 'top',
                    onShow: function() {
                        $('#annotations-table_filter input').focus();
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
                    }
                }
		    ]
	    };
    }]);