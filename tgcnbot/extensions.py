import os

import logging

from tgcnbot.lib.database import SQLAlchemy


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

db = SQLAlchemy('sqlite:////{}/data/tgcnbot.db'.format(os.getcwd()))
