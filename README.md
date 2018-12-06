# mock-rate-limiting-endpoint


## Usage
```
$> python3 endpoint.py -h

usage: endpoint.py [-h] [-p LISTEN_PORT] [-m MAX_CALLS] [-P PERIOD_SECONDS]
                  [-r RETRY_SECONDS] [-c LIMIT_HIT_RESPONSE_CODE]

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

  -r RETRY_SECONDS, --retry-seconds RETRY_SECONDS
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

2018-12-06 19:09:16,171 - root - DEBUG - Starting with config: {"listen_port": 8081, "max_calls": 1, "period_seconds": 10, "retry_seconds": 10, "limit_hit_response_code": 429, "retry_after_header_name": "Retry-After"}
```

In another shell:
```
# make a request
bash-4.4$ curl http://localhost:8081
{
  "path": "/",
  "status_code": 200,
  "msg": "OK",
  "total_reqs": 1,
  "total_ok": 1,
  "total_limit_hits": 0
}

# make a 2nd request
bash-4.4$ curl http://localhost:8081
{
  "path": "/",
  "status_code": 429,
  "msg": "429: rate limit hit max_calls:1 period_seconds:10",
  "retry_in_seconds": 30,
  "retry_after_header_name": "Retry-After",
  "total_reqs": 2,
  "total_ok": 1,
  "total_limit_hits": 1
}

# Wait 10s for 3rd
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
