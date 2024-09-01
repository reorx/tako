var draw_event_drops = function(el, data, margin) {
  var now = new Date();
  var tooltip = d3
    .select('body')
    .append('div')
    .classed('ed-tooltip', true)
    .style('opacity', 0)
    .style('pointer-events', 'auto');

  var options = {
    bound: {
      format: d3.timeFormat('%Y-%m-%d'),
    },
    line: {
      height: 36,
      color: function(line, _) {
        switch (line.name) {
          case 'SUCCESS':
            return '#26A745';
          case 'SENT':
            return '#5755d9';
          case 'ERROR':
            return '#DC3545';
          default:
            return '#FFDD57';
        }
      },
    },
    metaballs: {
      blurDeviation: 8,
    },
    drop: {
      date: function(d) {
        return new Date(d.date);
      },
      radius: 4.1,
      onMouseOver: function(data) {
        tooltip
          .transition()
          .duration(200)
          .style('opacity', 1)
          .style('pointer-events', 'auto');
        tooltip
          .html(`
            <div>
              <span class="label ${data.status_class}">${data.status}</span>
              <span class="number-font text-underline">${data.id}</span>
              <span class="number-font">${data.date}</span>
              <span class="number-font">${data.duration}</span>
            </div>
            <div>${data.job_id}</div>
          `)
          .style('left', d3.event.pageX - 30 + 'px')
          .style('top', d3.event.pageY + 15 + 'px');
      },
      onMouseOut: function() {
       tooltip
        .transition()
        .duration(500)
        .style('opacity', 0)
        .style('pointer-events', 'none');
      },
      onClick: function(data) {
        window.open('/executions/' + data.id, '_blank');
      },
    },
    range: {
      start: (new Date()).setDate(now.getDate() - 1),
      end: (new Date()).setDate(now.getDate() + 1),
    },
    axis: {
      formats: {
        milliseconds: '%L',
        seconds: ':%S',
        minutes: '%I:%M',
        hours: '%I %p',
        days: '%m-%d',
        weeks: '%b %d',
        months: '%m',
        year: '%Y',
      },
    },
  };
  if (margin === undefined) {
    margin = {
      right: 0,
      left: 0,
    };
  }
  options['margin'] = margin;
  var chart = eventDrops(options);

  // console.log('data', data);
  d3.select(el).data([data]).call(chart);
};
