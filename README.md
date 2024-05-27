# Fireworks Load Test Assignment

## Author 

Alex Shapiro <shapiro.alex@gmail.com>

May 24, 2024

## Installing

This python script can be installed and run using a docker image:

```
docker build -t alex-shapiro-fireworks-loadtest .
docker run --rm alex-shapiro-fireworks-loadtest
```

## Running

By default we use the parameters from `config.json` included in the distribution.
* If config.json is changed you need to rebuild the image to activate the changes.

The script supports a number of command-line parameters that can be used directly.

```
Example:
docker run --rm alex-shapiro-fireworks-loadtest --url https://www.target.com/ --qps 50 --duration 10
```

Supported Options:
```
--config CONFIG      Path to config file containing session URLs and
                     headers.

--qps QPS            Queries per second.

--duration DURATION  Loadtest duration is seconds.

--timeout TIMEOUT    Force timeout if page doesn't load within this many
                     seconds. Zero for no timeout.

--url URL            URL to load test, uses headers from config file.

--debug              Debug mode has more verbose logging.
```

## Script output explanation

Sample output:
```
Load testing https://www.target.com/ for 5s at 60 QPS.

INFO:loader:Started loader
INFO:loader:Started 60 tasks as of 0.98s - Live thread count 41, Mem usage 2735 KiB
INFO:loader:Started 120 tasks as of 1.99s - Live thread count 57, Mem usage 3261 KiB
INFO:loader:Started 180 tasks as of 2.99s - Live thread count 67, Mem usage 4097 KiB
INFO:loader:Started 240 tasks as of 3.99s - Live thread count 81, Mem usage 7813 KiB
INFO:loader:Started 300 tasks as of 4.99s - Live thread count 86, Mem usage 8060 KiB
INFO:loader:Completed 300 tasks in 6.59s

Performance over time:
Time  1.00s, Request count   60, Avg resp time  0.729s, Max  1.451s, Success 100%, Error   0%, Timeout   0%
Time  2.00s, Request count   60, Avg resp time  1.096s, Max  1.719s, Success 100%, Error   0%, Timeout   0%
Time  3.00s, Request count   60, Avg resp time  1.274s, Max  1.729s, Success 100%, Error   0%, Timeout   0%
Time  4.00s, Request count   60, Avg resp time  1.344s, Max  2.330s, Success 100%, Error   0%, Timeout   0%
Time  5.00s, Request count   60, Avg resp time  1.476s, Max  1.783s, Success 100%, Error   0%, Timeout   0%

Summary:
Time  4.98s, Request count  300, Avg resp time  1.184s, Max  2.330s, Success 100%, Error   0%, Timeout   0%
```

The script runs a series of threads in parallel and waits for all the requests to finish, then prints the statistics.

### Output - Performance over time
* Time: 1 second window over which the requests occurred.
* Request count: How many requests were made during the window, can vary slightly for high request rates.
* Avg resp time: The average time it took requests started during this time window to respond.
* Max: The maximum time it took for a request during this time window to respond.
* Success: 200 HTTP response statuses (also 100 and 300 statuses)
* Error: 400 and 500 HTTP response statuses
* Timeout: We can intentionally terminate long waiting requests from our end, this reports those cases.

### Output - Summary
* Time: The total time during which requests were started, they may have taken longer to complete.
* Request count: The total number of requests performed.
* The other metrics are the same as for performance over time.

## Design Decisions

Python multi-threading is good enough for simple load testing.

Experimentation shows we can handle 1,000 requests a second on a macbook. At a requested QPS of above 2,000 we start getting a lag where we can't generate threads with requests at this rate. The limiting factor seems to be the python requests library, or some system limitation on how fast we can create requests. To handle larger request volumes we can introduce multi-processing and otherwise try to scale the application horizontally.

A decision was made to specify the time window during which the requests were started, and allow for requests to finish beyond the window duration. Alternatively we could have terminated the ongoing requests at the conclusion of the time window. The former approach seems to create nicer results where we know how many requests we'll be making. The time it takes to finish is roughly equal to the requested duration + max response time.

## Potential enhancements

* The loader test outputs are simply printed to standard out. The results could be written to an output file or a database.

* We could support other types of load tests like increasing the QPS over time. We could then benchmark the rate at which we get a high error rate.

* We could terminate the test early if we see a high error rate.

* We could support visiting multiple URLs in a session and having the output of one page visit be an input to the request to the following pages.

## Testing

A test is included, it can be run as follows.

```
pipenv install --dev
pipenv run pytest
```
