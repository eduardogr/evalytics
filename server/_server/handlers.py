#!/usr/bin/python3

import tornado.web


class WelcomeHandler(tornado.web.RequestHandler):
    path = r"/"

    async def get(self):
        self.finish({
            'message': 'Welcome this is the evalytics server!',
            'entrypoints': [
                '/',
            ]
        })
