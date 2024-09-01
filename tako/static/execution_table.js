// execute task
(function() {
  var executeBtns = document.getElementsByClassName('btn-execute');
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
})();

// cancel job
(function() {
  var executeBtns = document.getElementsByClassName('btn-cancel-job');
  [].slice.call(executeBtns).forEach(function(x) {
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
