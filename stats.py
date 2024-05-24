
def get_stats(request_passes):
    pass_count = len(request_passes)
    avg_response_time = 0

    # group response statuses starting with 100, 200, etc.
    response_statuses = [0]*6
    status_percents = [0]*6

    if pass_count > 0:
        response_times = [
            lr.end_time - lr.start_time for lr in request_passes
        ]
        for request_pass in request_passes:
            status = request_pass.status
            response_statuses[status//100-1] += 1
        avg_response_time = sum(response_times)/pass_count
        status_percents = [
            status_count / pass_count for status_count in response_statuses
        ]

    return {
        "pass_count": pass_count,
        "avg_response_time": avg_response_time,
        "status_percents": status_percents
    }


def group_completed_requests_into_batches(loader, batch_duration=0.1):
    batch_start_time = loader.start_time
    batches = []
    request_index = 0
    while batch_start_time < loader.start_time+loader.duration:
        batch = []
        batches.append(batch)
        while request_index < len(loader.request_passes):
            request_pass = loader.request_passes[request_index]
            if request_pass.start_time < batch_start_time+batch_duration:
                batch.append(request_pass)
                request_index += 1
            else:
                break
        batch_start_time += batch_duration

    if len(batches[-1]) == 0:
        # if all the requests fit neatly into the allotted duration we don't need
        # a trailing empty batch.
        batches.pop()

    return batches


def get_stats_in_batches(loader, batch_duration=0.1):
    request_batches = group_completed_requests_into_batches(
        loader, batch_duration)

    return [get_stats(batch) for batch in request_batches]
