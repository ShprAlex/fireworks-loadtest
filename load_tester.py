from loader import Loader, RequestConfig
from stats import get_stats, get_stats_in_batches


def print_stats(stats, elapsed_time):
    pass_count = stats["pass_count"]
    avg_response_time = stats["avg_response_time"]
    success = stats["success"]
    error = stats["error"]
    timeout = stats["timeout"]

    print(
        f"Time {elapsed_time:.2f}s, Request count {pass_count:4d}, Avg resp time {avg_response_time:.3f}s "
        f"Success {success*100:3.0f}%, Error {error*100:3.0f}%, Timeout {timeout*100:3.0f}%"
    )


def print_results(loader):
    batch_duration = 0.1
    stats_in_batches = get_stats_in_batches(loader, batch_duration)
    for batch_index, stats in enumerate(stats_in_batches):
        elapsed_time = (batch_index+1)*batch_duration
        print_stats(stats, elapsed_time)

    print("\nSummary:")
    print_stats(
        get_stats(loader.request_passes), loader.end_time-loader.start_time
    )


def main():
    request_config = RequestConfig("http://example.com", timeout=1)
    loader = Loader(request_config, duration=2)
    loader.start()
    print_results(loader)


if __name__ == "__main__":
    main()
