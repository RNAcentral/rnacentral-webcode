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

            ctrl.loadRelationships = function() {
                if (!ctrl.taxid || !ctrl.upi) {
                    return;
                }
                
                ctrl.loading = true;
                ctrl.error = false;
                
                var relationshipsUrl = '/api/v1/rna/' + ctrl.upi + '/relationships/' + ctrl.taxid;
                
                $http.get(relationshipsUrl)
                    .then(function(response) {
                        // API returns {count: X, results: [...]} format, not {relationships: [...]}
                        ctrl.relationships = response.data.results || [];
                        ctrl.loading = false;
                    })
                    .catch(function(error) {
                        ctrl.error = true;
                        ctrl.loading = false;
                        ctrl.relationships = [];
                    });
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
                        This RNA sequence has {{ctrl.relationships.length}} molecular relationships and interactions <a href="https://rna-kg.biodata.di.unimi.it/index.html" target="_blank">according to RNA-KG</a>.
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
                    
                    <div class="text-muted small">
                        <p>
                            <i class="fa fa-info-circle"></i>
                            Relationship data is aggregated from multiple sources including experimental evidence and computational predictions.
                            Click on external links to view detailed information about specific targets or publications.
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