import dill
import logging
import sys
import threading


logger = logging.getLogger('mainmod')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)

fmt = logging.Formatter('%(levelname)s::%(asctime)s::%(name)s - %(message)s')
sh.setFormatter(fmt)

logger.addHandler(sh)


logger.info('Test message')


class MyLogger:
    def __init__(self, logger):
        self.logger = logger
        self.handlers = self.logger.handlers
        self.level = self.logger.level

    def __getstate__(self):
        d = self.__dict__.copy()
        if 'logger' in d:
            d['logger'] = d['logger'].name

            # Remove RLock to allow proper serialization
            for handler in d['handlers']:
                handler.lock = None

        return d

    def __setstate__(self, d):
        if 'logger' in d:
            d['logger'] = logging.getLogger(d['logger'])

            # Restore RLock
            for handler in d['handlers']:
                handler.lock = threading.RLock()

            d['logger'].handlers = d['handlers']
            d['logger'].level = d['level']
            d['logger'].propagate = False
        self.__dict__.update(d)


to_sz = MyLogger(logger)

with open('pickledlogger.bin', 'wb') as f:
    sz = dill.dump(to_sz, f)
