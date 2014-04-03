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

// Visualize expert databases as a treemap.
// based on http://bl.ocks.org/mbostock/4063582

ExpertDatabaseTreemap = function(selector){

  var data = {
    "name": "RNAcentral Expert Databases",
    "children": [
      {"name": "To be imported",
      "color": "#428bca",
      "children": [
        {"name": "CRW", "size": 14.3, "info": "comparative sequence and structure information for ribosomal, intron, and other RNAs"},
        {"name": "gtRNAdb", "size": 14.3, "info": "tRNA predictions in genomes"},
        {"name": "HGNC", "size": 14.3, "info": "HUGO Gene Nomenclature Committee"},
        {"name": "lncRNAdb", "size": 14.3, "info": "annotations of eukaryotic long non-coding RNAs"},
        {"name": "MODOMICS", "size": 20, "info": "RNA modification data"},
        {"name": "NONCODE", "size": 14.3, "info": "integrative annotation of long noncoding RNAs"},
        {"name": "NPInter", "size": 14.3, "info": "experimentally determined functional interactions between ncRNAs and proteins, mRNAs or genomic DNA"},
        {"name": "piRNABank", "size": 14.3, "info": "comprehensive resource on Piwi-interacting RNAs"},
        {"name": "RefSeq", "size": 14.3, "info": "comprehensive, integrated, non-redundant, well-annotated set of reference sequences"},
        {"name": "RDP", "size": 14.3, "info": "ribosome-related data and services"},
        {"name": "RNApathways", "size": 14.3, "info": "RNA maturation and decay pathways"},
        {"name": "snoRNAdb", "size": 14.3, "info": "predicted snoRNA genes"},
        {"name": "RFAM", "size": 14.3, "info": "collection of RNA families, each represented by multiple sequence alignments, consensus secondary structures and covariance models"},
        {"name": "SILVA", "size": 14.3, "info": "quality checked and aligned ribosomal RNA sequences"}
      ]},

      {"name": "Imported",
      "color": "#5cb85c",
      "children": [
        {"name": "tmRNA Website", "size": 20, "xref": 20000, "info": "tmRNA sequence data"},
        {"name": "SRPDB", "size": 10, "xref": 20000, "info": "aligned, annotated and phylogenetically ordered sequences related to structure and function of SRP" },
        {"name": "VEGA", "size": 10, "xref": 21000, "info": "high quality manual annotation of vertebrate finished genome sequence"},
        {"name": "miRBase", "size": 10, "xref": 20000, "info": "microRNA sequences and annotation"},
        {"name": "ENA", "size": 60, "xref": 6000000, "info": "European Nucleotide Archive stores a comprehensive record of the world's nucleotide sequencing information"}
      ]}
    ]
  };

  var w = 1180 - 80,
      h = 600 - 180,
      x = d3.scale.linear().range([0, w]),
      y = d3.scale.linear().range([0, h]),
      color = d3.scale.category20c(),
      root,
      node;

  var treemap = d3.layout.treemap()
      .round(false)
      .size([w, h])
      .sticky(true)
      .sort(null)
      .value(function(d) { return d.size; });

  var svg = d3.select(selector).append("div")
      .attr("class", "chart")
      .style("width", w + "px")
      .style("height", h + "px")
    .append("svg:svg")
      .attr("width", w)
      .attr("height", h)
    .append("svg:g")
      .attr("transform", "translate(.5,.5)");


    node = root = data;

    var nodes = treemap.nodes(root)
        .filter(function(d) { return !d.children; });

    var cell = svg.selectAll("g")
        .data(nodes)
      .enter().append("svg:g")
        .attr("class", "cell")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
        .on("click", function(d) { return zoom(node == d.parent ? root : d.parent); });

    cell.append("svg:rect")
        .attr("width", function(d) { return d.dx - 1; })
        .attr("height", function(d) { return d.dy - 1; })
        .attr("title", function(d) { return d.info; } )
        .style("fill", function(d) { return d.parent.color; });

    cell.append("svg:text")
        .attr("x", function(d) { return d.dx / 2; })
        .attr("y", function(d) { return d.dy / 2; })
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .text(function(d) { return d.name; })
        .style("fill", "whitesmoke")
        .style("opacity", function(d) { d.w = this.getComputedTextLength(); return d.dx > d.w ? 1 : 0; });

    d3.select(window).on("click", function() { zoom(root); });

    // d3.select("select").on("change", function() {
    //   treemap.value(this.value == "size" ? size : xref).nodes(xrefsort);
    //   zoom(node);
    // });

  function size(d) {
    return d.size;
  }

  function xref(d) {
    return d.xref;
  }

  function count(d) {
    return 1;
  }

  function zoom(d) {
    var kx = w / d.dx, ky = h / d.dy;
    x.domain([d.x, d.x + d.dx]);
    y.domain([d.y, d.y + d.dy]);

    var t = svg.selectAll("g.cell").transition()
        .duration(d3.event.altKey ? 7500 : 750)
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    t.select("rect")
        .attr("width", function(d) { return kx * d.dx - 1; })
        .attr("height", function(d) { return ky * d.dy - 1; })

    t.select("text")
        .attr("x", function(d) { return kx * d.dx / 2; })
        .attr("y", function(d) { return ky * d.dy / 2; })
        .style("opacity", function(d) { return kx * d.dx > d.w ? 1 : 0; });

    node = d;
    d3.event.stopPropagation();
  }

};
