import enum
from abc import abstractclassmethod
from datetime import datetime, date
from serial import Serial


SXT = 0x02
EXT = 0x03
DELIM = 0x1C


class Value:

    def __init__(self, source):
        self.source = source


    def bool(self, bit):
        return int(chr(self.source)) & 1 << bit

    def string(self):
        return "".join(chr(d) for d in self.source)

    def int(self):
        return int(chr(self.source[0]))

    def date(self):
        return datetime.strptime(self.string(), "%d%m%y")

    def time(self):
        return datetime.strptime(self.string(), "%H%M%S")


class Output:

    def __init__(self, code: int):
        self.code = code
        self.params = []

    def add_param(self, value) -> 'Output':
        if type(value) == str:
            self.params.append(x for x in value.encode("CP866"))
        elif type(value) == bool:
            if value:
                self.params.append(0x31)
            else:
                self.params.append(0x30)
        elif type(value) == datetime:
            self.params.append(ord(x) for x in value.strftime("%d%m%y"))
            self.params.append(ord(x) for x in value.strftime("%H%M%S"))
        else:
            self.params.append(value)
        return self

    def get_bytes(self, password, id):
        result = [SXT]
        result.extend(ord(x) for x in password)
        result.append(id)
        result.extend(ord(x) for x in "%02X" % self.code)
        for param in self.params:
            if type(param) == int:
                result.append(param)
            elif type(param) == str:
                result.extend(ord(x) for x in password)
            else:
                result.extend(param)
            result.append(DELIM)
        result.append(EXT)
        crc = 0
        for x in result[1:]:
            crc ^= x
        for x in (ord(x) for x in str("%02x" % crc)):
            result.append(x)
        return result


class Input:

    def __init__(self, port: Serial):
        self.__port: Serial = port
        self.__buffer = []

        if ord(self.__read(1)) != SXT:
            raise Exception("Wrong start byte")
        self.id = ord(self.__read(1))

        self.code = int("0x" + "".join(chr(x) for x in self.__read(2)), 16)
        self.error = int("0x" + "".join(chr(x) for x in self.__read(2)), 16)
        self.data = []
        current = ord(self.__read(1))
        element = []
        while current != EXT:
            if current == DELIM:
                self.data.append(element)
                element = []
            else:
                element.append(current)

            current = ord(self.__read(1))
        crc = 0
        for x in self.__buffer[1:]:
            crc ^= x

        packet_crc = int("0x" + "".join(chr(x) for x in self.__read(2)), 16)
        if crc != packet_crc:
            raise Exception("Wrong CRC!")

    def get_error(self):
        if self.error == 0:
            return None
        if self.error == 3:
            return "Неверный формат команды"

    def value(self, index):
        return Value(self.data[index])

    def to_bool(self, index):
        return self.to_string(index) == '1'

    def to_string(self, index):
        return bytearray(self.data[index]).decode("cp866")

    def to_int(self, index):
        return int(self.to_string(index))

    def to_date(self, index):
        return datetime.strptime(self.to_string(index), "%d%m%y")

    def to_time(self, index):
        return datetime.strptime(self.to_string(index), "%H%M%S")

    def to_datetime(self, date_index, time_index):
        if self.to_string(date_index) == "000000":
            return datetime.min
        return datetime.strptime(self.to_string(date_index)+self.to_string(time_index), "%d%m%y%H%M%S")

    def __read(self, size: int):
        result = self.__port.read(size)
        self.__buffer.extend(result)
        return result

    def __str__(self):
        s = "{ id:%i code:%02x error:%i} raw [%s]\n" % (self.id, self.code, self.error, " ".join("%02x" % x for x in self.__buffer))
        for d in self.data:
            s = s +  " ".join("%02x" % x for x in d) + "\n"
        return s

class Command:

    def __init__(self, code: int, params: [], answer=None):
        self.output = Output(code)
        for param in params:
            self.output.add_param(param)

    def value(self, packet):
        return None

class AnswerFNVersion(Command):

    def __init__(self):
        Command.__init__(self, 0x78, [14])

    def value(self, packet):
        pass

