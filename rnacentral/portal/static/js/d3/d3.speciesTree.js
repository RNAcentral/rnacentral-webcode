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

// Displays species tree based on the combined lineages from all xrefs.
// Based on http://mbostock.github.io/d3/talk/20111018/tree.html

d3SpeciesTree = function(data, upi, selector){

  var levelWidth = [1],
      edgeLength = 150,
      duration = 500,
      longestLabel = 0,
      maxLabelLength = 20,
      m = {
        'top': 20,
        'right': 40,
        'bottom': 20,
        'left': 40
      },
      i = 0;

  childCount(0, data);

  var w = levelWidth.length * edgeLength + longestLabel * 3,
      h = d3.max(levelWidth) * 30;

  var tree = d3.layout.tree()
      .size([h, w]);

  var diagonal = d3.svg.diagonal()
      .projection(function(d) { return [d.y, d.x]; });

  var vis = d3.select(selector).append("svg:svg")
      .attr("width", w + m.left + m.right)
      .attr("height", h + m.top + m.bottom)
    .append("svg:g")
      .attr("transform", "translate(" + m.top + "," + m.bottom + ")");

  (function(){
    data.x0 = h / 2;
    data.y0 = w;

    function toggleAll(d) {
      if (d.children) {
        d.children.forEach(toggleAll);
        toggle(d);
      }
    }

    // Initialize the display to show the nodes.
    toggle(data.children);
    toggle(data);
    update(data);
    toggle(data);
    update(data);

  })();

  function update(source) {
    // Compute the new tree layout.
    var nodes = tree.nodes(data).reverse();

    // Normalize for fixed-depth.
    nodes.forEach(function(d) { d.y = w - (d.depth * edgeLength); });

    // Update the nodes
    var node = vis.selectAll("g.node")
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("svg:g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
        .on("click", function(d) { toggle(d); update(d); });

    nodeEnter.append("svg:circle")
        .attr("r", 1e-6)
        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

    nodeEnter.filter(function(d){return d.hasOwnProperty('taxid');})
      .append("a")
        .attr("xlink:href", function (d) { return "/rna/" + upi + "/" + d.taxid; })
      .append("text")
        .attr("x", function(d) { return d.children || d._children ? 10 : -10; })
        .attr("dy", ".35em")
        .attr("class", "species-node")
        .attr("text-anchor", "end")
        .style("fill", "steelblue")
        .text(function(d){return d.name;});

    nodeEnter.filter(function(d){return !d.hasOwnProperty('taxid');}).append("svg:text")
        .attr("x", function(d) { return d.children || d._children ? 10 : -10; })
        .attr("dy", ".35em")
        .attr("text-anchor", function(d) { return d.children || d._children ? "start" : "end"; })
        .text(function(d) { return getNodeName(d); })
        .style("fill-opacity", 1e-6);

    nodeEnter.append("svg:title")
      .text(function(d) { return getHoverText(d) });

    // Transition nodes to their new position.
    var nodeUpdate = node.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

    nodeUpdate.select("circle")
        .attr("r", 4.5)
        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

    nodeUpdate.select("text")
        .style("fill-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
        .remove();

    nodeExit.select("circle")
        .attr("r", 1e-6);

    nodeExit.select("text")
        .style("fill-opacity", 1e-6);

    // Update the links
    var link = vis.selectAll("path.link")
        .data(tree.links(nodes), function(d) { return d.target.id; });

    // Enter any new links at the parent's previous position.
    link.enter().insert("svg:path", "g")
        .attr("class", "link")
        .attr("d", function(d) {
          var o = {x: source.x0, y: source.y0};
          return diagonal({source: o, target: o});
        })
      .transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function(d) {
          var o = {x: source.x, y: source.y};
          return diagonal({source: o, target: o});
        })
        .remove();

    // Stash the old positions for transition.
    nodes.forEach(function(d) {
      d.x0 = d.x;
      d.y0 = d.y;
    });

  }

  function childCount(level, n) {
    if(n.children && n.children.length > 0) {
      if(levelWidth.length <= level + 1) levelWidth.push(0);

      levelWidth[level+1] += n.children.length;

      n.children.forEach(function(d) {
        childCount(level + 1, d);
        if (d.name && d.name.length > longestLabel) {
          longestLabel = d.name.length;
        }
      });
    }
  }

  // Toggle children.
  function toggle(d) {
    if (d.children) {
      d._children = d.children;
      d.children = null;
    } else {
      d.children = d._children;
      d._children = null;
    }
  }

  function getHoverText(node) {
    var hoverText = '';
    if (node.size) {
      hoverText += [node.size, ' cross-reference', node.size > 1 ? 's' : ''].join('');
    } else if (node.name.length > maxLabelLength) {
      hoverText = node.name;
    }
    return hoverText;
  }

  function getNodeName(node) {
    var nodeName;
    // truncate long taxon names
    if (node.name.length > maxLabelLength) {
      nodeName = node.name.substr(0,maxLabelLength) + '...';
    } else {
      nodeName = node.name;
    }
    return nodeName;
  }

};
