# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from collections import defaultdict
from tornado.options import define, options

from trie import Trie

define("port", default=8888, help="run on the given port", type=int)

words_collection = Trie("OWL2.txt")


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


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # TODO: Front-end goes here.
        doc_str = ("Find what words you can spell<br>"
                   "By entering a word in the url!")
        print type(doc_str)
        self.write(doc_str)


class WordHandler(tornado.web.RequestHandler):
    # TODO: A cache engine should handle this.
    # Save last 10 responses
    requests = list()
    responces = list()

    def get(self, word):
        # Bad Caching Example
        # Note this could be a future (aka all other threads)
        # will hold for the first to finish?
        uri = self.request.uri
        if uri in self.requests:
            self.write(self.responces[self.requests.index(uri)])
            return

        # Actual Code
        word = word.upper()
        distance = int(self.get_argument('distance', '0'))

        words = defaultdict(list)
        for x in words_collection.get_words(word, distance):
            words[len(x)].append(x)

        resp = {'word': word,
                'words': words}

        # Bad Caching Example
        self.requests.append(uri)
        self.responces.append(resp)
        if len(self.requests) > 10:
            self.requests.pop(0)
            self.responces.pop(0)

        self.write(resp)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
