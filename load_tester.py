import argparse
import json
import os
from typing import Optional
from loader import Loader, SessionConfig
from stats import get_stats, get_stats_in_batches


def print_stats(stats, elapsed_time: float) -> None:
    task_count = stats["task_count"]
    avg_response_time = stats["avg_response_time"]
    success = stats["success"]
    error = stats["error"]
    timeout = stats["timeout"]

    print(
        f"Time {elapsed_time:5.2f}s, Request count {task_count:4d}, Avg resp time {avg_response_time:6.3f}s "
        f"Success {success*100:3.0f}%, Error {error*100:3.0f}%, Timeout {timeout*100:3.0f}%"
    )


def print_results(loader: Loader) -> None:
    # we could set this to 0.1 seconds for fine grained reporting.
    batch_duration = 1
    stats_in_batches = get_stats_in_batches(loader, batch_duration)

    print("\nPerformance over time:")

    for batch_index, stats in enumerate(stats_in_batches):
        elapsed_time = (batch_index+1)*batch_duration
        print_stats(stats, elapsed_time)

    print("\nSummary:")
    print_stats(
        get_stats(loader.tasks), loader.end_time-loader.start_time
    )


def load_config(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, "r") as file:
        config = json.load(file)

    return config


def main(config: dict, qps: int, duration: int, timeout: int, url: Optional[str]) -> None:
    if url is None:
        url = config["session"][0]["url"]
    headers = config["session"][0]["headers"]
    # SessionConfig is designed for easier testing from the command line
    session_config = SessionConfig(url=url, headers=headers, timeout=timeout)
    loader = Loader(session_config, duration=duration, qps=qps)

    print(
        f"\nLoad testing {loader.session_config.url} for {duration}s at {qps} QPS.\n"
    )

    loader.start()
    print_results(loader)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str, default="config.json", help="Path to config file containing session URLs and headers."
    )
    parser.add_argument(
        "--qps", type=int, default=None, help="Queries per second."
    )
    parser.add_argument(
        "--duration", type=int, default=None, help="Loadtest duration is seconds."
    )
    parser.add_argument(
        "--timeout", type=int, default=None, help="Force timeout if page doesn't load within this many seconds. Zero for no timeout."
    )
    parser.add_argument(
        "--url", type=str, default=None, help="URL to load test, uses headers from config file."
    )
    args = parser.parse_args()
    config_file = args.config
    config = load_config(config_file)

    qps = args.qps if args.qps is not None else config["qps"]
    duration = args.duration if args.duration is not None else config["duration"]
    timeout = args.timeout if args.timeout is not None else config["timeout"]

    main(config=config, qps=qps, duration=duration, timeout=timeout, url=args.url)
