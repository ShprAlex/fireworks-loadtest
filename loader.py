
import requests
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class RequestsErrorStatus:
    """
    This lets us report on errors with ULR requests as if they were HTTP response codes.
    """
    CONNECTION_ERROR = 600
    TIME_OUT = 700


class SessionConfig:
    """
    SessionConfig contains information about the URLs we're visiting during a single
    loader session. This includes the request headers, and a request timeout.

    For now we only support visiting one URL during a session, but this class
    can be updated to support visiting multiple urls in a single pass.
    """

    def __init__(self, session_config, timeout):
        self.url = session_config[0]["url"]
        self.headers = session_config[0]["headers"]
        if timeout == 0:
            timeout = None
        self.timeout = timeout


class Task:
    def __init__(self, session_config):
        """
        Initialize a task that will be used to load a single request session.

        Args:
            session_config (SessionConfig): Info about the requests we're making during this task.
        """
        self.session_config = session_config
        self.start_time = None
        self.end_time = None
        self.status = None
        self.thread = None

    def _load(self):
        self.start_time = time.time()
        try:
            response = requests.get(
                self.session_config.url,
                headers=self.session_config.headers,
                timeout=self.session_config.timeout
            )
            self.status = response.status_code
        except requests.exceptions.ConnectionError as error:
            self.status = RequestsErrorStatus.CONNECTION_ERROR
            logger.warning(error)
        except requests.exceptions.Timeout:
            self.status = RequestsErrorStatus.TIME_OUT

        self.end_time = time.time()

    def start(self):
        self.thread = threading.Thread(target=self._load)
        self.thread.start()


class Loader:
    def __init__(self, session_config, qps=100, duration=1):
        self.tasks = []
        self.session_config = session_config
        self.qps = qps
        self.duration = duration
        self.start_time = None
        self.end_time = None

    def get_rate_limited_max_task_count(self):
        elapsed_seconds = time.time()-self.start_time
        return elapsed_seconds*self.qps

    def start(self):
        self.start_time = time.time()
        logger.info(f"Started loader")
        task_count = 0
        expected_end_time = self.start_time+self.duration
        expected_task_count = self.qps*self.duration
        # we're calling tasks at an even rate but for tidy accounting make sure we reach
        # expected_task_count with the very last batch which might take an extra millisecond.
        while time.time() < expected_end_time or task_count < expected_task_count:
            if task_count > self.get_rate_limited_max_task_count():
                # sleep for 1ms to save CPU cycles
                # this still allows us to request more than 1000 times a second because
                # multiple requests will happen after we wake up
                time.sleep(0.001)
                continue
            task = Task(self.session_config)
            self.tasks.append(task)
            task.start()
            task_count += 1
            if task_count % self.qps == 0:
                logger.info(
                    f"Started {task_count} tasks as of {time.time()-self.start_time:.2f}s"
                )

        for task in self.tasks:
            task.thread.join()

        logger.info(
            f"Completed {task_count} tasks in {time.time()-self.start_time:.2f}s"
        )

        # for the Loader we consider the end_time to be the start_time of
        # the last tasks (not how long it takes requests to complete)
        self.end_time = max([task.start_time for task in self.tasks])
