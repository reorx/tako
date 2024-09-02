(function () {
  // filter jobs button
  delegate('.btn-filter-job', 'click', (e) => {
    const el = e.delegateTarget;
    if (el.dataset.navExecutions) {
      window.location.href = TAKO.urls.executions + '?' + new URLSearchParams({job_id: el.dataset.jobId}).toString();
    } else {
      const params = new URLSearchParams(window.location.search);
      params.set('job_id', el.dataset.jobId)
      TAKO.setSearchParams(params);
    }
  })

  // execute job
  delegate('.btn-execute-job', 'mouseup', (e) => {
    var dom = e.delegateTarget;
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
    }).then(function (res) {
      console.log(res.json());
      location.reload();
    }).catch(function (err) {
      console.error(err);
    })
  })

  // cancel job
  delegate('.btn-cancel-job', 'mouseup', (e) => {
    var dom = e.delegateTarget;
    var id = Number(dom.dataset.jobId);
    fetch('/api/job/cancel', {
      method: 'POST',
      body: JSON.stringify({
        job_id: id,
      }),
      headers: {
        'Content-Type': 'application/json'
      },
    }).then(function (res) {
      console.log(res.json());
      location.reload();
    }).catch(function (err) {
      console.error(err);
    })
  })
})();
