var goflowReasoning = {
    bindings: {
        upi: '<',
        taxid: '<?'
    },
    controller: ['$http', '$interpolate', 'routes', '$timeout', '$element', '$compile', '$scope', function($http, $interpolate, routes, $timeout, $element, $compile, $scope) {
        var ctrl = this;
        
        // State for each reasoning text
        $scope.reasoningStates = {};
        
        // Toggle reasoning text
        $scope.toggleReasoning = function(index) {
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
        
        ctrl.$postLink = function() {
            $timeout(function() {
                initializeReasoningText();
            }, 100);
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
                    
                    // Create btn
                    var buttonHtml = '<span class="show-more-btn" ng-click="toggleReasoning(' + index + ')">{{reasoningStates[' + index + '].buttonText}}</span>';
                    var $showMoreBtn = $compile(buttonHtml)($scope);
                    
                    var $detailsElement = $textElement.closest('details');
                    if ($detailsElement.length > 0) {
                        $detailsElement.append($showMoreBtn);
                    } else {
                        $textElement.after($showMoreBtn);
                    }
                    
                    
                    // Check overflow
                    $timeout(function() {
                        var textEl = textElement;
                        var computedStyle = getComputedStyle(textEl);
                        var lineHeight = parseFloat(computedStyle.lineHeight);
                        
                        if (isNaN(lineHeight)) {
                            lineHeight = parseFloat(computedStyle.fontSize) * 1.2;
                        }
                        
                        var maxHeight = lineHeight * 3;
                        var actualHeight = textEl.scrollHeight;
                        
                      
                        
                        if (actualHeight <= maxHeight + 5) {
                            $scope.reasoningStates[index].visible = false;
                            $showMoreBtn.hide();
                        } else {
                            $scope.reasoningStates[index].visible = true;
                            $showMoreBtn.show();
                        }
                        
                        // Trigger digest cycle
                        $scope.$apply();
                    }, 50);
                }
            });
        }
    }],
    templateUrl: '/static/js/components/sequence/goflow-reasoning/goflow-reasoning.html' 
};

angular.module("rnaSequence").component("goflowReasoning", goflowReasoning);