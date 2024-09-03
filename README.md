# Tako - Embedded Task Manager

Tako is a simple task manager aimed for embedding into your existing Django application.
Tako can also be run as a standalone application, think of it as a crontab with a web interface.

When integrated into your Django application, Tako can add your Python functions as jobs and run them on a schedule.
Your application will have an interface to see the status of the jobs and re-run them if needed.
You can also create and edit tasks that take a script to run without restarting your application.


## Features

- Give a complete overview of job executions in a dashboard, with timeline visualization and detailed data table.
- Filter job executions by job and status.
- Re-run job by a single click.
- Create tasks that take a script and run it on a schedule.
- Remember historical versions of the scripts.


## TODO

Before 1.0:
- [x] Create and update task
- [ ] Create and update script
- [ ] Run job
- [ ] Cancel a running job (if possible)


Additional Features:
- [ ] Filter executions by time range
- [ ] Better script editor
- [ ] Pause job
- [ ] Add support for bash scripts
- [ ] Async and ASGI support
- [ ] Send notifications when a task fails (with [apprise](https://github.com/caronc/apprise))
