// Displays species sunburst based on the combined lineages from all xrefs.
// Based on http://bl.ocks.org/mbostock/4348373
// Text labels: http://blog.luzid.com/2013/extending-the-d3-zoomable-sunburst-with-labels/

d3SpeciesSunburst = function(data, selector, width, height){

	var jsonTree = data,
	    radius = Math.min(width, height) / 2;

	var x = d3.scale.linear()
	    .range([0, 2 * Math.PI]);

	var y = d3.scale.linear()
	    .range([0, radius]);

	var color = d3.scale.category20c();

	var svg = d3.select(selector).append("svg")
	    .attr("width", width)
	    .attr("height", height)
	  .append("g")
	    .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

	var partition = d3.layout.partition()
	    .value(function(d) { return d.size; });

	var arc = d3.svg.arc()
	    .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
	    .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
	    .innerRadius(function(d) { return Math.max(0, y(d.y)); })
	    .outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

	// d3.json("flare.json", function(error, root) {
	  var g = svg.selectAll("g")
	      .data(partition.nodes(jsonTree))
	    .enter().append("g");

	  var path = g.append("path")
	    .attr("d", arc)
	    // .style("fill", function(d) { return color((d.children ? d : d.parent).name); })
	    .attr("fill", function(d) { return "#6baed6"; })
	    .attr("title", function(d) { return d.name; })
		.on("mouseover", function() {
		  d3.select(this)
		    .attr('fill', '#f0ad4e')
		})
		.on("mouseout",  function() {
		  d3.select(this)
		    .attr('fill', '#3F7D97' )
	  	});

	    ;
	    // .on("click", click);

	  // var text = g.append("text")
	  //   .attr("transform", function(d) { return "rotate(" + computeTextRotation(d) + ")"; })
	  //   .attr("x", function(d) { return y(d.y); })
	  //   .attr("dx", "6") // margin
	  //   .attr("dy", ".35em") // vertical-align
	  //   .text(function(d) { return d.name; });

	  // function click(d) {
	  //   // fade out all text elements
	  //   text.transition().attr("opacity", 0);

	  //   path.transition()
	  //     .duration(750)
	  //     .attrTween("d", arcTween(d))
	  //     .each("end", function(e, i) {
	  //         // check if the animated element's data e lies within the visible angle span given in d
	  //         if (e.x >= d.x && e.x < (d.x + d.dx)) {
	  //           // get a selection of the associated text element
	  //           var arcText = d3.select(this.parentNode).select("text");
	  //           // fade in the text element and recalculate positions
	  //           arcText.transition().duration(0)
	  //             .attr("opacity", 1)
	  //             .attr("transform", function() { return "rotate(" + computeTextRotation(e) + ")" })
	  //             .attr("x", function(d) { return y(d.y); });
	  //         }
	  //     });
	  // }
	// });

	d3.select(self.frameElement).style("height", height + "px");

	//initializing tooltips
	$("svg path").tooltip({
	    'container': 'body'
	});

	// Interpolate the scales!
	function arcTween(d) {
	  var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
	      yd = d3.interpolate(y.domain(), [d.y, 1]),
	      yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
	  return function(d, i) {
	    return i
	        ? function(t) { return arc(d); }
	        : function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); return arc(d); };
	  };
	}

	function computeTextRotation(d) {
	  return (x(d.x + d.dx / 2) - Math.PI / 2) / Math.PI * 180;
	}

};
