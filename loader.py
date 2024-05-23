
import requests
import threading
import time

TIME_OUT_STATUS = 600


class LoaderRequest:
    def __init__(self, url, timeout=None):
        """
        Initialize a loader request

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
    def __init__(self, url, qps=1000, duration=1, timeout=None):
        self.loader_requests = []
        self.timeout = timeout
        self.url = url
        self.qps = qps
        self.duration = duration
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()
        count = 0
        print(self.start_time)
        while time.time() < self.start_time+self.duration and count < 1000:
            loader_request = LoaderRequest(self.url, timeout=self.timeout)
            self.loader_requests.append(loader_request)
            loader_request.start()
            count += 1

        print(time.time())

        for lr in self.loader_requests:
            lr.thread.join()
