queue()
    .defer(d3.json, "donorschoose/projects")
    .await(makeGraphs);


d3.select(window).on('resize.updatedc', function() {
  dc.events.trigger(function() {
    dc.chartRegistry.list().forEach(function(chart) {
            var container = chart.root().node();
            if (!container) return; // some graphs don't have a node (?!)
            container=container.parentNode.getBoundingClientRect();
            chart.width(container.width);
            chart.rescale && chart.rescale(); // some graphs don't have a rescale
      });

      dc.redrawAll();
  },500);
});

function makeGraphs(error,projectsJson) {
	//Clean projectsJson data

  var width = document.getElementById('time-chart').offsetWidth;

	var donorschooseProjects = projectsJson;
	//var dateFormat = d3.time.format("%Y-%m-%d");
  var dateFormat = d3.time.format("%Y-%m-%d");
  donorschooseProjects.forEach(function(d) {
      d["race_driven"] = dateFormat.parse(d["race_driven"]);

  });
	//Create a Crossfilter instance
	var ndx = crossfilter(donorschooseProjects);

	//Define Dimensions
	var dateDim = ndx.dimension(function(d) { return d.race_driven; });
	var trackDim = ndx.dimension(function(d) { return d.track_id; });
  var trackDim_row = ndx.dimension(function(d) { return d.track_id; });

  var weekdayDimension = ndx.dimension(function(d) {
      return new Date(d.race_driven).getDay();
  });

	//Calculate metrics
	var numRacesByDate = dateDim.group();
	var numRacesByTrack = trackDim.group();
  var numMon = trackDim_row.group().reduceSum(function (d){return d.sum_money});

	var all = ndx.groupAll();

	//Define values (to be used in charts)
	var minDate = dateDim.bottom(1)[0]["race_driven"];
	var maxDate = dateDim.top(1)[0]["race_driven"];

    //Charts
	var timeChart = dc.barChart("#time-chart");
  var resourceTypeChart = dc.pieChart("#daytrack-chart");
  var RowChart = dc.rowChart("#row-chart");



  function sel_stack(i) {
      return function(d) {
          return d.value[i];
      };
  }


	timeChart
		.width(width)
		.height(200)
		.margins({top: 10, right: 50, bottom: 30, left: 50})
		.dimension(dateDim)
		.group(numRacesByDate, "1", sel_stack('1'))

		.transitionDuration(500)
    //.xUnits(d3.time.hours)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.xAxisLabel("Year")
    .renderTitle(true)
    .title(function(d){ return "emma"; })

		.yAxis().ticks(4);

  resourceTypeChart
    .width(width*1.2/5)
    .height(width*1.2/5)
    .slicesCap(12)
    .innerRadius(100)
    .dimension(trackDim)
    .group(numRacesByTrack)
    .legend(dc.legend());



  RowChart
    .width(width*(3/5))
    .height(300)
    .dimension(trackDim_row)
    .group(numMon)
    .elasticX(true);


  dc.renderAll();


};
