#!/usr/bin/env python

__author__ = "bitsofinfo"

from twisted.web import server, resource
from twisted.internet import reactor, endpoints
from ratelimit import limits, RateLimitException
import time
import threading
import logging
import json
import argparse

# The MockRateLimitingEndpoint impl
class MockRateLimitingEndpoint(resource.Resource):
    isLeaf = True
    total_reqs = 0
    total_ok = 0
    total_limit_hits = 0

    max_calls= 1
    period_seconds = 10
    retry_in_seconds = 30
    limit_hit_response_code = 429

    # Default: https://tools.ietf.org/html/rfc7231#section-7.1.3
    retry_after_header_name = "Retry-After"

    # The function actually enforcing the rate limits configured
    @limits(calls=max_calls, period=period_seconds)
    def endpoint(self):
        return "OK"

    def render_GET(self, request):
        self.total_reqs += 1

        curr_retry_header_name = self.retry_after_header_name;
        curr_limit_hit_response_code = self.limit_hit_response_code
        toReturn = {'path':request.path.decode("UTF-8")}

        # Override the retry_after_header_name
        if request.args.get(b'retryHeaderName'):
            curr_retry_header_name = request.args.get(b'retryHeaderName')[0].decode('utf-8')

        # Override the limit_hit_response_code
        if request.args.get(b'limitHitResponseCode'):
            curr_limit_hit_response_code = request.args.get(b'limitHitResponseCode')[0].decode('utf-8')

        try:
            # attempt to call it
            self.endpoint()
            self.total_ok += 1

            toReturn['status_code'] = 200
            toReturn['msg'] = "OK"
            toReturn['total_reqs'] = self.total_reqs
            toReturn['total_ok'] = self.total_ok
            toReturn['total_limit_hits'] = self.total_limit_hits

        except RateLimitException as e:
            self.total_limit_hits += 1
            request.setResponseCode(curr_limit_hit_response_code)
            toReturn['status_code'] = curr_limit_hit_response_code
            toReturn['msg'] = "%d: rate limit hit max_calls:%d period_seconds:%d" % (curr_limit_hit_response_code,self.max_calls,self.period_seconds)
            toReturn['retry_in_seconds'] = self.retry_in_seconds
            toReturn['retry_after_header_name'] = curr_retry_header_name
            toReturn['total_reqs'] = self.total_reqs
            toReturn['total_ok'] = self.total_ok
            toReturn['total_limit_hits'] = self.total_limit_hits

        finally:

            # capture all request args
            if len(request.args) > 0:
                toReturn['args'] = []
                for a in request.args:
                    toReturn['args'].append({a.decode('utf-8'):request.args.get(bytes(a))[0].decode('utf-8')})

            logging.debug(("GET %s : " + json.dumps(toReturn)) % request.path.decode("UTF-8"))

        request.setHeader(curr_retry_header_name, self.retry_in_seconds)
        return json.dumps(toReturn,indent=2).encode('UTF-8')



###########################
# Main program
##########################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--listen-port', dest='listen_port', help="Port to listen on, default 8081", type=int, default=8081)
    parser.add_argument('-m', '--max-calls', dest='max_calls', help="Max calls for the rate limiter over the specified --period-seconds, Default 1", type=int, default=1)
    parser.add_argument('-P', '--period-seconds', dest='period_seconds', help="Period in seconds that the --max-calls will apply for, Default 10", type=int, default=10)
    parser.add_argument('-r', '--retry-in-seconds', dest='retry_in_seconds', help="Value for the --retry-after-header-name argument which is returned when the rate limit has been reached, default 10", type=int, default=10)
    parser.add_argument('-c', '--limit-hit-response-code', dest='limit_hit_response_code', help="Default 429", type=int, default=429)
    parser.add_argument('-a', '--retry-after-header-name', dest='retry_after_header_name', help="Default Retry-After", default="Retry-After")

    # set vars
    args = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName("DEBUG"),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=None,filemode='w')
    logging.Formatter.converter = time.gmtime


    endpoint = MockRateLimitingEndpoint()
    endpoint.retry_after_header_name = args.retry_after_header_name
    endpoint.limit_hit_response_code = args.limit_hit_response_code
    endpoint.retry_in_seconds = args.retry_in_seconds
    endpoint.period_seconds = args.period_seconds
    endpoint.max_calls = args.max_calls
    endpoint.listen_port = args.listen_port

    endpoints.serverFromString(reactor, "tcp:" + str(args.listen_port)).listen(server.Site(endpoint))

    # start it up
    httpdthread = threading.Thread(target=reactor.run,args=(False,))
    httpdthread.daemon = True
    httpdthread.start()

    logging.debug("Starting with config: " + json.dumps(vars(args)))

    # wait for interrupt
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
