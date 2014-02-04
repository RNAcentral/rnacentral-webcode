/*
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Visualize expert database sequence distribution as an area chart.
// Inspired by:
// http://bl.ocks.org/mbostock/3883195
// http://bl.ocks.org/mbostock/3902569

ExpertDatabaseSequenceDistribution = function(selector, data, max_width, max_height){

    var margin = {top: 20, right: 60, bottom: 40, left: 50},
        width = max_width - margin.left - margin.right,
        height = max_height - margin.top - margin.bottom;

    var bisect = d3.bisector(function(d) { return d.length; }).left;

    var x = d3.scale.log()
        .range([0, width]);

    var y = d3.scale.log()
        .range([height, 0]);

    var numberFormat = d3.format("s");
    function logFormat(d) {
        var x = Math.log(d) / Math.log(10) + 1e-6;
        return Math.abs(x - Math.floor(x)) < .6 ? numberFormat(d) : "";
    }

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickFormat(logFormat)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickFormat(logFormat)
        .orient("left");

    var area = d3.svg.area()
        .x(function(d) { return x(d.length); })
        .interpolate("monotone")
        .y0(height)
        .y1(function(d) { return y(d.count); });

    var svg = d3.select(selector).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function(d) {
      d.length = d.length;
      d.count = +d.count;
    });

    data.sort(function(a, b) {
        return a.length - b.length;
    });

    x.domain(d3.extent(data, function(d) { return d.length; }));
    y.domain(d3.extent(data, function(d) { return d.count; }));

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
      .append("text")
        .attr("x", 330)
        .attr("dy", "2.7em")
        .style("text-anchor", "middle")
        .text("Number of nucleotides");

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Sequences");

    svg.append("path")
        .datum(data)
        .attr("class", "area")
        .attr("d", area);

    var focus = svg.append("g")
      .attr("class", "focus")
      .style("display", "none");

    focus.append("circle")
      .attr("r", 4.5);

    focus.append("text")
      .attr("x", 9)
      .attr("dy", ".35em");

    svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() { focus.style("display", null); })
      .on("mouseout", function() { focus.style("display", "none"); })
      .on("mousemove", mousemove);

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]),
            i = bisect(data, x0, 1),
            d0 = data[i - 1],
            d1 = data[i],
            d = x0 - d0.count > d1.count - x0 ? d1 : d0;
        focus.attr("transform", "translate(" + x(d.length) + "," + y(d.count) + ")");
        focus.select("text").text(d.length + " nts");
    }

}