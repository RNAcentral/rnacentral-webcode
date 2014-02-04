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

d3ExpertDatabasePieChart = function(selector){

  var width = 400,
      height = 400,
      radius = Math.min(width, height) / 2,
      labelr = radius + 30; // radius for label anchor

  var color = d3.scale.category10();

  var arc = d3.svg.arc()
      .outerRadius(radius - 10)
      .innerRadius(0);

  var pie = d3.layout.pie()
      .sort(null)
      .value(function(d) { return d.sequences; });

  var svg = d3.select(selector).append("svg")
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  var data = [
    {"database": "SRPDB", "sequences": "855"},
    {"database": "miRBase", "sequences": "3661"},
    {"database": "tmRNA Website", "sequences": "21318"},
    {"database": "VEGA", "sequences": "21388"}
  ];

  data.forEach(function(d) {
    d.sequences = +d.sequences;
  });

  var g = svg.selectAll(".arc")
      .data(pie(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", arc)
      .attr("title", function(d) { return get_tooltip(d) } )
      .style("fill", function(d) { return color(d.data.sequences); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
      .attr("dy", ".35em")
      .style("fill", "whitesmoke")
      .style("text-anchor", "middle")
      .text(function(d) { return get_label(d) });

  function get_label(d) {
      if (d.data.database == 'SRPDB' || d.data.database == 'miRBase') {
        return '';
      } else {
        return d.data.database;
      }
  }

  function get_tooltip(d) {
      if (d.data.database == 'SRPDB') {
        return 'SRPDB: ' + d.data.sequences + " sequences";
      } else if ( d.data.database == 'miRBase' ) {
        return 'miRBase: ' + d.data.sequences + " sequences";
      } else {
        return d.data.sequences + " sequences";
      }
  }

};