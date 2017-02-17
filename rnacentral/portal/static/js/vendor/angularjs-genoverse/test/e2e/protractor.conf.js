// see config options here:
// https://github.com/angular/protractor/blob/master/lib/config.ts

exports.config = {
    specs: [
        '*.js'
    ],

    baseUrl: 'http://localhost:8000/',

    allScriptsTimeout: 10000,

    capabilities: {
        'browserName': 'chrome'
    },

    framework: 'jasmine',

    jasmineNodeOpts: {
        defaultTimeoutIntervals: 30000,
        showColors: true,
        isVerbose: true,
        includeStackTree: true
    }
}
