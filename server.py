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



define("port", default=8080, help="Run tornado server on the given port", type=int)
define("config", default="config.yaml", help="Config file holding configuration for the server", type=str)

class App():

    def get_paths_and_handlers(self):
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

    def create(self) -> tornado.web.Application:
        tornado.options.parse_command_line()
        paths_and_handlers = self.get_paths_and_handlers()
        app = tornado.web.Application(paths_and_handlers)
        return app


class Server(App):

    def run(self):
        app = super().create()
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        #logger.info(f'Listening to port {options.port} (use CTRL + C to quit)')
        tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    Server().run()
