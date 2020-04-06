import tornado.web

from .usecases import SetupUseCase, GetReviewersUseCase

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

class ReviewersHandler(tornado.web.RequestHandler):
    path = r"/reviewers"

    async def get(self):
        get_reviewers = GetReviewersUseCase()
        reviewers = get_reviewers.execute()

        self.finish({
            'success': True,
            'reviewers': [r.to_json() for uid, r in reviewers.items()]
        })

class SendMailHandler(tornado.web.RequestHandler):
    path = r"/sendmail"

    async def post(self):
        revieweers = self.get_argument('revieweers', [], True)

        self.finish({
            'id': id,
            'revieweers': revieweers,
        })

class EvalsHandler(tornado.web.RequestHandler):
    path = r"/evals"

    async def get(self):
        id = str(self.get_argument('id', -1, True))

        self.finish({
            'id': id,
            'eval': {},
        })
