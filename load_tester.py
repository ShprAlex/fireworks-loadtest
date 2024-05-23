from loader import Loader
from stats import get_stats_in_batches


def print_results(loader):
    batch_duration = 0.1
    stats_in_batches = get_stats_in_batches(loader, batch_duration)
    elapsed_time = batch_duration
    for stats in stats_in_batches:
        request_count = stats["request_count"]
        avg_response_time = stats["avg_response_time"]
        status_percents = stats["status_percents"]

        print(f"Time {elapsed_time}, Request count {request_count}, Response time {avg_response_time}, Statuses {status_percents}")
        elapsed_time += batch_duration


def main():
    loader = Loader("http://example.com", duration=5, timeout=1)
    loader.start()
    print_results(loader)
    # print("\nLoad times:")
    # for lr in loader.loader_requests:
    #     print(int((lr.end_time - lr.start_time)*1000), lr.end_time, lr.status)


if __name__ == "__main__":
    main()
