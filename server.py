import tornado.ioloop
from tornado.web import Application

from tornado.options import define, options

from evalytics.handlers import \
    EmployeesHandler, \
    SurveysHandler, \
    ReviewersHandler, \
    CommunicationHandler, \
    ResponseStatusHandler, EvalReportsHandler, \
    PeersAssignmentHandler

define(
    "port", default=8080,
    help="Run tornado server on the given port", type=int)

class GetPathAndHandler:

    def get(self):
        handlers = [
            PeersAssignmentHandler,
            EmployeesHandler,
            SurveysHandler,
            ReviewersHandler,
            CommunicationHandler,
            ResponseStatusHandler,
            EvalReportsHandler
        ]

        return [(h.path, h) for h in handlers]

def main():
    tornado.options.parse_command_line()
    path_and_handler = GetPathAndHandler().get()
    app = Application(path_and_handler)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
