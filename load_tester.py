import argparse
import json
import os
from loader import Loader, SessionConfig
from stats import get_stats, get_stats_in_batches


def print_stats(stats, elapsed_time):
    task_count = stats["task_count"]
    avg_response_time = stats["avg_response_time"]
    success = stats["success"]
    error = stats["error"]
    timeout = stats["timeout"]

    print(
        f"Time {elapsed_time:5.2f}s, Request count {task_count:4d}, Avg resp time {avg_response_time:6.3f}s "
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
        get_stats(loader.tasks), loader.end_time-loader.start_time
    )


def load_config(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, "r") as file:
        config = json.load(file)

    return config


def main(config):
    session_config = SessionConfig(config["session"], timeout=10)
    loader = Loader(session_config, duration=12, qps=10)
    loader.start()
    print_results(loader)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-config", default="config.json", type=str, help="Path to the config file"
    )
    args = parser.parse_args()
    config_file = args.config
    config = load_config(config_file)

    main(config)
