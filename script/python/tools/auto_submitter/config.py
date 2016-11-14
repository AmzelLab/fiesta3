"""Some constant defined for this package
"""

from xmlrpc.server import SimpleXMLRPCRequestHandler

HOSTNAME = 'localhost'
PORT = 8000


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
