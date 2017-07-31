queue()
    .defer(d3.json, "user/charts")
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


//Charts
//global defined because the html doc calls the charts
var moveChart = dc.lineChart('#monthly-move-chart');
var volumeChart = dc.barChart('#monthly-volume-chart');
var gainOrLossChart = dc.pieChart('#gain-loss-chart');
var weatherChart = dc.pieChart('#weather-chart');
var trackChart = dc.pieChart('#track-chart');
var quarterChart = dc.pieChart('#quarter-chart');
var dayOfWeekChart = dc.rowChart('#day-of-week-chart');
var nasdaqCount = dc.dataCount('.dc-data-count');


function makeGraphs(error,projectsJson) {
	//Clean projectsJson data

  var width = document.getElementById('monthly-move-chart').offsetWidth;
	var data = projectsJson;
  var dateFormat = d3.time.format("%Y-%m-%dT%M:%H:%S");

  data.forEach(function (d) {
    d.dd = dateFormat.parse(d.race_driven);
    d.month = d3.time.month(d.dd); // pre-calculate month for better performance
    d.close = +d.close; // coerce to number
    d.open = +d.open;
  });

	//Create a Crossfilter instance
	var ndx = crossfilter(data);
  var all = ndx.groupAll();

	//Define Dimensions
	var dateDim = ndx.dimension(function(d) { return d.race_driven; });
	var trackDim = ndx.dimension(function(d) { return d.track_id; });


  var yearlyDimension = ndx.dimension(function (d) {
    return d3.time.year(d.dd).getFullYear();
  });

  var dateDimension = ndx.dimension(function (d) {
    return d.dd;
  });

  var weekdayDimension = ndx.dimension(function(d) {
      return new Date(d.race_driven).getDay();
  });

  // Dimension by month
  var moveMonths = ndx.dimension(function (d) {
      return d.month;
  });


  var Weather = ndx.dimension(function(d) { return d.weather; });

  var moveMonths = ndx.dimension(function (d) {
      return d.month;
  });


  var quarter = ndx.dimension(function (d) {
     var month = d.dd.getMonth();
     if (month <= 2) {
         return 'Q1';
     } else if (month > 2 && month <= 5) {
         return 'Q2';
     } else if (month > 5 && month <= 8) {
         return 'Q3';
     } else {
         return 'Q4';
     }
   });

  var gainOrLoss = ndx.dimension(function (d) {
       return d.won > 0 ? 'Win' : 'Loss';
  });


   // Counts per weekday
  var dayOfWeek = ndx.dimension(function (d) {
        var day = d.dd.getDay();
        var name = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return day + '.' + name[day];
  });


	//Calculate metrics

  var wonByMonthGroup = moveMonths.group().reduceSum(function (d) {
     return d.won;
  });

  var monthlyLossesGroup = moveMonths.group().reduceSum(function (d) {
       return d.lost;
  });


  var numWeather = Weather.group();

  var numTracks = trackDim.group();

	var numRacesByDate = dateDim.group();

  var gainOrLossGroup = gainOrLoss.group();

  var quarterGroup = quarter.group().reduceSum(function (d) {
       return d.won;
   });
  var dayOfWeekGroup = dayOfWeek.group();

  moveChart /* dc.lineChart('#monthly-move-chart', 'chartGroup') */
      .renderArea(true)
      .width(990)
      .height(200)
      .transitionDuration(1000)
      .margins({top: 30, right: 50, bottom: 25, left: 40})
      .dimension(moveMonths)
      .mouseZoomable(true)
  // Specify a "range chart" to link its brush extent with the zoom of the current "focus chart".
      .rangeChart(volumeChart)
      .x(d3.time.scale().domain([new Date(2010, 0, 1), new Date(2017, 11, 31)]))
      .round(d3.time.month.round)
      .xUnits(d3.time.months)
      .elasticY(true)
      .renderHorizontalGridLines(true)

      .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
      .brushOn(false)

      .group(wonByMonthGroup, 'Monthly Wins Sum')

      .stack(monthlyLossesGroup, 'Monthly Losses Sum')
      ;

  volumeChart
      .width(990) /* dc.barChart('#monthly-volume-chart', 'chartGroup'); */
      .height(40)
      .margins({top: 0, right: 50, bottom: 20, left: 40})
      .dimension(moveMonths)
      .group(wonByMonthGroup)
      .centerBar(true)
      .gap(1)
      .x(d3.time.scale().domain([new Date(2010, 0, 1), new Date(2017, 11, 31)]))
      ;

  gainOrLossChart /* dc.pieChart('#gain-loss-chart', 'chartGroup') */
      .width(180)
      .height(180)
      .radius(80)
      .dimension(gainOrLoss)
      .group(gainOrLossGroup)
      .label(function (d) {
          if (gainOrLossChart.hasFilter() && !gainOrLossChart.hasFilter(d.data.key)) {
              return d.data.key + ' (0%)';
          }
          var label = d.data.key;
          if (all.value()) {
              label += ' (' + Math.floor(d.value / all.value() * 100) + '%)';
          }
          return label;
      })
      ;


  weatherChart /* dc.pieChart('#gain-loss-chart', 'chartGroup') */
      .width(180)
      .height(180)
      .radius(80)
      .dimension(Weather)
      .group(numWeather);

  trackChart
  .width(180)
  .height(180)
  .radius(80)
  .dimension(trackDim)
  .group(numTracks);


  quarterChart /* dc.pieChart('#quarter-chart', 'chartGroup') */
      .width(180)
      .height(180)
      .radius(80)
      .innerRadius(30)
      .dimension(quarter)
      .group(quarterGroup);

  dayOfWeekChart /* dc.rowChart('#day-of-week-chart', 'chartGroup') */
        .width(180)
        .height(180)
        .margins({top: 20, left: 10, right: 10, bottom: 20})
        .group(dayOfWeekGroup)
        .dimension(dayOfWeek)
        // Assign colors to each value in the x scale domain
        .label(function (d) {
            return d.key.split('.')[1];
        })
        // Title sets the row text
        .title(function (d) {
            return d.value;
        })
        .elasticX(true)
        .xAxis().ticks(4);

  nasdaqCount /* dc.dataCount('.dc-data-count', 'chartGroup'); */
      .dimension(ndx)
      .group(all)
      ;

  dc.renderAll();

};
