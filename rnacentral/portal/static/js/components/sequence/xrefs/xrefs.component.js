var xrefs = {
    bindings: {
        upi: '<',
        timeout: '<?',
        page: '<?',
        pageSize: '<?',
        taxid: '<?',
        onActivatePublications: '&',
        onCreateModificationsFeature: '&',
        onActivateGenomeBrowser: '&',
        onScrollToGenomeBrowser: '&'
    },
    controller: ['routes', '$http', '$interpolate', '$timeout', '$filter', function(routes, $http, $interpolate, $timeout, $filter) {
        var ctrl = this;

        /**
         * Given unique rna page url, extracts urs from it.
         */
        ctrl.url2urs = function(url) {
            // if url ends with a slash, strip it
            if (url.slice(-1) === '/') url = url.slice(-1);

            // url might have a taxid, so let's just take the url fragment after 'rna'
            var breadcrumbs = url.split('/');
            for (var urlFragment = 0; urlFragment < breadcrumbs.length; urlFragment++) {
                if (breadcrumbs[urlFragment] === 'rna') return breadcrumbs[urlFragment + 1];
            }
        };

        /**
         * Display 3D structure using MolStar
         */
        ctrl.show3D = function($event, pdbId, chainId, entityId) {
            // prevent errors by disablign the button so it cannot be clicked again
            $event.target.classList.add('disabled');
            // show spinner
            var label = document.getElementById('label-' + pdbId + '-' + chainId);
            label.style.display = 'inline';
            // launch MolStar
            var viewerInstance = new PDBeMolstarPlugin();
            var options = {
                moleculeId: pdbId.toLowerCase(),
            };
            var viewerContainer = document.getElementById('molstarViewer-' + pdbId + '-' + chainId);
            var struct_asym_id = chainId; // fallback to chainId in case struct_asym_id cannot be found
            jQuery(viewerContainer).slideDown('fast', function(){
                viewerInstance.render(viewerContainer, options);
                viewerInstance.canvas.toggleControls(false);
                // get struct_asym_id (chainId is not enough)
                // https://www.ebi.ac.uk/pdbe/api/pdb/entry/residue_listing/3J9M/chain/AA
                jQuery.get('https://www.ebi.ac.uk/pdbe/api/pdb/entry/residue_listing/' + pdbId + '/chain/' + chainId, function(data) {
                    var molecules = data[pdbId.toLowerCase()]['molecules'];
                    for (i = 0, lenMolecules = molecules.length; i < lenMolecules; i++) {
                        if (molecules[i]['entity_id'] == entityId) {
                            var chains = molecules[i]['chains'];
                            for (j = 0, lenChains = chains.length; j < lenChains; j++) {
                                if (chains[j]['chain_id'] === chainId) {
                                    struct_asym_id = chains[j]['struct_asym_id'];
                                }
                            }
                        }
                    }
                }, 'json');
                viewerInstance.events.loadComplete.subscribe(function (e) {
                    viewerInstance.visual.selection([{struct_asym_id: struct_asym_id, color:{r:68,g:143,b:182}}], {r:255,g:255,b:255}, true);
                    // update label
                    label.innerHTML = 'Chain ' + chainId + ':' + struct_asym_id + ' is shown in blue';
      	        });
            });
        }

        ctrl.onPageSizeChanged = function(newPageSize, oldPageSize) {
            oldPageSize = parseInt(oldPageSize);

            // re-calculate page, taking new pageSize into account
            ctrl.page = Math.floor(((ctrl.page - 1) * oldPageSize) / newPageSize) + 1;
            ctrl.pageSize = newPageSize;
            ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);

            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'client') {
                ctrl.displayedXrefs = ctrl.xrefs.slice((ctrl.page - 1) * ctrl.pageSize, ctrl.page * ctrl.pageSize);
            }
            else if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            ctrl.status = 'loading';
            $http.get(ctrl.dataEndpoint, {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.displayedXrefs = ctrl.orderXrefs(response.data.results);
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);

                    // for all new xrefs with modifications, create corresponding features in feature viewer
                    for (var i = 0; i < ctrl.displayedXrefs.length; i++) {
                        if (ctrl.displayedXrefs[i].modifications.length > 0) {
                            ctrl.onCreateModificationsFeature({modifications: ctrl.displayedXrefs[i].modifications, accession: ctrl.displayedXrefs[i].accession.id});
                        }
                    }
                },
                function(response) {
                    ctrl.status = 'error';
                }
            )
        };

        /**
         * Custom logic for prioritising xrefs.
         *
         * @param {Array} results - e.g. [{ database: "Ensembl", is_expert_db: false, accession: {...} ... }, ...]
         * @returns {Array} - sorted copy of results
         */
        ctrl.orderXrefs = function(results) {
            new_results = [];
            to_append = [];
            for (var x = 0; x < results.length; x++) {
              if (results[x].database == "GeneCards") {
                  to_append.push(results[x]);
              } else {
                  new_results.push(results[x]);
              }
            }
            new_results = new_results.concat(to_append);
            return new_results;
        };

        /**
         * Genome browser breaks with chromosomes like 'GL00220.1' (e.g. localhost:8000/rna/URS000075A823/9606)
         * Don't show "View genomic location" button, if that's the case.
         */
        ctrl.chromosomeIsScaffold = function(chromosome) {
            return !!chromosome.match(/\S+\.\S/);
        };

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.page = ctrl.page || 1;  // human-readable number of page to show, in range of (1, n)
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'client';  // load all Xrefs at once and paginate Xrefs table on client-side, or if too slow, fallback to loading'em page-by-page from server
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;  // if (time of response) > timeout, paginate on server side

            ctrl.status = 'loading';  // {'loading', 'error' or 'success'} - display spinner, error message or xrefs table

            // Request xrefs from server (with taxid, if necessary)
            if (ctrl.taxid) ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs/{{taxid}}')({upi: ctrl.upi, taxid: ctrl.taxid});
            else ctrl.dataEndpoint = $interpolate('/api/v1/rna/{{upi}}/xrefs')({upi: ctrl.upi});

            $http.get(ctrl.dataEndpoint, { timeout: ctrl.timeout, params: { page: 1, page_size: 1000000000000 } }).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.xrefs = ctrl.orderXrefs(response.data.results);
                    ctrl.displayedXrefs = ctrl.xrefs.slice(0, ctrl.pageSize);
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);

                    // for all new xrefs with modifications, create corresponding features in feature viewer
                    for (var i = 0; i < ctrl.xrefs.length; i++) {
                        if (ctrl.xrefs[i].modifications.length > 0) {
                            ctrl.onCreateModificationsFeature({ modifications: ctrl.xrefs[i].modifications, accession: ctrl.xrefs[i].accession.id });
                        }
                    }
                },
                function(response) {
                    // if it took server too long to respond and request was aborted by timeout
                    // send a paginated request instead and fallback to server-side processing
                    if (response.status === -1) {  // for timeout response.status is -1
                        ctrl.paginateOn = 'server';
                        ctrl.getPageFromServerSide();
                    }
                    else {
                        ctrl.status = 'error';
                    }
                }
            );
        }
    }],
    templateUrl: '/static/js/components/sequence/xrefs/xrefs.html'
};

angular.module("rnaSequence").component("xrefs", xrefs);
