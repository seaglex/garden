import datetime as dt
import threading
import time
import sys

class PeriodicAlarm(object):
    def __init__(self, period_seconds):
        self._lock = threading.Lock()
        self._period_seconds = period_seconds
        self._set_timer()

    def _set_timer(self):
        self._timer = threading.Timer(self._period_seconds, self.alarm)
        self._timer.setDaemon(True)
        self._timer.start()

    def alarm(self):
        try:
            print("start...")
            time.sleep(2)
            now = dt.datetime.now()
            cur_thread = threading.current_thread()
            print("end", now, cur_thread.ident, cur_thread.getName(), cur_thread.isDaemon())
        except Exception as e:
            print("exception caugth:", e, file=sys.stderr)
        self._set_timer()

    def stop(self):
        self._timer.cancel()

if __name__ == "__main__":
    alarm = PeriodicAlarm(3)
    print(dt.datetime.now(), "main thread started")
    try:
        time.sleep(60)
    except Exception as e:
        print("exception caught in main:", e, file=sys.stderr)
    # alarm.stop()
