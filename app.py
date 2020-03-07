from tornado import httpclient
import tornado.ioloop
import tornado.web
from jetbot import Robot
import logging
import time
import os

logger = logging.getLogger()
handler1 = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
logger.setLevel(logging.DEBUG)
handler1.setFormatter(formatter)


robot = Robot()

SPEED_OPTION = {
    'forward': (0.4, 0.4),
    'backward': (-0.3, -0.3),
    'left': (-0.2, 0.2),
    'right': (0.2, -0.2)
}

def run(act):
    ls, rs = SPEED_OPTION[act]
    robot.set_motors(ls, rs)
    time.sleep(0.01)
    robot.stop()


class MotionHandler(tornado.web.RequestHandler):

    def post(self):
        action = self.get_body_argument('move')
        logger.debug('[DIRECTION]: %s' % action)
        run(action)
        self.finish()

def make_app():
    return tornado.web.Application([
        (r'/move',  MotionHandler),
    ],
    debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(5500)
    tornado.ioloop.IOLoop.current().start()


