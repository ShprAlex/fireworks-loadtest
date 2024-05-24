
from typing import Optional
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

    def __init__(self, url: str, headers: dict, timeout: Optional[int]) -> None:
        self.url = url
        self.headers = headers
        if timeout == 0:
            timeout = None
        self.timeout = timeout


class Task:
    """
    Tasks are used to load a single request session. During a load test we run the task
    multiple times in parallel.
    """

    def __init__(self, session_config: SessionConfig) -> None:
        self.session_config = session_config
        self.start_time = None
        self.end_time = None
        self.status = None
        self.thread = None

    def _load(self) -> None:
        self.start_time = time.time()
        try:
            raise requests.exceptions.Timeout
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
    """
    The Loader creates a list of Tasks for a given SessionConfig.

    We start each task in its own Thread.

    Args:
        session_config (SessionConfig): Info about the web requests we're making for the session,
            for now we only support loading one URL per session.
        qps (int): Queries Per Second
        duration (int): How many seconds to run the load test for.
    """

    def __init__(self, session_config: SessionConfig, qps: int = 100, duration: int = 1) -> None:
        self.tasks = []
        self.session_config = session_config
        self.qps = qps
        self.duration = duration
        self.start_time = None
        self.end_time = None

    def get_rate_limited_max_task_count(self) -> float:
        """
        Calculate how many requests we should have made by this time assuming an even request rate.
        We use this value to limit our request rate to match the desired QPS.
        """
        elapsed_seconds = time.time()-self.start_time
        return elapsed_seconds*self.qps

    def start(self) -> None:
        """
        Start multiple tasks at a rate of QPS. This function waits for the task threads
        to finish and returns.
        """
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
