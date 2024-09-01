(function() {
  // filter job
  const filterBtns = document.querySelectorAll('.btn-filter-job');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget;
      const params = new URLSearchParams(window.location.search);
      params.set('job_id', el.dataset.jobId)
      TAKO.setSearchParams(params);
    })
  });

  // execute job
  var executeBtns = document.getElementsByClassName('btn-execute-job');
  [].slice.call(executeBtns).forEach(function(x) {
    x.addEventListener('mouseup', function(e) {
      var dom = e.currentTarget;
      var taskid = Number(dom.dataset.taskId);
      if (!confirm("Are you sure to execute task " + taskid + ' ?')) {
        return
      }
      fetch('/api/task/execute', {
        method: 'POST',
        body: JSON.stringify({
          task_id: taskid,
        }),
        headers: {
          'Content-Type': 'application/json'
        },
      }).then(function(res) {
        console.log(res.json());
        location.reload();
      }).catch(function(err) {
        console.error(err);
      })
    })
  })

  // cancel job
  var cancelBtns = document.getElementsByClassName('btn-cancel-job');
  [].slice.call(cancelBtns).forEach(function(x) {
    x.addEventListener('mouseup', function(e) {
      var dom = e.currentTarget;
      var id = Number(dom.dataset.jobId);
      fetch('/api/job/cancel', {
        method: 'POST',
        body: JSON.stringify({
          job_id: id,
        }),
        headers: {
          'Content-Type': 'application/json'
        },
      }).then(function(res) {
        console.log(res.json());
        location.reload();
      }).catch(function(err) {
        console.error(err);
      })
    })
  })
})();
