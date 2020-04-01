
import tornado.web


class WelcomeHandler(tornado.web.RequestHandler):
    path = r"/"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def get(self):
        self.finish({
            'message': 'Welcome this is the evalytics server!',
            'entrypoints': [
                '/',
                '/start',
                '/status',
                '/finish',
            ]
        })

class StartHandler(tornado.web.RequestHandler):
    path = r"/start"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def get(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'message': 'With this entrypoint you are starting an evaluation process!',
        })

    async def post(self):
        try:
            id = str(self.get_argument('id', -1, True))

            self.finish({
                'success': True,
                'message': 'You have started an evaluation process',
                'id': id,
            })
        except:
            self.finish({
                'success': False,
                'message': 'Something went wrong starting the evaluation process',
                'id': id,
            })

class StatusHandler(tornado.web.RequestHandler):
    path = r"/status"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def get(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'message': 'With this entrypoint you querying the process of the evaluation process!',
        })

class FinishHandler(tornado.web.RequestHandler):
    path = r"/finish"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def post(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'message': 'With this entrypoint you are finishing the process and processing results!',
        })
