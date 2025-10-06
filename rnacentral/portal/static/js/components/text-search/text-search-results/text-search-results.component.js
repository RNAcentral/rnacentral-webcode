var textSearchResults = {
    bindings: {},
    templateUrl: '/static/js/components/text-search/text-search-results/text-search-results.html',
    controller: ['$http', '$timeout', '$scope', '$filter', '$q', 'search', 'routes', 'normalizeExpertDbName',
    function($http, $timeout, $scope, $filter, $q, search, routes, normalizeExpertDbName) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // expose search service in template
            ctrl.search = search;

            // error flags for UI state
            ctrl.showExportError = false;
            ctrl.showExpertDbError = false;

            // urls used in template (hardcoded)
            ctrl.routes = routes;
            ctrl.normalizeExpertDbName = normalizeExpertDbName;

            // help urls
            ctrl.rfamHelp = "/help/qc";
            ctrl.crsHelp = "/help/sequence-features";
            ctrl.goHelp = "/help/gene-ontology-annotations";
            ctrl.genomeMappingHelp = "/help/genomic-mapping";

            // subspecies can be toggled on and off
            ctrl.includeSubspecies = !!search.query.match(/lineage_path:"(\d+)"/);

            // slider that allows users to set range of sequence lengths
            ctrl.setLengthSlider(); // initial value

            search.registerSearchCallback(function() { 
                ctrl.setLengthSlider(); 
            });

            // retrieve expert_dbs json for display in tooltips
            $http.get(routes.expertDbsApi({ expertDbName: '' })).then(
                function(response) {
                    ctrl.expertDbs = response.data;

                    // expertDbsObject has lowerCase db names as keys
                    ctrl.expertDbsObject = {};
                    for (var i=0; i < ctrl.expertDbs.length; i++) {
                        ctrl.expertDbsObject[ctrl.expertDbs[i].name.toLowerCase()] = ctrl.expertDbs[i];
                    }
                },
                function(response) {
                    ctrl.showExpertDbError = true;
                }
            );
        };

        // Add function to get entry type count
        ctrl.getEntryTypeCount = function(entryType) {
            if (!ctrl.search.result.facets) return 0;
            
            var entryTypeFacet = ctrl.search.result.facets.find(function(facet) {
                return facet.label === 'Entry type';
            });
            
            if (!entryTypeFacet) return 0;
            
            var facetValue = entryTypeFacet.facetValues.find(function(fv) {
                return fv.value === entryType;
            });
            
            return facetValue ? facetValue.count : 0;
        };

        // Length slider-related code
        // --------------------------

        /**
         * Sets new value of length slider upon init or search.
         */
        ctrl.setLengthSlider = function() {
            var query = ctrl.search.query;

            var min, max, floor, ceil;
            var lengthClause = 'length\\:\\[(\\d+) TO (\\d+)\\]';
            var lengthRegexp = new RegExp('length\\:\\[(\\d+) TO (\\d+)\\]', 'i');

            // remove length clause in different contexts
            var filteredQuery = query;
            filteredQuery = filteredQuery.replace(new RegExp(' AND ' + lengthClause + ' AND '), ' AND ', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(lengthClause + ' AND '), '', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(' AND ' + lengthClause), '', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(lengthClause), '', 'i') || 'RNA';

            // find min/max in query's lengthClause (if any), get floor/ceil by sending query without lengthClause
            var groups = lengthRegexp.exec(query);
            ctrl.getFloorCeil(filteredQuery).then(
                function(floorceil) {
                    floor = parseInt(floorceil[0].data.entries[0].highlights.length) ? parseInt(floorceil[0].data.entries[0].highlights.length) : 10;
                    ceil = parseInt(floorceil[1].data.entries[0].highlights.length);

                    if (groups) {
                        min = parseInt(groups[1]) < floor ? floor : parseInt(groups[1]);
                        max = parseInt(groups[2]) > ceil ? ceil : parseInt(groups[2]);
                    } else {
                        min = floor;
                        max = ceil;
                    }

                    ctrl.lengthSlider = ctrl.LengthSlider(min, max, floor, ceil);
                    $timeout(function () { $scope.$broadcast('rzSliderForceRender'); }); // issue render just in case
                },
                function (failure) { // non-mission critical, let's fallback to sensible defaults
                    var floor = 10;
                    var ceil = 2147483647; // macrocosm constant - if length exceeds it, EBI search fails

                    if (groups) {
                        min = parseInt(groups[1]) < floor ? floor : parseInt(groups[1]);
                        max = parseInt(groups[2]) > ceil ? ceil : parseInt(groups[2]);
                    } else {
                        min = floor;
                        max = ceil;
                    }

                    ctrl.lengthSlider = ctrl.LengthSlider(min, max, floor, ceil);
                    $timeout(function () { $scope.$broadcast('rzSliderForceRender'); }); // issue render just in case
                }
            );
        };

        /**
         * Issues additional queries to EBI search to get lowest and highest
         * lengths of sequences in this query.
         *
         * @param query - value of search.query
         * @returns {Promise} - resolves to Array of [floor, ceil]
         */
        ctrl.getFloorCeil = function(query) {
            function createEbeyeUrl(ascending) {
                ascending = ascending ? "ascending" : "descending";

                return routes.ebiSearch({
                    ebiBaseUrl: global_settings.EBI_SEARCH_ENDPOINT,
                    query: query ? search.preprocessQuery(query): query,
                    hlfields: "length",
                    facetcount: "",
                    facetfields: "length",
                    size: 1,
                    start: 0,
                    sort: "length:" + ascending
                });
            }

            var ascendingEbeyeUrl = createEbeyeUrl(true);
            var descendingEbeyeUrl = createEbeyeUrl(false);

            var ascendingQueryUrl = routes.proxy({url: encodeURIComponent(ascendingEbeyeUrl)});
            var descendingQueryUrl = routes.proxy({url: encodeURIComponent(descendingEbeyeUrl)});

            return $q.all([$http.get(ascendingQueryUrl), $http.get(descendingQueryUrl)]);
        };

        /**
         * Constructor-ish function (but no 'new' needed) that returns a model for length slider
         */
        ctrl.LengthSlider = function(min, max, floor, ceil) {
            return {
                min: min,
                max: max,
                options: {
                    floor: floor,
                    ceil: ceil,
                    logScale: true,
                    translate: function(value) {
                        if (value < 10000) return $filter('number')(value);
                        else return Number(Math.floor(value/1000)).toString() + 'k';
                    },
                    onEnd: ctrl.lengthSearch
                }
            };
        };

        /**
         * Edge case of facet search with length field applied.
         */
        ctrl.lengthSearch = function () {
            ctrl.facetSearch('length', '[' + ctrl.lengthSlider.min + ' TO ' + ctrl.lengthSlider.max + ']', true)
        };

        /**
         * Resets slider to default value
         */
        ctrl.resetSlider = function() {
            var lengthClause = 'length\\:\\[(\\d+) TO (\\d+)\\]';
            var lengthRegexp = new RegExp('length\\:\\[(\\d+) TO (\\d+)\\]', 'i');

            // remove length clause in different contexts
            var filteredQuery = search.query;
            filteredQuery = filteredQuery.replace(new RegExp(' AND ' + lengthClause + ' AND '), ' AND ', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(lengthClause + ' AND '), '', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(' AND ' + lengthClause), '', 'i');
            filteredQuery = filteredQuery.replace(new RegExp(lengthClause), '', 'i') || 'RNA';

            search.search(filteredQuery);
        };

        // Facets-related code
        // -------------------

        /**
         * Determine if the facet has already been applied.
         */
        ctrl.isFacetApplied = function(facetId, facetValue) {
            var facetQuery = new RegExp(facetId + '\\:"' + facetValue + '"', 'i');
            return !!search.query.match(facetQuery);
        };

        /**
         * Determine if the facet has already been applied.
         */
        ctrl.isSoFacetApplied = function(facetLabel) {
            var facetQuery = new RegExp('so_rna_type_name' + '\\:"' + facetLabel + '"', 'i');
            return !!search.query.match(facetQuery);
        };

        /**
         * Show subspecies in the TAXONOMY facet.
         */
        ctrl.showSubspecies = function() {
            ctrl.includeSubspecies = true;
            if (search.query.match(/TAXONOMY:"(\d+)"/)) {
                var addLineage = search.query.replace("RNA AND", "").replace(/TAXONOMY:"(\d+)"/, '(TAXONOMY:"$1" OR lineage_path:"$1")').trim()
                search.search(addLineage);
            }
        };

        /**
         * Hide subspecies in the TAXONOMY facet.
         */
        ctrl.hideSubspecies = function() {
            ctrl.includeSubspecies = false;
            if (search.query.match(/TAXONOMY:"(\d+)"/) && search.query.match(/lineage_path:"(\d+)"/)) {
                var removeLineage = search.query.replace(/\(TAXONOMY:"(\d+)"\s+OR\s+lineage_path:"\d+"\)/, 'TAXONOMY:"$1"').trim()
                search.search(removeLineage);
            }
        };

        /**
         * Clean up SO term labels.
         */
        ctrl.prettySoLabel = function(facetLabel) {
            var uppercase_exceptions = [
              'C_D_box_snoRNA',
              'H_ACA_box_snoRNA',
              'RNase_MRP_RNA',
              'RNase_P_RNA',
              'SRP_RNA',
              'U1_snRNA',
              'U11_snRNA',
              'U12_snRNA',
              'U2_snRNA',
              'U3_snoRNA',
              'U4_snRNA',
              'U4atac_snRNA',
              'U5_snRNA',
              'U6_snRNA',
              'U6atac_snRNA',
              'UTR_region',
              'Y_RNA',
              'RNA_thermometer',
            ];
            if (uppercase_exceptions.indexOf(facetLabel) === -1) {
                facetLabel = facetLabel.charAt(0).toLowerCase() + facetLabel.slice(1);
            }
            if (facetLabel === 'lnc_RNA') {
                facetLabel = 'lncRNA';
            } else if (facetLabel === 'pre_miRNA') {
                facetLabel = 'pre-miRNA';
            } else if (facetLabel === 'C_D_box_snoRNA') {
                facetLabel = 'C/D box snoRNA';
            } else if (facetLabel === 'H_ACA_box_snoRNA') {
                facetLabel = 'H/ACA box snoRNA';
            } else if (facetLabel === 'RRNA_5_8S') {
                facetLabel = 'rRNA 5.8S';
            } else {
                facetLabel = facetLabel.replace(/_/g, ' ');
            }
            return facetLabel;
        }

        /**
         * Run a search with a facet enabled.
         * The facet will be toggled on and off in the repeated calls with the same
         * parameters.
         */
        ctrl.facetSearch = function(facetId, facetValue) {
            var facet, newQuery = search.query;

            if (facetId === 'rna_type'){
                // register the use of the INSDC RNA Type facet
                gtag('event', 'text_search_facet_rna_type', {
                    'event_category': 'text_search',
                    'event_label':'rna_type',
                    'event_name':'text_search_facet_rna_type'
                });
            }

            if (facetId !== 'length') {
                facet = facetId + ':"' + facetValue + '"';

                if (ctrl.isFacetApplied(facetId, facetValue)) {
                    // remove facet in different contexts
                    if (ctrl.includeSubspecies && facetId === "TAXONOMY" && search.query.match(new RegExp('TAXONOMY', 'g')).length > 1) {
                        // remove subspecies
                        newQuery = newQuery.replace(/AND TAXONOMY:"(\d+)"/, '').trim();
                    } else if (ctrl.includeSubspecies && facetId === "TAXONOMY" && search.query.match(/lineage_path:"(\d+)"/)) {
                        // remove lineage_path
                        newQuery = newQuery.replace(/\(TAXONOMY:"(\d+)"\s+OR\s+lineage_path:"\d+"\)/, 'TAXONOMY:"$1"');
                    }
                    newQuery = newQuery.replace(new RegExp(' AND ' + facet + ' AND ', 'gi'), ' AND ');
                    newQuery = newQuery.replace(new RegExp(facet + ' AND ', 'gi'), '');
                    newQuery = newQuery.replace(new RegExp(' AND ' + facet, 'gi'), '');
                    newQuery = newQuery.replace(new RegExp(facet, 'gi'), '' || 'RNA');
                } else {
                    newQuery = search.query + ' AND ' + facet; // add new facet
                }

                if (ctrl.includeSubspecies && facetId === "TAXONOMY" && !search.query.match(/lineage_path:"(\d+)"/)) {
                    // add lineage_path
                    newQuery = newQuery.replace("RNA AND", "").replace(/TAXONOMY:"(\d+)"/, '(TAXONOMY:"$1" OR lineage_path:"$1")').trim()
                }
            } else {
                var lengthClause = 'length\\:\\[\\d+ TO \\d+\\]';

                // remove length clause in different contexts
                newQuery = newQuery.replace(new RegExp(' AND ' + lengthClause + ' AND '), ' AND ', 'i');
                newQuery = newQuery.replace(new RegExp(lengthClause + ' AND '), '', 'i');
                newQuery = newQuery.replace(new RegExp(' AND ' + lengthClause), '', 'i');
                newQuery = newQuery.replace(new RegExp(lengthClause), '', 'i') || 'RNA';

                // add length facet
                facet = facetId + ':' + facetValue;
                newQuery = newQuery + ' AND ' + facet; // add new facet
            }

            search.search(newQuery);
        };

        /**
         * Show/hide hierarchical subfacets.
         * Uses jQuery for simplicity.
         */
        ctrl.toggleSubFacets = function(label) {
          var $toggle = $('#toggle-' + label);
          $toggle.siblings('ul').toggle();
          $toggle.children('i').toggleClass('fa-minus fa-plus');
        }

        /**
         * Show/hide search facets to save screen space.
         * Uses jQuery for simplicity.
         * Activated only on mobile devices.
         */
        ctrl.toggleFacets = function() {
            var facets = $('.text-search-facets');
            facets.toggleClass('hidden-xs', !facets.hasClass('hidden-xs'));
            $('#toggle-facets').text(function(i, text) {
                 return text === "Show facets" ? "Hide facets" : "Show facets";
            });

            // if facets were hidden, this is required to render the slider
            $timeout(function () { $scope.$broadcast('rzSliderForceRender'); });

        };

        /**
         * Launch results export.
         * - submit export job
         * - open the results page in a new window.
         */
        ctrl.exportResults = function(format) {
            var queryParam = encodeURIComponent(`(${search.preprocessQuery(ctrl.search.query)})`);
            var apiUrl = `https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=${queryParam}&size=1000&sort=id&format=json`;

            var payload = {
                api_url: apiUrl,
                data_type: format
            };

            $http.post(routes.exportApp() + '/submit/', JSON.stringify(payload), {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }).then(
                function(response) {
                    ctrl.showExportError = false;
                    var task_id = response.data.task_id;
                    window.location.href = ctrl.routes.resultsPage() + '?job=' + task_id;
                },
                function(response) {
                    ctrl.showExportError = true;
                }
            );
        };

        /*
        ctrl.expert_db_logo = function(expert_db) {
            // expert_db can contain some html markup - strip it off, replace whitespaces with hyphens
            expert_db = expert_db.replace(/\s/g, '-').toLowerCase();

            return '/static/img/expert-db-logos/' + expert_db + '.png';
        };
        */

        /**
         * Sorts expertDbs so that starred dbs have priority over non-starred, otherwise, keeping lexicographical order.
         * @param v1 - plaintext db name
         * @param v2 - plaintext db name
         * @returns {number} - (-1 if v1 before v2) or (1 if v1 after v2)
         */
        ctrl.expertDbHasStarComparator = function(v1, v2) {
            if (ctrl.expertDbHasStar(v1.value.toLowerCase()) && !ctrl.expertDbHasStar(v2.value.toLowerCase())) return -1;
            else if (!ctrl.expertDbHasStar(v1.value.toLowerCase()) && ctrl.expertDbHasStar(v2.value.toLowerCase())) return 1;
            else
                return v1.value.toLowerCase() < v2.value.toLowerCase() ? -1 : 1;
        };

        /**
         * We assign a star only to those expert_dbs that have a curated tag and don't have automatic tag at the same time.
         * @param db {String} - name of expert_db as a key in expertDbsObject
         * @returns {boolean}
         */
        ctrl.expertDbHasStar = function(db) {
            return ctrl.expertDbsObject[db] && ctrl.expertDbsObject[db].tags.indexOf('curated') != -1 && ctrl.expertDbsObject[db].tags.indexOf('automatic') == -1;
        };

        /**
         * Given EBIsearch results, returns a field name and a highlighted text snippet, matching the query. This
         * helps explain the user, why this result was included into the results list.
         * @param fields {Object} - object of field as returned by search.search()
         * @returns {{highlight: String, fieldName: String}}
         */
        ctrl.highlight = function(fields) {
            try {
                var highlight;
                var verboseFieldName;
                var maxWeight = -1; // multiple fields can have highlights - pick the field with highest weight

                for (var fieldName in fields) {
                    if (fields.hasOwnProperty(fieldName) && ctrl.anyHighlightsInField(fields[fieldName])) { // description is quoted in hit's header, ignore it
                        if (search.config.fieldWeights[fieldName] > maxWeight) {

                            // get highlight string with match
                            var field = fields[fieldName];
                            for (var i = 0; i < field.length; i++) {
                                if (field[i].indexOf('text-search-highlights') !== -1) {
                                    highlight = field[i];
                                    break;
                                }
                            }

                            // assign the new weight and verboseFieldName
                            maxWeight = search.config.fieldWeights[fieldName];
                            verboseFieldName = search.config.fieldVerboseNames[fieldName];
                        }
                    }
                }

                // use human-readable fieldName
                return {highlight: highlight, fieldName: verboseFieldName};
            } catch (error) {
                return {highlight: '', fieldName: ''};
            }
        };

        /**
         * Are there any highlighted snippets in search results at all?
         */
        ctrl.anyHighlights = function(fields) {
            try {
                return Object.keys(fields).some(function(fieldName) {
                    return (fields.hasOwnProperty(fieldName) && ctrl.anyHighlightsInField(fields[fieldName]));
                });
            } catch (error) {
                return false;
            }
        };

        /**
         * Does the given field contain any highlighted text snippets?
         */
        ctrl.anyHighlightsInField = function(field) {
            try {
                if (!Array.isArray(field)) {
                    return false;
                }
                return field.some(function(el) { return el && el.indexOf('text-search-highlights') !== -1 });
            } catch (error) {
                return false;
            }
        };

        ctrl.getURS = function(urs_taxid) {
            try {
                return urs_taxid.replace(/_\d+/, '');
            } catch (error) {
                return urs_taxid || '';
            }
        }
    }]
};

angular.module('textSearch').component('textSearchResults', textSearchResults);