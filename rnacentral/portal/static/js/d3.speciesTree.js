// Displays species tree based on the combined lineages from all xrefs.
// Based on http://mbostock.github.io/d3/talk/20111018/tree.html

d3SpeciesTree = function(data, selector){

  var m = [20, 120, 20, 120],
      jsonTree = JSON.parse(data),
      w = 2200 - m[1] - m[3], // width
      h = 400 - m[0] - m[2], // height
      edgeLength = 100,
      i = 0,
      root;

  var tree = d3.layout.tree()
      .size([h, w]);

  var diagonal = d3.svg.diagonal()
      .projection(function(d) { return [d.y, d.x]; });

  var vis = d3.select(selector).append("svg:svg")
      .attr("width", w + m[1] + m[3])
      .attr("height", h + m[0] + m[2])
    .append("svg:g")
      .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

  // replace the anonymous functin with d3.json if necessary
  (function(){
    root = jsonTree;
    root.x0 = h / 2;
    root.y0 = 0;

    function toggleAll(d) {
      if (d.children) {
        d.children.forEach(toggleAll);
        toggle(d);
      }
    }

    // Initialize the display to show the nodes.
    toggle(root.children);
    toggle(root);
    update(root);
    toggle(root);
    update(root);

  })();

  function update(source) {
    var duration = d3.event && d3.event.altKey ? 3000 : 500;

    // compute the new height
    var levelWidth = [1];
    var childCount = function(level, n) {

      if(n.children && n.children.length > 0) {
        if(levelWidth.length <= level + 1) levelWidth.push(0);

        levelWidth[level+1] += n.children.length;
        n.children.forEach(function(d) {
          childCount(level + 1, d);
        });
      }
    };
    childCount(0, root);
    var newHeight = d3.max(levelWidth) * 20; // 20 pixels per line
    tree = tree.size([newHeight, w]);

    // Compute the new tree layout.
    var nodes = tree.nodes(root).reverse();

    // Normalize for fixed-depth.
    nodes.forEach(function(d) { d.y = d.depth * edgeLength; });

    // Update the nodes…
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

    nodeEnter.append("svg:text")
        .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
        .attr("dy", ".35em")
        .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
        .text(function(d) { return getNodeName(d); })
        .style("fill-opacity", 1e-6);

    nodeEnter.append("svg:title")
      .text(function(d) { return d.name; });

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

    // Update the links…
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

    // Set height and width
    var speciesLabels = 350;
    $('#d3-species-tree svg').attr('height', newHeight + 20);
    $('#d3-species-tree svg').attr('width', levelWidth.length * edgeLength + speciesLabels);
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

  function getNodeName(node) {
    var nodeName = '';
    if (node.size) {
      // terminal node, display cross-reference counts
      nodeName = [node.name, ' (', node.size, ' cross-references)'].join('')
    } else {
      // truncate long taxon names
      if (node.name.length > 10) {
        nodeName = node.name.substr(0,10) + '...';
      } else {
        nodeName = node.name;
      }
    }
    return nodeName;
  }

};
