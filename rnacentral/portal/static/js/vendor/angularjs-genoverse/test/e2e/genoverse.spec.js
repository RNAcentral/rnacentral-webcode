describe("genoverse directive spec", function() {
    var Homepage = function() {
        browser.get("http://localhost:8000/index.html");

        this.genomicStartInput = element(by.css('#genomic-start-input'));
        expect((this.genomicStartInput).isPresent()).toBe(true);
        this.genomicEndInput = element(by.css('#genomic-end-input'));
        expect((this.genomicEndInput).isPresent()).toBe(true);

        this.gvScrollRightButton = element(by.css('.gv-scroll-right'));
        expect((this.gvScrollRightButton).isPresent()).toBe(true);
        this.gvWrapper = element.all(by.css('.gv-wrapper')).get(1);
        expect((this.gvWrapper).isPresent()).toBe(true);
    };

    var page;

    beforeEach(function() {
        page = new Homepage();
    });


    it("should update start and end locations in response to viewport movement button", function() {
        var initialStart = page.genomicStartInput.getAttribute('value');
        var initialEnd = page.genomicEndInput.getAttribute('value');

        page.gvScrollRightButton.click();

        var updatedStart = page.genomicStartInput.getAttribute('value');
        var updatedEnd = page.genomicEndInput.getAttribute('value');

        expect(updatedStart).toBeGreaterThan(initialStart);
        expect(updatedEnd).toBeGreaterThan(initialEnd);
    });


    it("should update start and end locations in response to viewport drag", function() {
        var initialStart = page.genomicStartInput.getAttribute('value');
        var initialEnd = page.genomicEndInput.getAttribute('value');

        // drag canvas, increase coordinates
        browser.actions()
            .mouseMove(page.gvWrapper, {x: 200, y: 100})
            .mouseDown()
            .mouseMove({x: -100, y: 0})
            .mouseUp()
            .perform();

        var updatedStart = page.genomicStartInput.getAttribute('value');
        var updatedEnd = page.genomicEndInput.getAttribute('value');

        expect(updatedStart).toBeGreaterThan(initialStart);
        expect(updatedEnd).toBeGreaterThan(initialEnd);
    });


    it("should keep url, browser address line, forms and hyperlinks in sync", function() {

    });

    it("should be able to leave the page", function() {

    });


    it("should survive switcing to a wrong species", function() {

    });


    it("should survive wrong coordinates", function() {

    });

});