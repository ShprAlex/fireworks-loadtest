
import requests
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

TIME_OUT_STATUS = 600


class RequestConfig:
    """
    RequestConfig contains information about the URLs we're visiting during a single
    loader pass. This includes the request headers, and a request timeout.

    For now we only support visiting one URL during a loader pass, but this class
    can be updated to support visiting multiple urls in a single pass.
    """

    def __init__(self, url, timeout=None):
        self.url = url
        self.timeout = timeout


class RequestPass:
    def __init__(self, request_config):
        """
        Initialize a single request pass.

        Args:
            request_config (RequestConfig): Info about the request we're making over the pass.
        """
        self.request_config = request_config
        self.start_time = None
        self.end_time = None
        self.status = None
        self.thread = None

    def load(self):
        self.start_time = time.time()
        try:
            response = requests.get(
                self.request_config.url, timeout=self.request_config.timeout
            )
            self.status = response.status_code
        except requests.exceptions.Timeout:
            self.status = TIME_OUT_STATUS

        self.end_time = time.time()

    def start(self):
        self.thread = threading.Thread(target=self.load)
        self.thread.start()


class Loader:
    def __init__(self, request_config, qps=1000, duration=1):
        self.request_passes = []
        self.request_config = request_config
        self.qps = qps
        self.duration = duration
        self.start_time = None
        self.end_time = None

    def get_rate_limited_max_request_count(self):
        elapsed_seconds = time.time()-self.start_time
        return elapsed_seconds*self.qps

    def start(self):
        self.start_time = time.time()
        logger.info(f"Started loader")
        pass_count = 0
        expected_end_time = self.start_time+self.duration
        expected_pass_count = self.qps*self.duration
        # we're making requests at an even rate but for tidy accounting make sure we reach
        # expected_pass_count with the very last batch which might take an extra millisecond.
        while time.time() < expected_end_time or pass_count < expected_pass_count:
            if pass_count > self.get_rate_limited_max_request_count():
                # sleep for 1ms to save CPU cycles
                # this still allows us to request more than 1000 times a second because
                # multiple requests will happen after we wake up
                time.sleep(0.001)
                continue
            request_pass = RequestPass(self.request_config)
            self.request_passes.append(request_pass)
            request_pass.start()
            pass_count += 1
            if pass_count % 1000 == 0:
                logger.info(
                    f"Started {pass_count} requests at {time.time()-self.start_time:.2f}s"
                )

        for lr in self.request_passes:
            lr.thread.join()

        logger.info(
            f"Completed {pass_count} requests at {time.time()-self.start_time:.2f}s"
        )

        # for the Loader we consider the end_time to be the start_time of
        # the last request (not how long it takes requests to complete)
        self.end_time = max([rp.start_time for rp in self.request_passes])
