/**
 * Relationships component for displaying RNA molecular relationships
 * Usage: <relationships upi="upi" taxid="taxid"></relationships>
 */

(function() {
    'use strict';

    // Prevent multiple registrations
    if (window.relationshipsComponentRegistered) {
        return;
    }

    // Wait for Angular to be available
    function initializeComponent() {
        if (typeof angular === 'undefined') {
            setTimeout(initializeComponent, 100);
            return;
        }

        var relationshipsController = function($scope, $http) {
            var ctrl = this;
            
            ctrl.relationships = [];
            ctrl.loading = false;
            ctrl.error = false;
            ctrl.currentPage = 1;
            ctrl.totalCount = 0;
            ctrl.pageSize = 20;
            ctrl.showPagination = false;

            ctrl.loadRelationships = function(page, append) {
                if (!ctrl.taxid || !ctrl.upi) {
                    return;
                }
                
                page = page || 1;
                append = append || false;
                ctrl.loading = true;
                ctrl.error = false;
                
                var relationshipsUrl = '/api/v1/rna/' + ctrl.upi + '/relationships/' + ctrl.taxid + '?page=' + page;
                
                $http.get(relationshipsUrl)
                    .then(function(response) {
                        // API returns paginated format
                        var newResults = response.data.results || [];
                        if (append) {
                            ctrl.relationships = ctrl.relationships.concat(newResults);
                        } else {
                            ctrl.relationships = newResults;
                        }
                        ctrl.totalCount = response.data.count || 0;
                        ctrl.currentPage = page;
                        ctrl.showPagination = ctrl.totalCount > ctrl.pageSize;
                        ctrl.loading = false;
                    })
                    .catch(function(error) {
                        ctrl.error = true;
                        ctrl.loading = false;
                        if (!append) {
                            ctrl.relationships = [];
                            ctrl.totalCount = 0;
                            ctrl.showPagination = false;
                        }
                    });
            };

            ctrl.goToPage = function(page) {
                if (page >= 1 && page <= ctrl.getTotalPages()) {
                    ctrl.loadRelationships(page);
                }
            };

            ctrl.getTotalPages = function() {
                return Math.ceil(ctrl.totalCount / ctrl.pageSize);
            };

            ctrl.getPageNumbers = function() {
                var totalPages = ctrl.getTotalPages();
                var currentPage = ctrl.currentPage;
                var pages = [];
                var start = Math.max(1, currentPage - 2);
                var end = Math.min(totalPages, currentPage + 2);
                
                for (var i = start; i <= end; i++) {
                    pages.push(i);
                }
                return pages;
            };

            ctrl.getStartRecord = function() {
                return ((ctrl.currentPage - 1) * ctrl.pageSize) + 1;
            };

            ctrl.getEndRecord = function() {
                return Math.min(ctrl.currentPage * ctrl.pageSize, ctrl.totalCount);
            };

            ctrl.loadMore = function() {
                if (ctrl.relationships.length < ctrl.totalCount && !ctrl.loading) {
                    ctrl.loadRelationships(ctrl.currentPage + 1, true);
                }
            };

            // Watch for changes in upi or taxid
            ctrl.$onChanges = function(changes) {
                if (ctrl.upi && ctrl.taxid) {
                    ctrl.loadRelationships();
                }
            };

            // Also try to load on init in case values are already set
            ctrl.$onInit = function() {
                if (ctrl.upi && ctrl.taxid) {
                    ctrl.loadRelationships();
                }
            };
        };

        relationshipsController.$inject = ['$scope', '$http'];

        var relationshipsComponent = {
            bindings: {
                upi: '<',
                taxid: '<'
            },
            controller: relationshipsController,
            controllerAs: 'ctrl',
            template: `
                <div ng-if="ctrl.loading">
                    <i class="fa fa-spinner fa-spin fa-2x"></i> Loading relationships...
                </div>
                
                <div ng-if="ctrl.error" class="alert alert-danger">
                    <i class="fa fa-exclamation-triangle"></i> Error loading relationship data.
                </div>
                
                <div ng-if="!ctrl.loading && !ctrl.error && ctrl.relationships.length > 0">
                    <p class="text-muted">
                        <i class="fa fa-info-circle"></i>
                        This RNA sequence has {{ctrl.totalCount}} molecular relationships and interactions <a href="https://rna-kg.biodata.di.unimi.it/index.html" target="_blank">according to RNA-KG</a>.
                        <span ng-if="ctrl.showPagination">Showing {{ctrl.getStartRecord()}} - {{ctrl.getEndRecord()}} of {{ctrl.totalCount}} relationships.</span>
                    </p>
                    
                    <div class="table-responsive">
                        <table class="table table-striped table-bordered">
                            <thead>
                                <tr>
                                    <th>Relationship Type</th>
                                    <th>Target</th>
                                    <th>Target Description</th>
                                    <th>Source</th>
                                    <th>Method</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr ng-repeat="rel in ctrl.relationships">
                                    <td>
                                        <span class="label label-info">
                                            {{ rel.relationship_type || "Unknown" }}
                                        </span>
                                    </td>
                                    <td>
                                        <a ng-if="rel.node_uri" href="{{ rel.node_uri }}" target="_blank" title="View external resource">
                                            {{ rel.node_properties.Label || rel.node_id || "Unknown" }}
                                        </a>
                                        <span ng-if="!rel.node_uri">
                                            {{ rel.node_properties.Label || rel.node_id || "Unknown" }}
                                        </span>
                                    </td>
                                    <td>
                                        <small class="text-muted">
                                            {{ (rel.node_properties.Description || "No description available") | limitTo:100 }}<span ng-if="rel.node_properties.Description && rel.node_properties.Description.length > 100">...</span>
                                        </small>
                                    </td>
                                    <td>
                                        <span ng-if="rel.relationship_properties.Source">
                                            <span class="badge" ng-repeat="source in rel.relationship_properties.Source">{{ source }}</span>
                                        </span>
                                        <span ng-if="!rel.relationship_properties.Source" class="text-muted">Not specified</span>
                                    </td>
                                    <td>
                                        <small ng-if="rel.relationship_properties.Method">
                                            <span ng-repeat="method in rel.relationship_properties.Method">{{ method }}<span ng-if="!$last">, </span></span>
                                        </small>
                                        <span ng-if="!rel.relationship_properties.Method" class="text-muted">-</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Pagination Controls -->
                    <div ng-if="ctrl.showPagination" class="text-center" style="margin-top: 20px;">
                        <nav aria-label="Relationships pagination">
                            <ul class="pagination pagination-sm">
                                <li ng-class="{disabled: ctrl.currentPage <= 1}">
                                    <a href="#" ng-click="ctrl.currentPage > 1 && ctrl.goToPage(1); $event.preventDefault()" aria-label="First">
                                        <span aria-hidden="true">&laquo;&laquo;</span>
                                    </a>
                                </li>
                                <li ng-class="{disabled: ctrl.currentPage <= 1}">
                                    <a href="#" ng-click="ctrl.currentPage > 1 && ctrl.goToPage(ctrl.currentPage - 1); $event.preventDefault()" aria-label="Previous">
                                        <span aria-hidden="true">&laquo;</span>
                                    </a>
                                </li>
                                <li ng-repeat="page in ctrl.getPageNumbers()" ng-class="{active: page === ctrl.currentPage}">
                                    <a href="#" ng-click="ctrl.goToPage(page); $event.preventDefault()">{{ page }}</a>
                                </li>
                                <li ng-class="{disabled: ctrl.currentPage >= ctrl.getTotalPages()}">
                                    <a href="#" ng-click="ctrl.currentPage < ctrl.getTotalPages() && ctrl.goToPage(ctrl.currentPage + 1); $event.preventDefault()" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                </li>
                                <li ng-class="{disabled: ctrl.currentPage >= ctrl.getTotalPages()}">
                                    <a href="#" ng-click="ctrl.currentPage < ctrl.getTotalPages() && ctrl.goToPage(ctrl.getTotalPages()); $event.preventDefault()" aria-label="Last">
                                        <span aria-hidden="true">&raquo;&raquo;</span>
                                    </a>
                                </li>
                            </ul>
                        </nav>
                        <p class="text-muted small">
                            Page {{ctrl.currentPage}} of {{ctrl.getTotalPages()}} 
                            <span ng-if="ctrl.totalCount > 0">({{ctrl.totalCount}} total relationships)</span>
                        </p>
                    </div>
                </div>
                
                <div ng-if="!ctrl.loading && !ctrl.error && (!ctrl.relationships || ctrl.relationships.length === 0)" class="alert alert-info">
                    <i class="fa fa-info-circle"></i>
                    No relationship data is currently available for this RNA sequence.
                </div>
            `
        };

        // Check if the rnaSequence module exists and register component
        try {
            var module = angular.module('rnaSequence');
            
            // Check if component is already registered
            try {
                module._invokeQueue.forEach(function(item) {
                    if (item[1] === 'component' && item[2][0] === 'relationships') {
                        throw new Error('Component already registered');
                    }
                });
            } catch (e) {
                if (e.message === 'Component already registered') {
                    window.relationshipsComponentRegistered = true;
                    return;
                }
            }
            
            module.component('relationships', relationshipsComponent);
            window.relationshipsComponentRegistered = true;
            
        } catch (e) {
            setTimeout(function() {
                try {
                    angular.module('rnaSequence').component('relationships', relationshipsComponent);
                    window.relationshipsComponentRegistered = true;
                } catch (e2) {
                    console.error('Failed to register relationships component:', e2);
                }
            }, 500);
        }
    }

    // Start the initialization process
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeComponent);
    } else {
        initializeComponent();
    }

})();