angular.module('rnacentralApp', [
    'ngAnimate',
    'ngSanitize',
    'angular.filter',
    'ui.bootstrap',
    'chieffancypants.loadingBar',
    'rzModule',
    'underscore',

    'Genoverse',
    'rnaSequence',
    'textSearch',
    'expertDatabase',
    'useCases',
    'homepage'
])
.config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    // hide spinning wheel
    cfpLoadingBarProvider.includeSpinner = false;
}])
.config(['$locationProvider', function($locationProvider) {
    /**
     * Turn on html5mode only in modern browsers because
     * in the older ones html5mode rewrites urls with Hangbangs
     * which break normal Django pages.
     *
     * With html5mode off IE lt 10 will be able to navigate the site
     * but won't be able to open deep links to Angular pages
     * (for example, a link to a search result won't load in IE 9).
     *
     * Even in newer browsers we shall disable rewriteLinks, unless
     * we want to create a client-side router.
     */
    if (window.history && window.history.pushState) {
        $locationProvider.html5Mode({enabled: true, rewriteLinks: false});
    }

    // IE10- don't have window.location.origin, let's shim it
    if (!window.location.origin) {
         window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
    }
}])
.run(['$rootScope', '$window', '$location', function($rootScope, $window, $location) {
    /**
     * This is an ugly hack to catch back/forward buttons pressed in the browser.
     *
     * When url is changed in a usual way (not with back/forward button),
     *  $locationChangeSuccess event fires after $watch callback.
     * But when url is changed using back/forward button or history.back() api,
     * $locationChangeSuccess event fires before $watch callback.
     *
     * Taken from here:
     * https://stackoverflow.com/questions/15813850/how-to-detect-browser-back-button-click-event-using-angular
     */

    $rootScope.$on('$locationChangeSuccess', function() {
        $rootScope.actualLocation = $location.absUrl();
    });

    $rootScope.$watch(function () {return $location.absUrl()}, function (newLocation, oldLocation) {
        if($rootScope.actualLocation === newLocation) {
            $window.location.href = $rootScope.actualLocation;
        }
    })
}])
.run([function() {
    /**
    * Function that tracks a click on an outbound link in Analytics.
    * This function takes a valid URL string as an argument, and uses that URL string
    * as the event label. Setting the transport method to 'beacon' lets the hit be sent
    * using 'navigator.sendBeacon' in browser that support it.
    */
    var trackOutboundLink = function(url) {
       ga('send', 'event', 'outbound', 'click', url, {
         'transport': 'beacon',
         // 'hitCallback': function(){ document.location = url; } - use this callback, if you decide to prevent default link bevaviour
       });
    };

    var trackOutboundLinkHostname = function(url) {
        var tmp = document.createElement('a');
        tmp.href = url;

        ga('send', 'event', 'outbound', 'domain', tmp.hostname, {
            'transport': 'beacon'
        });
    };

    /**
     * Track outbound traffic with Google Analytics.
     *
     * NOTE: we delegate events to body in order to handle clicks on links created by angular dynamically
     * NOTE: ng-clicks resulting in outbound traffic won't be reported!
     */
    $('body').on('click', 'a[href^="http://"]:not([href^="http://rnacentral.org"])', function (event) {
        trackOutboundLink($(event.target).attr('href'));
        trackOutboundLinkHostname($(event.target).attr('href'));
    }).on('click', 'a[href^="https://"]:not([href^="https://rnacentral.org"])', function (event) {
        trackOutboundLink($(event.target).attr('href'));
        trackOutboundLinkHostname($(event.target).attr('href'));
    });
}])
.run(['$anchorScroll', function ($anchorScroll) {
    /**
     * This will make anchorScroll scroll to the div minus 50px
     */
   $anchorScroll.yOffset = 50;
}]);
