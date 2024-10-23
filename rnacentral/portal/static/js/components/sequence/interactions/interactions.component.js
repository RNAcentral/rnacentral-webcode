var interactions = {
    bindings: {
        upi: '=',
        taxid: '=',
        timeout: '<?',
        page: '<?',
        pageSize: '<?'
    },

    controller: ['$http', 'routes', '$location', function($http, routes, $location) {
        var ctrl = this;

        ctrl.$onInit = function() {
            // set defaults for optional parameters, if not given
            ctrl.page = ctrl.page || 1;  // human-readable number of page to show, in range of (1, n)
            ctrl.pageSize = ctrl.pageSize || 5;
            ctrl.paginateOn = 'server';  // use server-side pagination
            ctrl.timeout = parseInt(ctrl.timeout) || 5000;  // timeout value
            ctrl.status = 'loading';  // {'loading', 'error' or 'success'} - display spinner, error message or xrefs table

            ctrl.getPageFromServerSide();
        };

        ctrl.onPageSizeChanged = function(newPageSize, oldPageSize) {
            oldPageSize = parseInt(oldPageSize);

            // re-calculate page, taking new pageSize into account
            ctrl.page = Math.floor(((ctrl.page - 1) * oldPageSize) / newPageSize) + 1;
            ctrl.pageSize = newPageSize;
            ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);

            if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.onPageChanged = function(page) {
            ctrl.page = page;
            if (ctrl.paginateOn === 'server') {
                ctrl.getPageFromServerSide();
            }
        };

        ctrl.getPageFromServerSide = function() {
            ctrl.status = 'loading';
            $http.get(routes.apiInteractionsView({ upi: ctrl.upi, taxid: ctrl.taxid }), {params: { page: ctrl.page, page_size: ctrl.pageSize }}).then(
                function(response) {
                    ctrl.status = 'success';
                    ctrl.displayedInteractions = response.data.results;
                    ctrl.total = response.data.count;
                    ctrl.pages = _.range(1, Math.ceil(ctrl.total / ctrl.pageSize) + 1);
                },
                function(response) {
                    ctrl.status = 'error';
                }
            );
        };
    }],

    templateUrl: '/static/js/components/sequence/interactions/interactions.html'
};

angular.module("rnaSequence").component("interactions", interactions);
