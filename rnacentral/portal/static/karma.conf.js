// Karma configuration
// Generated on Sun Mar 04 2018 16:50:46 GMT+0000 (GMT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'node_modules/angular/angular.js',
      'node_modules/angular-animate/angular-animate.js',
      'node_modules/angular-sanitize/angular-sanitize.js',
      'node_modules/angular-filter/dist/angular-filter.js',
      'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls.js',
      'node_modules/angular-loading-bar/build/loading-bar.js',
      'node_modules/angularjs-slider/dist/rzslider.js',
      'node_modules/underscore/underscore.js',
      'js/components/underscore.module.js',

      'node_modules/angular-mocks/angular-mocks.js',

      // rnacentralApp module
      'js/app.js',

      'js/components/main-content.controller.js',
      'js/components/routes.service.js',

      'js/components/sequence-search/nhmmer.sequence.search.js',

      // Genoverse module
      'node_modules/angularjs-genoverse/lib/Genoverse/dist/js/genoverse.min.nodeps.js',
      'node_modules/angularjs-genoverse/dist/angularjs-genoverse.all.js',

      // genomeBrowser module
      'js/components/genome-browser/genoverse-utils.service.js',
      'js/components/genome-browser/genome-browser.controller.js',

      // textSearch module
      'js/components/text-search/text-search.module.js',
      'js/components/text-search/text-search.service.js',
      'js/components/text-search/capitalize-first.filter.js',
      'js/components/text-search/export-results.search.js',
      'js/components/text-search/plaintext.filter.js',
      'js/components/text-search/sanitize.filter.js',
      'js/components/text-search/text-search.service.js',
      'js/components/text-search/underscore-to-spaces.filter.js',

      'js/components/text-search/text-search-bar/text-search-bar.component.js',

      'js/components/text-search/text-search-results/text-search-results.component.js',

      // rnaSequence module
      'js/components/sequence/sequence.module.js',
      'js/components/sequence/abstract/abstract.component.js',
      'js/components/sequence/publications/publication.component.js',
      'js/components/sequence/publications/publications.component.js',
      'js/components/sequence/taxonomy/taxonomy.component.js',
      'js/components/sequence/xrefs/xrefs.component.js',
      'js/components/sequence/xrefs/xref-publications/xref-publications.component.js',
      'js/components/sequence/2d/2d.component.js',

      // expertDatabase module
      'js/components/expert-database/expert-database.module.js',
      'js/components/expert-database/expert-database-top.component.js',
      'js/components/expert-database/expert-database-left.component.js',
      'js/components/expert-database/expert-database-right.component.js',
      'js/components/expert-database/normalize-expert-db-name.service.js',
      'js/components/expert-database/normalize-expert-db-name.service.spec.js',

      // useCases module
      'js/components/use-cases/use-cases.module.js',

      // homepage module
      'js/components/homepage/homepage.module.js'
    ],


    // list of files / patterns to exclude
    exclude: [
      'node_modules'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: false,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Firefox', 'Chrome', 'Safari'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity
  })
};
