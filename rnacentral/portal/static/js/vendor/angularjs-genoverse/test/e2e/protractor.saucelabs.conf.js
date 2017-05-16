// See:
// https://github.com/angular/protractor/blob/master/lib/config.ts
// https://gist.github.com/spenoir/e27dd5a4cb5cdd159ed9
// https://www.ignoredbydinosaurs.com/posts/257-angular-protractor-tests-and-sauce-connect-config
// https://github.com/esvit/ng-table/blob/master/e2e/protractor-travis.config.js
// https://marmelab.com/blog/2014/12/12/protractor-in-ng-admin-angularjs-app.html

/**
 * Updates the input config with a tunnel identifier, if we're running this on Travis CI.
 *
 * @param {Object} config - normal capabilities property of protractor config
 * @returns {Object} - config (same object!), updated with tunnel identifier,
 *  if we're running this on travis instances with TRAVIS_JOB_NUMBER available
 */
function capabilities(config) {
    if (process.env.TRAVIS_JOB_NUMBER) config['tunnel-identifier'] = process.env.TRAVIS_JOB_NUMBER;
    return config;
}

exports.config = {
    specs: [
        '*.spec.js'
    ],

    baseUrl: 'http://localhost:8000/',

    sauceUser: process.env.SAUCE_USERNAME,
    sauceKey: process.env.SAUCE_ACCESS_KEY,

    allScriptsTimeout: 10000,

    getPageTimeout: 10000,

    multiCapabilities: [
        capabilities({
            'name': 'Linux/Chrome',
            'browserName': 'chrome'
        }),
        capabilities({
            'name': 'Linux/Firefox',
            'browserName': 'firefox'
        }),
        // capabilities({
        //     'name': 'Win7/Firefox',
        //     'browserName': 'firefox',
        //     'platform': 'Windows 7'
        // }),
        capabilities({
            'name': 'Win7/Chrome',
            'browserName': 'chrome',
            'platform': 'Windows 7'
        }),
        // capabilities({
        //     'name': 'Win7/IE9',
        //     'browserName': 'internet explorer',
        //     'platform': 'Windows 7',
        //     'version': 9
        // }),
        // capabilities({
        //     'name': 'Win8/IE10',
        //     'browserName': 'internet explorer',
        //     'platform': 'Windows 8',
        //     'version': 10
        // }),
        // capabilities({
        //     'name': 'Win8.1/IE11',
        //     'browserName': 'internet explorer',
        //     'platform': 'Windows 8.1',
        //     'version': 11
        // }),
        capabilities({
            'name': 'Win10/Edge',
            'browserName': 'microsoftedge',
            'platform': 'Windows 10',
            'version': '13.10586'
        })
        // capabilities({
        //     'name': 'Mac/Safari 8',
        //     'browserName': 'safari',
        //     'platform': 'OS X 10.10',
        //     'version': 8
        // }),
        // capabilities({
        //     'name': 'Mac/Safari 9',
        //     'browserName': 'safari',
        //     'platform': 'OS X 10.11',
        //     'version': 9
        // }),
        // capabilities({
        //     'name': 'Mac/Safari 10',
        //     'browserName': 'safari',
        //     'platform': 'OS X 10.12',
        //     'version': 10
        // })
    ],

    framework: 'jasmine',

    jasmineNodeOpts: {
        defaultTimeoutInterval: 30000,
        showColors: true,
        includeStackTrace: true
    }
};
