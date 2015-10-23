#!/usr/bin/env python3
import asyncore, socket, processor

LPD_PORT = 515
LPD_CONNECTION_SCOPE = ''

class LPD(asyncore.dispatcher):

    def __init__(self, host=LPD_CONNECTION_SCOPE, port=LPD_PORT):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('*****************\nIncoming connection from %s' % repr(addr))
            proc = processor.Processor(sock)

server = LPD()
asyncore.loop()
