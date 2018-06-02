import socket
from create_packet import create_packet
from threading import Thread
from threading import Lock


class ClientThreads(Thread):


    def __init__(self, ip, sock, byte_size):
        Thread.__init__(self)
        self.ip = ip
        self.socket = sock
        self.byte_size = byte_size
        self.checksum = 0
        self.field = 21845
        self.msg_pack_format = "!iHH" + str(byte_size) + "s"
        self.msg_ack_unpack_format = "!iHH"
        self.send_byte = {}
        self.packet = create_packet()
        self.lock = Lock()


    def run(self):
        message_in_byptes = []
        print("Starting threads for ", self.ip)
        with open('file1', 'rb') as f:
            while 1:
                chunk = f.read(self.byte_size)
                if chunk:
                    message_in_byptes.append(chunk)
                else:
                    break

        end_of_data = ""
        end_data = end_of_data.encode('utf-8')
        encoded_byte_size = str(self.byte_size).encode('utf-8')
        print("Sending byte size")
        #self.lock.acquire()
        self.send_byte_size(encoded_byte_size, self.ip)
        #self.lock.release()

        if self.send_byte[self.ip] == "ok":
            for msg in message_in_byptes:
         #       self.lock.acquire()
                seq_num = message_in_byptes.index(msg)
                header = self.packet.pack_header(format=self.msg_pack_format, seq_num=seq_num, checksum=self.checksum, field=self.field, message=msg)
                original_checksum = self.packet.calc_checksum(header)
                original_header = self.packet.pack_header(format=self.msg_pack_format, seq_num=seq_num, checksum=original_checksum, field=self.field, message=msg)
                print("Sending packet to server ",self.ip)
                self.send_to_servers(original_header, self.ip)
          #      self.lock.release()
           # self.lock.acquire()
            self.send_end_of_data(end_data, self.ip)
            #self.lock.release()
        print("Completed sending file to server ",self.ip)
        self.socket.close()


    def send_byte_size(self, message, server):
        try:
            self.socket.sendto(message, server)
            self.socket.settimeout(5)
            data, ser = self.socket.recvfrom(1024)
            recv_data = data.decode('utf-8')
            print(recv_data)
            if recv_data == "ok":
                self.send_byte[server] = recv_data

        except (socket.timeout,ConnectionResetError):
            print("Timeout on server: ", server)


    def send_to_servers(self, message, server, retry=0):
        if retry == 5:
            print("Reached max retires")
            exit(1)
        else:
            retry += 1
            self.socket.sendto(message, server)
            self.wait_for_reply(message, server, retry)


    def wait_for_reply(self, message_sent, receiving_server, retry_num):
        try:
            print("waiting for reply from ",receiving_server)
            self.socket.settimeout(5)
            data, ser = self.socket.recvfrom(1024)
            print(data, self.msg_ack_unpack_format)
            ack = self.packet.unpack_header(self.msg_ack_unpack_format, data)
            if ack[-1] == 43690:
                print("Ack received")

        except (socket.timeout,ConnectionResetError):
            print("Timeout on server: ", receiving_server," retrying again")
            self.send_to_servers(message_sent, receiving_server, retry_num)



    def send_end_of_data(self, end_message, server):
        try:
            self.socket.sendto(end_message, server)
            self.socket.settimeout(5)
            data, ser = self.socket.recvfrom(1024)
            print("end of msg ack ",data)
            recv_data = data.decode('utf-8')
            if recv_data == "ok":
                self.send_byte[end_message] = "sent"

        except (socket.timeout, ConnectionResetError):
            print("Timeout on server: ", server)




def main():

    server_1 = ('localhost', 7753)
    server_2 = ('localhost', 7754)
    server_3 = ('localhost', 7755)
    servers = [server_1, server_2, server_3]

    byte_size = int(input("Enter byte size"))

    thread_list = []
    for server in servers:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        thread_list.append(ClientThreads(server, s, byte_size))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


if __name__ == "__main__":
    main()