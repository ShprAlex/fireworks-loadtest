import requests
import threading
import time
from collections import defaultdict

urls = [
    'http://example.com',
    'http://example.org',
    'http://example.net',
]


class LoadTester:

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


def main():
    load_tester = LoadTester()
    for url in urls:
        for i in range(50):
            load_tester.load_url(url)

    load_tester.wait_to_finish()

    print("\nLoad times:")
    for url, load_time in load_tester.load_times.items():
        print(f"{url}: {[int(t*1000) for t in load_time]} ms")


if __name__ == "__main__":
    main()
