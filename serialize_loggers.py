import dill
import logging
import sys
import threading


logger = logging.getLogger('mainmod')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)

fmt = logging.Formatter('%(levelname)s::%(asctime)s::%(name)s::%(message)s')
sh.setFormatter(fmt)

logger.addHandler(sh)


logger.info('Test message')


class MyLogger:
    def __init__(self, logger):
        self.state = logger.__dict__

    def __getstate__(self):
        d = self.__dict__.copy()

        # Remove RLock to allow proper serialization
        for handler in d['state']['handlers']:
            handler.lock = None

        # Remove unneeded objects
        for k in ['parent', '_cache', 'manager']:
            del d['state'][k]

        return d

    def __setstate__(self, d):
        # Get new logger with previously saved name
        d['logger'] = logging.getLogger(d['state']['name'])

        # Restore RLock to ensure thread safety
        for handler in d['state']['handlers']:
            handler.lock = threading.RLock()

        # Update logger with previously saved state
        # and disable message propagation to parent
        d['logger'].__dict__.update(d['state'])
        d['logger'].propagate = False

        # Cleanup
        del d['state']

        self.__dict__.update(d)


to_sz = MyLogger(logger)

with open('pickledlogger.bin', 'wb') as f:
    sz = dill.dump(to_sz, f)
