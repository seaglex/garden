import requests
import requests.exceptions
import threading
import sys


class ApiCaller(object):
    def __init__(self, url, thread_num, request_num, timeout):
        self.url = url
        self.thread_num = thread_num
        self.request_num = request_num
        self.timeout = timeout
        self.thread_count = 0
        self.timeout_count = 0
        self.threads = []
        self.mutex = threading.Lock()

    def call(self):
        url, num, timeout = self.url, self.request_num, self.timeout
        # offset
        self.mutex.acquire()
        self.thread_count += 1
        offset = self.thread_count * 10000
        self.mutex.release()
        timeout_cnt = 0
        for n in range(num):
            try:
                requests.get(url % (offset + n), timeout=timeout)
            except requests.exceptions.RequestException as e:
                timeout_cnt += 1
                print("Err:%s\t%s" % (url % (offset + n), e), file=sys.stderr, flush=True)
                pass
        # timeout_count
        self.mutex.acquire()
        self.timeout_count += timeout_cnt
        self.mutex.release()

    def run(self):
        threads = []
        for n in range(self.thread_num):
            t = threading.Thread(target=lambda: ApiCaller.call(self))
            threads.append(t)
        for t in threads:
            t.start()
        self.threads = threads

    def join(self):
        for t in self.threads:
            t.join()
        total_cnt = self.request_num * self.thread_num
        print("url", self.url, flush=True)
        print("call", total_cnt, flush=True)
        print("thread", self.thread_num, flush=True)
        print("timeout", self.timeout_count, "rate", self.timeout_count / total_cnt, flush=True)


def main():
    slow_url = "http://localhost:8000/flask/slow/%d"
    fast_url = "http://localhost:8000/flask/fast/%d"
    slow_caller = ApiCaller(slow_url, 2, 5, 4)
    fast_caller = ApiCaller(fast_url, 10, 10, 0.1)
    slow_caller.run()
    fast_caller.run()
    slow_caller.join()
    fast_caller.join()

if __name__ == "__main__":
    main()
