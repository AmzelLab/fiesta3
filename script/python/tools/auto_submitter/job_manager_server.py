"""Job manager server.

Here we implements a job manager server, which can automatically manage
remote jobs, update remote jobs and cancel remote jobs if necessary.
"""

import logging
import sys
from time import strftime
from xmlrpc.server import SimpleXMLRPCServer

from config import HOSTNAME
from config import PORT
from config import RequestHandler
from manager import JobManager

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

DESCRIPTION = "Batch Job Manager (Server)"

LOGGER = logging.getLogger('job_manager')
LOGGER.setLevel(logging.DEBUG)

LOG_FILE = 'server_%s.log' % strftime('%X_%d_%b_%Y')
FILE_HANDLER = logging.FileHandler(LOG_FILE)
FILE_HANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter(
    "[%(levelname)s %(asctime)s %(name)s] %(message)s")
FILE_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)


def main():
    """Server's Main function. Setup server's components.
    """
    LOGGER.info("setup job manager server [%s:%s]", HOSTNAME, PORT)
    server = SimpleXMLRPCServer((HOSTNAME, PORT),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()
    LOGGER.info("server setupped")

    LOGGER.info("create job manager")
    manager = JobManager()
    manager.take_office()
    server.register_instance(manager)
    LOGGER.info("registered manager to server")
    LOGGER.info("server starts serving")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("server closed by keyboard [Ctrl-C]")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
