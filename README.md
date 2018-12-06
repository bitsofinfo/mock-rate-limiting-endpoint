# mock-rate-limiting-endpoint

Simple mock endpoint that simulates a rate limiting endpoint. Useful for testing
clients and how they interact with a rate limited API.

Python 3+, and `pip twisted ratelimit`

Customizable: See usage and examples below for details.

## Docker file

```
docker build -t mock-rate-limiting-endpoint:latest .

docker run -p 8081:8081mock-rate-limiting-endpoint:latest endpoint.py
```

## Usage
```
$> python3 endpoint.py -h

usage: endpoint.py [-h] [-p LISTEN_PORT] [-m MAX_CALLS] [-P PERIOD_SECONDS]
                   [-r RETRY_IN_SECONDS] [-c LIMIT_HIT_RESPONSE_CODE]
                   [-a RETRY_AFTER_HEADER_NAME]

optional arguments:
  -h, --help            show this help message and exit
  -p LISTEN_PORT, --listen-port LISTEN_PORT
                        Port to listen on, default 8081
  -m MAX_CALLS, --max-calls MAX_CALLS
                        Max calls for the rate limiter over the specified
                        --period-seconds, Default 1
  -P PERIOD_SECONDS, --period-seconds PERIOD_SECONDS
                        Period in seconds that the --max-calls will apply for,
                        Default 10
  -r RETRY_IN_SECONDS, --retry-in-seconds RETRY_IN_SECONDS
                        Value for the --retry-after-header-name argument which
                        is returned when the rate limit has been reached,
                        default 10
  -c LIMIT_HIT_RESPONSE_CODE, --limit-hit-response-code LIMIT_HIT_RESPONSE_CODE
                        Default 429
  -a RETRY_AFTER_HEADER_NAME, --retry-after-header-name RETRY_AFTER_HEADER_NAME
                        Default Retry-After

```

## Examples

Start in a shell, logs to stdout
```
./python3 endpoint.py

2018-12-06 19:33:07,535 - root - DEBUG - Starting with config: {"listen_port": 8081, "max_calls": 1, "period_seconds": 10, "retry_in_seconds": 10, "limit_hit_response_code": 429, "retry_after_header_name": "Retry-After"}
...
2018-12-06 19:53:08,561 - root - DEBUG - GET / : {"path": "/", "status_code": 200, "msg": "OK", "total_reqs": 1, "total_ok": 1, "total_limit_hits": 0}
2018-12-06 19:53:09,339 - root - DEBUG - GET / : {"path": "/", "status_code": 429, "msg": "429: rate limit hit max_calls:1 period_seconds:10", "retry_in_seconds":
10, "retry_after_header_name": "Retry-After", "total_reqs": 2, "total_ok": 1, "total_limit_hits": 1}
```

In another shell make a request
```
bash-4.4$ curl http://localhost:8081
{
  "path": "/",
  "status_code": 200,
  "msg": "OK",
  "total_reqs": 1,
  "total_ok": 1,
  "total_limit_hits": 0
}
```

Make a 2nd request
```
bash-4.4$ curl -v  http://127.0.0.1:8081
* ...
>
< HTTP/1.1 429 Unknown Status
< Server: TwistedWeb/18.9.0
< Date: Thu, 06 Dec 2018 19:41:06 GMT
< Retry-After: 10
< Content-Length: 232
< Content-Type: text/html
<
{
  "path": "/",
  "status_code": 429,
  "msg": "429: rate limit hit max_calls:1 period_seconds:10",
  "retry_in_seconds": 10,
  "retry_after_header_name": "Retry-After",
  "total_reqs": 3,
  "total_ok": 2,
  "total_limit_hits": 1
}
```

Wait 10s for 3rd request:
```
bash-4.4$ curl http://localhost:8081
{
  "path": "/",
  "status_code": 200,
  "msg": "OK",
  "total_reqs": 3,
  "total_ok": 2,
  "total_limit_hits": 1
}
```

You can send any args for tracking i.e:
```
bash-4.4$ curl http://localhost:8081?callerid=99191
{
  "path": "/",
  "status_code": 200,
  "msg": "OK",
  "total_reqs": 5,
  "total_ok": 4,
  "total_limit_hits": 1,
  "args": [
    {
      "callerid": "99191"
    }
  ]
}
```

...Or override the the rate limit hit status code and response header:
```
bash-4.4$ curl -v http://localhost:8081?limit_hit_response_code=999\&retry_after_header_name=X-Custom-Retry
...
>
< HTTP/1.1 999 Unknown Status
< Server: TwistedWeb/18.9.0
< Date: Thu, 06 Dec 2018 19:50:01 GMT
< X-Custom-Retry: 10
< Content-Length: 366
< Content-Type: text/html
<
{
  "path": "/",
  "status_code": 999,
  "msg": "999: rate limit hit max_calls:1 period_seconds:10",
  "retry_in_seconds": 10,
  "retry_after_header_name": "X-Custom-Retry",
  "total_reqs": 5,
  "total_ok": 2,
  "total_limit_hits": 3,
  "args": [
    {
      "limit_hit_response_code": "999"
    },
    {
      "retry_after_header_name": "X-Custom-Retry"
    }
  ]
}
```
