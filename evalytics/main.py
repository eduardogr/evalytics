#!/usr/bin/python3

import tornado.ioloop
import tornado.web

from tornado.options import define, options

from server.di import Module
from server.handlers import \
    WelcomeHandler, StartHandler, StatusHandler, FinishHandler

define(
    "port", default=8080,
    help="Run tornado server on the given port", type=int)
define(
    "environment", default='dev',
    help="Environment to switch between di.Module instances", type=str)

class EvalyticsServer(tornado.web.Application):
    def __init__(self, environment):
        handlers = [
            WelcomeHandler,
            StartHandler,
            StatusHandler,
            FinishHandler,
        ]

        # Switch between 'dev' and 'production' DI containers
        instances = Module.containers[environment]

        paths_by_handler = [(h.path, h, instances) for h in handlers]
        tornado.web.Application.__init__(self, paths_by_handler)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(EvalyticsServer(options.environment))
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
