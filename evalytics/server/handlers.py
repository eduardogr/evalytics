import tornado.web

from .usecases import SetupUseCase, StartUseCase

class WelcomeHandler(tornado.web.RequestHandler):
    path = r"/"

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

    async def post(self):
        try:
            setup_usecase = SetupUseCase()
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

    async def post(self):
        id = str(self.get_argument('id', -1, True))
        start_usecase = StartUseCase()
        employees = start_usecase.execute()

        self.finish({
            'success': True,
            'eval': {
                'id': id
            },
            'employees': [e.to_json() for uid, e in employees.items()]
        })
  
class StatusHandler(tornado.web.RequestHandler):
    path = r"/status"

    async def get(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'eval': {},
        })

class FinishHandler(tornado.web.RequestHandler):
    path = r"/finish"

    async def post(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'eval': {},
        })
