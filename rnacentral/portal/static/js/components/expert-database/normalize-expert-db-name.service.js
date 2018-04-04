angular.module("expertDatabase").service('normalizeExpertDbName', ['routes', function(routes) {
    return {
        nameToImageUrl: function(name) {
            if (name === "tmRNA Website") name = 'tmrna-website';
            else name = name.toLowerCase();

            return routes.expertDbLogo({ expertDbName: name });
        },
        labelToImageUrl: function(label) {
            return routes.expertDbLogo({ expertDbName: label });
        }
    };
}]);