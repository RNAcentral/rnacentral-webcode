describe("normalize-expert-db-name:", function() {
    beforeEach(function() {
        module('expertDatabase');
    });

    describe("labelToImageUrl():", function() {
        it("should handle 'tmrna-website'", inject(function(normalizeExpertDbName) {
            console.log(normalizeExpertDbName.labelToImageUrl('tmrna-website'));
            expect(normalizeExpertDbName.labelToImageUrl('tmrna-website')).toEqual('');
        }));

        it("should handle 'gencode'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.labelToImageUrl('gencode')).toEqual('');
        }));
    });

    describe("nameToImageUrl():", function() {
        it("should handle 'tmRNA Website'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.nameToImageUrl('tmRNA Website')).toEqual('');
        }));

        it("should handle 'GENCODE'", inject(function(normalizeExpertDbName) {
            expect(normalizeExpertDbName.nameToImageUrl('GENCODE')).toEqual('');
        }));
    })
});
