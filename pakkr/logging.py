import logging
import time

from contextlib import contextmanager


class IndentationAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
            return '{indent}{identifier} - {msg}'.format(indent=' '*(4*self.extra['indent']),
                                                         identifier=self.extra['identifier'],
                                                         msg=msg),\
                   kwargs


@contextmanager
def log_timing(logger, suppressd=False):
    if suppressd:
        yield
    else:
        logger.info("starting")
        start_time = time.time()
        yield
        end_time = time.time()
        logger.info("finished (took {elapsed:.3f}s)".format(elapsed=end_time - start_time))
