describe("normalize-expert-db-name:", function() {
    beforeEach(function() {
        module('expertDatabase');
    });

    describe("labelToImageUrl():", function() {
        it("should handle 'tmrna-website'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.labelToImageUrl('tmrna-website')).toEqual('/static/img/expert-db-logos/tmrna-website.png');
        }));

        it("should handle 'gencode'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.labelToImageUrl('gencode')).toEqual('/static/img/expert-db-logos/gencode.png');
        }));
    });

    describe("nameToImageUrl():", function() {
        it("should handle 'tmRNA Website'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.nameToImageUrl('tmRNA Website')).toEqual('/static/img/expert-db-logos/tmrna-website.png');
        }));

        it("should handle 'GENCODE'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.nameToImageUrl('GENCODE')).toEqual('/static/img/expert-db-logos/gencode.png');
        }));
    });

    describe("labelToDb():", function() {
       it("should handle 'tmrna-website'", inject(function(normalizeExpertDbName) {
           expect(normalizeExpertDbName.labelToDb('tmrna-website')).toEqual('TMRNA_WEB');
       }));

       it("should handle 'GENCODE'", inject(function(normalizeExpertDbName) {
           expect(normalizeExpertDbName.labelToDb('gencode')).toEqual('GENCODE');
       }));
    });
});
