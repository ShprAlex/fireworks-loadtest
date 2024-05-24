from loader import Loader, RequestConfig
from stats import get_stats_in_batches


def print_results(loader):
    batch_duration = 0.1
    stats_in_batches = get_stats_in_batches(loader, batch_duration)
    elapsed_time = batch_duration
    for stats in stats_in_batches:
        pass_count = stats["pass_count"]
        avg_response_time = stats["avg_response_time"]
        status_percents = stats["status_percents"]

        print(f"Time {elapsed_time}, Request count {pass_count}, Response time {avg_response_time}, Statuses {status_percents}")
        elapsed_time += batch_duration


def main():
    request_config = RequestConfig("http://example.com", timeout=1)
    loader = Loader(request_config, duration=5)
    loader.start()
    print_results(loader)


if __name__ == "__main__":
    main()
