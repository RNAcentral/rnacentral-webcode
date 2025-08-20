var goflowReasoning = {
    bindings: {
        upi: '<',
        taxid: '<?',
        results: '<?' // Add binding for results data
    },
    controller: ['$http', '$interpolate', 'routes', '$timeout', '$element', '$compile', '$scope', function($http, $interpolate, routes, $timeout, $element, $compile, $scope) {
        var ctrl = this;
        
        // State for each reasoning text
        $scope.reasoningStates = {};
        $scope.isLoading = false;
        $scope.error = null;
        
        // Initialize with passed data or fetch if not provided
        ctrl.$onInit = function() {
            if (ctrl.results) {
                $scope.goflowData = ctrl.results;

                 // Parse annotation if it's a string
                if (typeof $scope.goflowData.annotation === 'string') {
                try {
                    $scope.goflowData.annotation = JSON.parse($scope.goflowData.annotation);
                } catch (e) {
                    console.error('Failed to parse annotation JSON:', e);
                }
                }
            } else if (ctrl.upi && ctrl.taxid) {
                fetchGoflowData();
            }
        };
        
        function fetchGoflowData() {
            if (!ctrl.upi || !ctrl.taxid) return;
            
            $scope.isLoading = true;
            $scope.error = null;
            
            var url = routes.goflow_data_url({
                upi: ctrl.upi,
                taxid: ctrl.taxid
            });
            
            $http.get(url).then(
                function(response) {
                    $scope.goflowData = response.data;
                    $scope.isLoading = false;

                    // Initialize reasoning text after data loads
                    $timeout(function() {
                        initializeReasoningText();
                    }, 100);
                },
                function(error) {
                    $scope.error = 'Failed to load GoFlow data';
                    $scope.isLoading = false;
                    console.error('GoFlow data fetch error:', error);
                }
            );
        }
        
        // Toggle reasoning text
        $scope.toggleReasoning = function(index) {
            if (!$scope.reasoningStates[index]) return;
            
            var textElement = $element.find('.reasoning-text').eq(index);
            
            if ($scope.reasoningStates[index].clamped) {
                textElement.removeClass('clamped');
                $scope.reasoningStates[index].clamped = false;
                $scope.reasoningStates[index].buttonText = 'Show less';
            } else {
                textElement.addClass('clamped');
                $scope.reasoningStates[index].clamped = true;
                $scope.reasoningStates[index].buttonText = 'Show more';
            }
        };
        
        // Get result icon based on value
        $scope.getResultIcon = function(result) {
            if (result === true || result === 'yes') return '✓';
            if (result === false || result === 'no') return '✗';
            return '−'; // unknown/null
        };
        
        // Get result class based on value
        $scope.getResultClass = function(result) {
            if (result === true || result === 'yes') return 'yes';
            if (result === false || result === 'no') return 'no';
            return 'unknown';
        };
        
        // Format field names for display
        $scope.formatFieldName = function(fieldName) {
            return fieldName.replace(/_/g, ' ')
                           .replace(/\b\w/g, function(l) { return l.toUpperCase(); });
        };
        
        // Check if field should be displayed
        $scope.shouldDisplayField = function(fieldName) {
            var excludeFields = ['id', 'urs_taxid', 'rna_id'];
            return excludeFields.indexOf(fieldName) === -1;
        };
        
        ctrl.$postLink = function() {
            // If data was passed in, initialize reasoning text
            if (ctrl.results) {
                $timeout(function() {
                    initializeReasoningText();
                }, 100);
            }
        };
        
        function initializeReasoningText() {
            var reasoningTexts = $element.find('.reasoning-text');
            
            reasoningTexts.each(function(index, textElement) {
                var $textElement = angular.element(textElement);
                var textContent = $textElement.text().trim();
                
                if (textContent.length > 150) {
                    $textElement.addClass('clamped');
                    
                    // Init state
                    $scope.reasoningStates[index] = {
                        clamped: true,
                        buttonText: 'Show more',
                        visible: false
                    };
                    
                    // Show more/less btn
                    var buttonHtml = '<span class="show-more-btn" ng-click="toggleReasoning(' + index + ')">{{reasoningStates[' + index + '].buttonText}}</span>';
                    var $showMoreBtn = $compile(buttonHtml)($scope);
                    
                    var $detailsElement = $textElement.closest('details');
                    if ($detailsElement.length > 0) {
                        $detailsElement.append($showMoreBtn);
                    } else {
                        $textElement.after($showMoreBtn);
                    }
                    
                    // Check if content actually overflows
                    $timeout(function() {
                        var textEl = textElement;
                        var computedStyle = getComputedStyle(textEl);
                        var lineHeight = parseFloat(computedStyle.lineHeight);
                        
                        if (isNaN(lineHeight)) {
                            lineHeight = parseFloat(computedStyle.fontSize) * 1.2;
                        }
                        
                        var maxHeight = lineHeight * 4; // Clamp to 4 lines
                        var actualHeight = textEl.scrollHeight;
                        
                        if (actualHeight <= maxHeight + 5) {
                            $scope.reasoningStates[index].visible = false;
                            $showMoreBtn.hide();
                        } else {
                            $scope.reasoningStates[index].visible = true;
                            $showMoreBtn.show();
                        }
                        
                        // Trigger digest cycle
                        if (!$scope.$$phase) {
                            $scope.$apply();
                        }
                    }, 50);
                }
            });
        }
        
        // Check if value exists and is not empty
        $scope.hasValue = function(value) {
            return value && value !== '' && value !== null && value !== undefined;
        };
        
    }],
    templateUrl: '/static/js/components/sequence/goflow-reasoning/goflow-reasoning.html' 
};

angular.module("rnaSequence").component("goflowReasoning", goflowReasoning)
.filter('markdown', ['$sce', function($sce) {
    return function(input) {
      if (input) {
        return $sce.trustAsHtml(marked.parse(input));
      }
      return '';
    };
  }]);