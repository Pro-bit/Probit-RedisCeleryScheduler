probit-scheduler - JSON redis backed scheduler for celery made directly from https://github.com/SPSCommerce/swiss-chard.

To install use:
	pip install probit-scheduler


To configure, set CELERYBEAT_SCHEDULER to probit.scheduler.ProbitScheduler and specify a CELERY_REDIS_SCHEDULER_URL.
```
    CELERYBEAT_SCHEDULER="probit.scheduler.ProbitScheduler"
	CELERY_REDIS_SCHEDULER_URL = "redis://localhost:6379/1"
	CELERYBEAT_SCHEDULE = {
	    'TestTask': {
	        'task': '¸path.to.TestTask',
	        'schedule': timedelta(seconds=3),
	        'args': (),
	    }
	}
```

SCHEDULER EXAMPLES:
# get scheduler
scheduler = EntryProxy(StrictRedis.from_url(app.config["CELERY_REDIS_SCHEDULER_URL"])

# create new scheduler entry
# with timedelta every 3 seconds
entry = scheduler.load({
    "name": "myNewTask",
    "schedule": {'seconds': 3, 'days': 0, 'microseconds': 0, 'relative': False, 'type': 'delta'},
    "task": "TestTask",
    "args": [],
    "kwargs": {},
    "options": {},
    "last_run_at": None,
    "total_run_count": 5
})
# or like crontab every day at 5 oclock
entry = scheduler.load({
    "name": "myNewTask",
    "schedule": { "hour": 5, "day_of_week": "*", "type": "crontab", "minute": 0 },
    "task": "TestTask",
    "args": [],
    "kwargs": {},
    "options": {},
    "last_run_at": None,
    "total_run_count": 5
})

# save global scheduler task for all databases (update task also like this)
scheduler.save_for_all(entry)

# save scheduler task for specified company
# create new scheduler entry for company (here we have to add company id to arguments of the task)
entry = scheduler.load({
    "name": "myNewTask",
    "schedule": {'seconds': 3, 'days': 0, 'microseconds': 0, 'relative': False, 'type': 'delta'},
    "task": "TestTask",
    "args": [company_id],
    "kwargs": {},
    "options": {},
    "last_run_at": None,
    "total_run_count": 5
})
# save company task to redis to redis
scheduler.save_for_company(company_id, entry)

# load global tasks
tasks = scheduler.get_for_all()

# load companys scheduled tasks
companyTasks = scheduler.get_for_company(company_id)

