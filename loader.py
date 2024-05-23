
import requests
import threading
import time
from collections import defaultdict


class Loader:

    def __init__(self):
        self.load_times = defaultdict(list)
        self.threads = []

    def _load_url(self, url):
        start_time = time.time()
        response = requests.get(url)
        load_time = time.time() - start_time
        self.load_times[url].append(load_time)
        print(f"Loaded {url} in {load_time:.2f} seconds")

    def load_url(self, url):
        thread = threading.Thread(target=self._load_url, args=(url,))
        self.threads.append(thread)
        thread.start()

    def wait_to_finish(self):
        for thread in self.threads:
            thread.join()
