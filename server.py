import tornado
from tornado.options import define, options


from evalytics.handlers import \
    HealthHandler, \
    EmployeesHandler, \
    SurveysHandler, \
    ReviewersHandler, \
    CommunicationHandler, \
    ResponseStatusHandler, EvalReportsHandler, \
    PeersAssignmentHandler

class GetPathAndHandler:

    def get(self):
        handlers = [
            HealthHandler,
            PeersAssignmentHandler,
            EmployeesHandler,
            SurveysHandler,
            ReviewersHandler,
            CommunicationHandler,
            ResponseStatusHandler,
            EvalReportsHandler
        ]

        return [(h.path, h) for h in handlers]


define(
    "port", default=8080,
    help="Run tornado server on the given port", type=int)


def create_app() -> tornado.web.Application:
    tornado.options.parse_command_line()
    path_and_handler = GetPathAndHandler().get()
    app = tornado.web.Application(path_and_handler)
    return app


def run_server():
    app = create_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    #logger.info(f'Listening to port {options.port} (use CTRL + C to quit)')
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run_server()
