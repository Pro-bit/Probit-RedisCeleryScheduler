probit-scheduler - JSON redis backed scheduler for celery made directly from https://github.com/SPSCommerce/swiss-chard.

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

