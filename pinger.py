# -*- coding: utf-8 -*-
"""
pinger
~~~~~~

Fetch a URL endpoint and check the response for (1) a 20X status code and (2) a
known, expected value. Log the success or failure to the logging API.

:copyright: (c) 2015 PMG <https://www.pmg.co>
:license: Apache-2.0
"""

import argparse
import os
import sys
import time
import urllib2 as urllib


class Result(object):
    """
    The result of of a check.
    """

    #: The status code
    code = None

    #: The response body given
    body = None

    #: Whether or not the response was considered succesful
    successful = None

    def __init__(self, code, body, successful):
        self.code = code
        self.body = body
        self.successful = successful

    def __str__(self):
        return '%s <%s> %s' % ('SUCCESS' if self.successful else 'ERROR', self.code, self.body)


class Checker(object):
    """
    The main object that checks a url and compares it against the expected
    response
    """

    #: The url to check
    url = None

    #: The expected response
    expected = None

    #: The url opener object
    opener = None

    def __init__(self, url, expected=None, opener=None):
        self.url = url
        self.expected = expected if expected is not None else 'OK'
        self.opener = opener or urllib.build_opener(urllib.HTTPRedirectHandler())

    def __call__(self):
        try:
            resp = self.opener.open(self.url)
        except urllib.HTTPError as e:
            resp = e

        body = resp.read()

        return Result(resp.code, body, str(body) == self.expected)


def main():
    p = argparse.ArgumentParser(description='Check a health URL')
    p.add_argument('-i', '--interval', help='How long to wait between checks', type=int, default=10)
    p.add_argument('-e', '--expected', help='The expected response body', type=str, default='OK')
    p.add_argument('url', help='The URL to check', type=str)

    args = p.parse_args()

    c = Checker(args.url, args.expected or None)
    while True:
        try:
            resp = c()
            fh = sys.stdout if resp.successful else sys.stderr
            fh.write(str(resp) + os.linesep)
        except Exception as e:
            sys.stderr.write(str(e) + os.linesep)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
