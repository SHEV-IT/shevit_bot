# coding: utf-8
from projects.abstract import Bot
from msgs import MsgWorker


class ShBot(Bot):
    def __init__(self, queue):
        super(ShBot, self).__init__(queue)
        self.msgs = MsgWorker()

    def proceed(self, msg):
        msg_type = msg['event']['type']
        if msg_type == 'message_new':
            self.msgs.proceed(msg['event']['object'])
        print 'shevit: i got smth:', msg
