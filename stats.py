"""
stats.py helps compile stats for loader performance overall, and broken down by time.
"""

import math
from typing import List

from loader import Task


def get_stats(tasks: List[Task]) -> dict:
    task_count = len(tasks)
    avg_response_time = 0
    max_response_time = 0

    # group response statuses starting with 100, 200, etc.
    response_statuses = [0]*8
    status_percents = [0]*8

    if task_count > 0:
        response_times = [
            task.end_time - task.start_time for task in tasks
        ]
        for task in tasks:
            response_statuses[task.status//100] += 1
        avg_response_time = sum(response_times)/task_count
        max_response_time = max(response_times)
        status_percents = [
            status_count / task_count for status_count in response_statuses
        ]

    return {
        "task_count": task_count,
        "avg_response_time": avg_response_time,
        "max_response_time": max_response_time,
        "status_percents": status_percents,
        # 100, 200, and 300 http status response
        "success": status_percents[1] + status_percents[2] + status_percents[3],
        # 400 errors, 500 errors, and "600" status indicating connection error
        "error": status_percents[4] + status_percents[5] + status_percents[6],
        # Track forced timeouts "700" from our side separately
        "timeout": status_percents[7]
    }


def group_completed_tasks_into_batches(loader, batch_duration: float = 0.1) -> List[List[Task]]:
    batch_count = math.ceil(
        (loader.end_time - loader.start_time)/batch_duration
    )
    batches = [[] for _ in range(batch_count)]
    for task in loader.tasks:
        batch_index = int((task.start_time-loader.start_time) / batch_duration)
        batches[batch_index].append(task)

    return batches


def get_stats_in_batches(loader, batch_duration: float = 0.1) -> List[dict]:
    task_batches = group_completed_tasks_into_batches(
        loader, batch_duration)

    return [get_stats(batch) for batch in task_batches]
