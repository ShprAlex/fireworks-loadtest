
import requests
import threading
import time


class LoaderRequest:
    def __init__(self, url):
        self.url = url
        self.start_time = None
        self.end_time = None
        self.status = None
        self.thread = None

    def load(self):
        self.start_time = time.time()
        response = requests.get(self.url)
        self.end_time = time.time()
        self.status = response.status_code

    def start(self):
        self.thread = threading.Thread(target=self.load)
        self.thread.start()


class Loader:
    def __init__(self, url, qps=1000, duration=1):
        self.loader_requests = []
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
            loader_request = LoaderRequest(self.url)
            self.loader_requests.append(loader_request)
            loader_request.start()
            count += 1

        print(time.time())

        for lr in self.loader_requests:
            lr.thread.join()
