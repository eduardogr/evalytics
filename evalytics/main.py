#!/usr/bin/python3

import tornado.ioloop
import tornado.web

from tornado.options import define, options

from evalytics.server.handlers import \
    SetupHandler, \
    ReviewersHandler, SendMailHandler, \
    EvalsHandler

define(
    "port", default=8080,
    help="Run tornado server on the given port", type=int)

class EvalyticsServer(tornado.web.Application):
    def __init__(self):
        handlers = [
            SetupHandler,
            ReviewersHandler,
            SendMailHandler,
            EvalsHandler,
        ]

        paths_by_handler = [(h.path, h) for h in handlers]
        tornado.web.Application.__init__(self, paths_by_handler)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(EvalyticsServer())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
