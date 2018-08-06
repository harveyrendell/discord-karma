import logging
import sys

__version__ = '0.1.0'
logger = logging.getLogger(__name__)

formatter = logging.Formatter('[%(levelname)s]: %(message)s')
handler = logging.StreamHandler(sys.stdout)

logger.setLevel('DEBUG')
handler.setFormatter(formatter)
logger.addHandler(handler)
