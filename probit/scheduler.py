try:
    import simplejson as json
except:
    import json
from celery.beat import Scheduler, ScheduleEntry
# from celery.utils.log import get_logger
from celery import current_app
from celery.schedules import crontab, schedule
from redis.client import StrictRedis
from redlock import Redlock
from datetime import timedelta, datetime

ENTRY_LIST_KEY = "probit:schedule:entries"

class EntryProxy(dict):
    """ A ScheduleEntry dictionary that mirrors a mongodb collection """

    def __init__(self, redis_connection):
        dict.__init__(self)
        self.__redis_connection = redis_connection
        self._load_all_entries()

    def _load_all_entries(self):
        entries = self.__redis_connection.hgetall(ENTRY_LIST_KEY)
        for entry in entries.values():
            data = json.loads(entry.decode('utf-8'))
            if data["last_run_at"]:
                data["last_run_at"] = datetime.strptime(data["last_run_at"], '%Y-%m-%dT%H:%M:%S.%f')
            self._load(data)

            print(str(entry))
    
    def _load(self, record):
        try:
            entry = ScheduleEntry(record['name'], record['task'], record['last_run_at'],
                record['total_run_count'], to_schedule(record['schedule']),
                record['args'], record['kwargs'], record['options'])
            dict.__setitem__(self, entry.name, entry)
            return entry
        except Exception as e:
            return None
        
    def _save(self, entry):
        print(str(entry))
        fields = {}
        fields['name'] = entry.name
        fields['schedule'] = from_schedule(entry.schedule)
        fields['task'] = entry.task
        fields['args'] = entry.args
        fields['kwargs'] = entry.kwargs
        fields['options'] = entry.options
        fields['last_run_at'] = entry.last_run_at
        fields['total_run_count'] = entry.total_run_count
        serialized = json.dumps(objISODateString(fields))
        self.__redis_connection.hmset(ENTRY_LIST_KEY, {entry.name: serialized})
        
    def __setitem__(self, name, entry):
        dict.__setitem__(self, name, entry)
        self._save(entry)
        
    def update(self, other):
        dict.update(self, other)
        for entry in other.items():
            self._save(entry)
            
    def sync(self, name):
        record = self.__redis_connection.hget(ENTRY_LIST_KEY, name)
        if record is None:
            self.pop(name, None)
            return None
        else:
            data = json.loads(record.decode('utf-8'))
            if data["last_run_at"]:
                data["last_run_at"] = datetime.strptime(data["last_run_at"], '%Y-%m-%dT%H:%M:%S.%f')
            return self._load(data)


class ProbitScheduler(Scheduler):
    def __init__(self, redis_connection=None, locker=None, *args, **kwargs):
        self.__redis_connection = redis_connection
        if self.__redis_connection is None:
             self.__redis_connection = StrictRedis.from_url(current_app.conf.CELERY_REDIS_SCHEDULER_URL)
        self._schedule = EntryProxy(self.__redis_connection)
        self._locker = locker
        if self._locker is None:
            self._locker = Redlock([current_app.conf.CELERY_REDIS_SCHEDULER_URL])
        super(ProbitScheduler, self).__init__(*args, **kwargs)

    def setup_schedule(self):
        self.install_default_entries(self._schedule)
        self._merge(self.app.conf.CELERYBEAT_SCHEDULE)

    def get_schedule(self):
        return self._schedule

    schedule = property(get_schedule)  # This isn't inherited anymore?  Do we want to do this?

    def sync(self):
        # Reload the schedule from the collection
        self._schedule = EntryProxy(self.__redis_connection)
    
    # I'm not sure what reserve() is intended to do, but it does not do what we
    # need it to do, so we define a _lock() method as well. 
    def maybe_due(self, entry, publisher=None):
        is_due, next_time_to_run = entry.is_due()
        if not is_due:
            return next_time_to_run
        lock = self._lock(entry.name)
        if not lock:
            return next_time_to_run
        try:
            # Now that we have the lock, double-check the timestamps on the
            # entry before executing it.
            entry = self._schedule.sync(entry.name)
            if entry is None:
                return next_time_to_run
            is_due, next_time_to_run = entry.is_due()
            if not is_due:
                return next_time_to_run
            
            return Scheduler.maybe_due(self, entry, publisher)
        finally:
            self._unlock(lock)

    def _lock(self, name):
        return self._locker.lock(name, 1000)

    def _unlock(self, lock):
        self._locker.unlock(lock)
        
    def _merge(self, schedule):
        for name, entry_dict in schedule.items():
            entry = ScheduleEntry(name, **entry_dict)
            if name not in self._schedule:
                self._schedule[name] = entry
            else:
                # _lock() the existing entry so that these values aren't changed
                # while we're merging them.
                lock = self._lock(name)
                if lock:
                    try:
                        existing = self._schedule.sync(name)
                        if existing:
                            entry.last_run_at = existing.last_run_at
                            entry.total_run_count = existing.total_run_count
                        self._schedule[name] = entry
                    finally:
                        self._unlock(lock)

def from_schedule(schedule):
    result = {}
    if isinstance(schedule, crontab):
        result['type'] = 'crontab'
        result['minute'] = schedule._orig_minute
        result['hour'] = schedule._orig_hour
        result['day_of_week'] = schedule._orig_day_of_week
    else:
        result['type'] = 'delta'
        result['days'] = schedule.run_every.days
        result['seconds'] = schedule.run_every.seconds
        result['microseconds'] = schedule.run_every.microseconds
        result['relative'] = schedule.relative
    return result

def to_schedule(dict_):
    if dict_['type'] == 'crontab':
        return crontab(dict_['minute'], dict_['hour'], dict_['day_of_week'])
    assert dict_['type'] == 'delta', dict_['type']
    delta = timedelta(dict_['days'], dict_['seconds'], dict_['microseconds'])
    return schedule(delta, dict_['relative']) 

def objISODateString(obj):
    if isinstance(obj, dict):
        for key in obj:
            obj[key] = objISODateString(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            item = objISODateString(item)
    elif isinstance(obj, datetime):
            obj = obj.isoformat()

    return obj