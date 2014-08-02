# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import time
import tornado.httpserver
import tornado.options
import tornado.web
import redis

from collections import defaultdict
from functools import wraps
from tornado.ioloop import IOLoop
from tornado.options import define, options

from trie import Trie

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/([a-zA-Z]+)", WordHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="31X9&hFV{ht|x%-NRSp2n?:cdH|M6uk>V2>9At-v|q-"
            "(+w$2+VZnS4}HM+VIE4?1",
            compress_response=True,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Global Connection to Words
        t0 = time.time()
        self.words_collection = Trie("OWL2.txt")
        t1 = time.time()
        print "Trie Loaded: {}ms".format(round((t1-t0) * 1000, 2))

        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.r.flushdb()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def redis(self):
        return self.application.r

    @property
    def words_collection(self):
        return self.application.words_collection

    def get(self, *args, **kwargs):
        self.content_type = 'application/json'
        self.write(self.get_resource(*args, **kwargs))
        self.finish()

    def get_resource(self, resource=None):
        raise NotImplementedError()

    def post_resource(self, resource=None):
        raise NotImplementedError()

    def patch_resource(self, resource=None):
        raise NotImplementedError()

    def delete_resource(self, resource=None):
        raise NotImplementedError()


def cached(timeout=60 * 60, future=True):
    '''
        Simple Cache decorator for a BaseHandler. Requires cache value to be
            setup externally to function.

        :param timeout: Number of seconds for cache to live. Default 1hour.
        :param key: String to format key.  Note: Format passed key with flask
            request.full_path
    '''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            self = args[0]
            uri = self.request.uri

            rv = self.redis.get(uri)

            while rv == "FUTURE":
                # Relax and try again
                time.sleep(0.01)
                rv = self.redis.get(uri)

            if rv is not None:
                return json.loads(rv)

            # Notify we're building a responce (expire in 3 seconds)
            self.redis.setex(uri, 3, "FUTURE")

            rv = f(*args, **kwargs)

            self.redis.setex(uri, 3600, json.dumps(rv))
            return rv

        return decorated_function
    return decorator


class MainHandler(BaseHandler):
    def get(self):
        # TODO: Front-end goes here.
        doc_str = ("Find what words you can spell<br>"
                   "By entering a word in the url!")
        self.write(doc_str)


class WordHandler(BaseHandler):
    @cached()
    def get_resource(self, word):
        word = word.upper()
        distance = int(self.get_argument('distance', '0'))

        words = defaultdict(list)
        for word, val in self.words_collection.get_words(word, distance):
            words[val].append(word)

        return {'word': word,
                'words': words}


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
