from projects.abstract import Bot


class ShBot(Bot):
    def __init__(self, queue):
        super(ShBot, self).__init__(queue)

    def proceed(self, msg):
        print 'shevit: i got smth:', msg
