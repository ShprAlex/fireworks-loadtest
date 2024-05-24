
import requests
import threading
import time

TIME_OUT_STATUS = 600


class RequestPass:
    def __init__(self, url, timeout=None):
        """
        Initialize a single request pass.

        Args:
            url (str): the url we're loading
            timeout (Optional[float]): how long we're willing to wait for the request to load
                or None if unlimited.
        """
        self.url = url
        self.timeout = timeout
        self.start_time = None
        self.end_time = None
        self.status = None
        self.thread = None

    def load(self):
        self.start_time = time.time()
        try:
            response = requests.get(self.url, timeout=self.timeout)
            self.status = response.status_code
        except requests.exceptions.Timeout:
            self.status = TIME_OUT_STATUS

        self.end_time = time.time()

    def start(self):
        self.thread = threading.Thread(target=self.load)
        self.thread.start()


class Loader:
    def __init__(self, url, qps=1000, duration=1, timeout=3):
        self.request_passes = []
        self.timeout = timeout
        self.url = url
        self.qps = qps
        self.duration = duration
        self.start_time = None
        self.end_time = None

    def get_rate_limited_max_request_count(self):
        elapsed_seconds = time.time()-self.start_time
        return elapsed_seconds*self.qps

    def start(self):
        self.start_time = time.time()
        pass_count = 0
        expected_end_time = self.start_time+self.duration
        # we're making requests at an even rate but for tidy accounting make sure we reach
        # expected_pass_count with the very last batch which might take an extra millisecond.
        expected_pass_count = self.qps*self.duration
        while time.time() < expected_end_time or pass_count < expected_pass_count:
            if pass_count > self.get_rate_limited_max_request_count():
                # sleep for 1ms to save CPU cycles
                # this still allows us to request more than 1000 times a second because
                # multiple requests will happen after we wake up
                time.sleep(0.001)
                continue
            request_pass = RequestPass(self.url, timeout=self.timeout)
            self.request_passes.append(request_pass)
            request_pass.start()
            pass_count += 1

        print(time.time(), pass_count)

        for lr in self.request_passes:
            lr.thread.join()
