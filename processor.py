import asynchat
import os

LPD_POSITIVE_ACKNOWLEDGEMENT = b'\x00'
LPD_NEGATIVE_DEFAULT_ACNOWLEDGEMENT = b'\x00'
LPD_COMMAND_TERMINATION = b'\n'
LPD_FILE_TERMINATION = b'\x00'
LPD_LEVEL1_COMMAND_COUNT = 5
LPD_LEVEL2_COMMAND_COUNT = 3


class Processor(asynchat.async_chat):

    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock=sock)
        self.ibuffer = b""
        self.set_terminator(LPD_COMMAND_TERMINATION)
        self.lpd_command_level = 1
        self.sock=sock
        self.file_name = ""

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer+=data

    def found_terminator(self):
        command = self.ibuffer[0]
        if self.lpd_command_level == 1:
            if command == 0 or command > LPD_LEVEL1_COMMAND_COUNT: self.bad_command()
            elif command == 1: self.command01()
            elif command == 2: self.command02()
            elif command == 3: self.command03()
            elif command == 4: self.command04()
            elif command == 5: self.command05()
        elif self.lpd_command_level == 2:
            if command == 0 or command > LPD_LEVEL2_COMMAND_COUNT: self.bad_command()
            elif command == 1: self.command02_01()
            elif command == 2: self.command02_02()
            elif command == 3: self.command02_03()
        elif self.lpd_command_level == 3: self.receive_file(self.file_name)

    def bad_command(self):
        print("bad command: %s" % self.ibuffer)
        self.negative_ack(b"bad command")
        self.close()

    def command01(self):
        print('%d' % self.ibuffer[0])
        self.close()

    def command02(self):
        print("command: %d, queue: %s, level: %d" % (self.ibuffer[0], self.ibuffer[1:].decode("utf-8"), self.lpd_command_level))
        self.ibuffer = b""
        self.positive_ack()
        self.lpd_command_level = 2

    def command03(self): print("03")

    def command04(self): 
        print("Command: 04")
        print("Data: $s".format(self.ibuffer[1:].decode("utf-8")))
        self.ibuffer = b""
        self.positive_ack()

    def command05(self): print("05")

    def command02_01(self):
        self.ibuffer = b""
        self.close()

    def command02_02(self):
        print("got command: %d on level: %d" % (self.ibuffer[0], self.lpd_command_level))
        params = self.ibuffer[1:].split(b' ')
        self.lpd_command_level = 3
        if self.ibuffer[0] == 2:
            self.set_terminator(LPD_FILE_TERMINATION)
        elif self.ibuffer[0] == 3:
            if int(params[0]) > 1000000000:
                self.set_terminator(None)
            else:
                self.set_terminator(int(params[0]))
        self.file_name = params[1].decode("windows-1251")
        self.ibuffer = b""
        self.positive_ack()

    def command02_03(self):
        self.command02_02()

    def positive_ack(self):
        print("send positive_ack")
        self.push(LPD_POSITIVE_ACKNOWLEDGEMENT)

    def negative_ack(self, ack=LPD_NEGATIVE_DEFAULT_ACNOWLEDGEMENT):
        print("send negative_ack")
        self.push(ack)

    def receive_file(self, file_name):
        print("receiving file %d bytes" % len(self.ibuffer))
        file_name = os.path.join(os.curdir, file_name)
        with open(file_name, "wb") as f:
            f.write(self.ibuffer)
        self.ibuffer = b""
        self.set_terminator(LPD_COMMAND_TERMINATION)
        self.lpd_command_level = 2
        self.positive_ack()

    def handle_close(self):
        if self.lpd_command_level == 3: 
            self.receive_file(self.file_name)
            print("file saved because channel is closing")
        self.close()

    def log(level, command):
        print("level: %d, command: %d" % (level, command)) 
        
