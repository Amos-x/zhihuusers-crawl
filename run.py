import os
from multiprocessing import Process
try:
    from zhihuusers.settings import CORE_NUMBER
except:
    CORE_NUMBER=None

class scheduler():
    def __init__(self):
        self.core_number = CORE_NUMBER

    @staticmethod
    def crwal():
        os.system('scrapy crawl zhihu')

    def run(self):
        names = locals()
        if self.core_number:
            for x in range(self.core_number):
                names['process%x' % x] = Process(target=scheduler.crwal)
                names['process%x' % x].start()

if __name__ == '__main__':
    s = scheduler()
    s.run()
