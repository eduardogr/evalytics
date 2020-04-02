import tornado.web

from .usecases import SetupUseCase, StartUseCase

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
                '/setup',
                '/start',
                '/status',
                '/finish',
            ]
        })

class SetupHandler(tornado.web.RequestHandler):
    path = r"/setup"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def post(self):
        try:
            setup_usecase = SetupUseCase(self.__repository, self.__comms_provider)
            setup = setup_usecase.execute()
            self.finish({
                'setup': setup.to_json()
            })
        except:
            self.finish({
                'success': False,
                'message': 'Something went wrong setting up evalytics',
            })

class StartHandler(tornado.web.RequestHandler):
    path = r"/start"

    __repository = None
    __comms_provider = None

    def initialize(self, repository, comms_provider):
        self.__repository = repository
        self.__comms_provider = comms_provider

    async def post(self):
        id = str(self.get_argument('id', -1, True))
        start_usecase = StartUseCase(self.__repository, self.__comms_provider)
        reviewers = start_usecase.execute()

        self.finish({
            'success': True,
            'eval': {
                'reviewers': [e.to_json() for e in reviewers]
            }
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
