angular.module("rnacentralApp").service('normalizeExpertDbName', ['routes', function() {
    return {
        nameToImageUrl: function(name) {
            if (name === "tmRNA Website") name = 'tmrna-website';
            else name = name.toLowerCase();

            return routes.expertDbLogo({ name: name });
        },
        labelToImageUrl: function(label) {
            return routes.expertDbLogo({ expertDbName: label });
        }
    };
}]);