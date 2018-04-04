angular.module("expertDatabase").service('normalizeExpertDbName', ['routes', function(routes) {
    return {
        /**
         * Given expertDb name, returns url of logo of that database
         * @param {string} name - human-readable db name, e.g. 'tmRNA Website'
         * @returns {string} url - url of corresponding database logo
         */
        nameToImageUrl: function(name) {
            if (name === "tmRNA Website") name = 'tmrna-website';
            else name = name.toLowerCase();

            return routes.expertDbLogo({ expertDbName: name });
        },

        /**
         * Given expertDb label, returns url of logo of that database.
         * @param {string} label - lower-kebab-case label, e.g. 'tmrna-website'
         * @returns {string} - url of corresponding database logo
         */
        labelToImageUrl: function(label) {
            return routes.expertDbLogo({ expertDbName: label });
        },

        /**
         * Given expertDb label, converts it to PK in DatabaseStats table.
         * @param {string} label - lower-kebab-case label, e.g. 'tmrna-website'
         * @returns {string} - uppercase, snake-case pk in DB, e.g. 'TMRNA_WEB'
         */
        labelToDb: function(label) {
            if (label === 'tmrna-website') return "TMRNA_WEB";
            else return label.toUpperCase();
        }
    };
}]);