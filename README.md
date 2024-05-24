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
docker run --rm alex-shapiro-fireworks-loadtest --url https://www.walmart.com/ --qps 50 --duration 10 
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
```

## Script output explanation

Sample output:
```
INFO:loader:Started loader

Load testing https://www.walmart.com/ for 5s at 80 QPS.

INFO:loader:Started 80 tasks as of 0.99s
INFO:loader:Started 160 tasks as of 1.99s
INFO:loader:Started 240 tasks as of 2.99s
INFO:loader:Started 320 tasks as of 3.99s
INFO:loader:Started 400 tasks as of 4.99s
INFO:loader:Completed 400 tasks in 13.85s

Performance over time:
Time  1.00s, Request count   80, Avg resp time  1.634s Success 100%, Error   0%, Timeout   0%
Time  2.00s, Request count   80, Avg resp time  5.559s Success 100%, Error   0%, Timeout   0%
Time  3.00s, Request count   80, Avg resp time  5.475s Success 100%, Error   0%, Timeout   0%
Time  4.00s, Request count   80, Avg resp time  4.777s Success 100%, Error   0%, Timeout   0%
Time  5.00s, Request count   80, Avg resp time  4.177s Success 100%, Error   0%, Timeout   0%

Summary:
Time  4.99s, Request count  400, Avg resp time  4.324s Success 100%, Error   0%, Timeout   0%
```

The sript runs a series of threads in parallel and waits for all the requests to finish, then prints the statistics.

### Output - Performance over time
* Time: 1 second window over which the requests occurred.
* Request count: How many requests were made during the winow, can vary slightly for high request rates.
* Avg resp time: The time it took for requests started during this time window to respond.
* Success: 200 HTTP response statuses (also 100 and 300 statuses)
* Error: 400 and 500 HTTP response statuses
* Timeout: We can intentionally terminate long waiting requests from our end, this reports those cases.

### Output - Summary
* Time: This is the window during which the requests were started, they may have taken longer to complete
* Request count: The total number of requests performed
* The other metrics are the same as for performance over time

## Design Decisions

Python muti-threading seems good enough for simple load testing.

Multi-threading was able to handle 10,000 requests a second on a macbook, so this should be reasonable in practice. For larger request volumes we can introduce multi-processing and otherwise try to scale the application horizontally.

A decision was made to specify the time window during which the requests were started, and allow time for requests to finish even if that takes longer than the window duration. Alternatively we could have terminated the ongoing requests at the conclusion of the time window. The former approach seems to create nicer results where we know how many requests we'll be making.

## Potential enhancements

* The loader test outputs are simply printed to standard out. The results could be written to an output file or a database.

* We could support other types of load tests like increasing the QPS over time to determine when we get a high error rate.

* We could terminate the test early if we see a high error rate.

* We could support visiting multiple URLs in a session and having the output of one page visit be an input to the request to the following pages.
