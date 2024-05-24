
def get_stats(tasks):
    task_count = len(tasks)
    avg_response_time = 0

    # group response statuses starting with 100, 200, etc.
    response_statuses = [0]*8
    status_percents = [0]*8

    if task_count > 0:
        response_times = [
            task.end_time - task.start_time for task in tasks
        ]
        for task in tasks:
            status = task.status
            response_statuses[status//100] += 1
        avg_response_time = sum(response_times)/task_count
        status_percents = [
            status_count / task_count for status_count in response_statuses
        ]

    return {
        "task_count": task_count,
        "avg_response_time": avg_response_time,
        "status_percents": status_percents,
        # 100, 200, and 300 http status response
        "success": status_percents[1] + status_percents[2] + status_percents[3],
        # 400 errors, 500 errors, and "600" status indicating connection error
        "error": status_percents[4] + status_percents[5] + status_percents[6],
        # Track forced timeouts "700" from our side separately
        "timeout": status_percents[7]
    }


def group_completed_tasks_into_batches(loader, batch_duration=0.1):
    batch_start_time = loader.start_time
    batches = []
    task_index = 0
    while batch_start_time < loader.start_time+loader.duration:
        batch = []
        batches.append(batch)
        while task_index < len(loader.tasks):
            task = loader.tasks[task_index]
            if task.start_time < batch_start_time+batch_duration:
                batch.append(task)
                task_index += 1
            else:
                break
        batch_start_time += batch_duration

    if len(batches[-1]) == 0:
        # if all the requests fit neatly into the allotted duration we don't need
        # a trailing empty batch.
        batches.pop()

    return batches


def get_stats_in_batches(loader, batch_duration=0.1):
    task_batches = group_completed_tasks_into_batches(
        loader, batch_duration)

    return [get_stats(batch) for batch in task_batches]
