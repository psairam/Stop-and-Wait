import random
import socket
from create_packet import create_packet


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_1 = ('localhost', 7753)
s.bind(server_1)
msg="ok"
reply=msg.encode('utf-8')
recv_seq_num = []
ack_format = "!iHH"
packet = create_packet()


def get_byte_size(reply):
    byte_size, client = s.recvfrom(1024)
    real_byte_size = byte_size.decode('utf-8')
    s.sendto(reply, client)
    format_for_packet = "!iHH" + real_byte_size + 's'
    return format_for_packet

unpack_format = get_byte_size(reply)

with open('server_1.txt', 'w') as f:
    while True:
        data, client = s.recvfrom(1024)
        if not data:
            s.sendto(reply, client)
            f.close()
            break
        else:
            checksum, seq_num, field, original_msg = packet.get_checksum_seq_num(unpack_format, data)
            if checksum == 0:
                print("checksum is correct")

                if seq_num in recv_seq_num:
                    print("seq num is already present")
                    ack = packet.pack_header(ack_format, seq_num=seq_num, ack=0, field=43690)
                    s.sendto(ack, client)
                else:
                    probability = round(random.random(), 2)
                    recv_seq_num.append(seq_num)
                    f.write(original_msg)
                    if probability!=0.3 :
                        ack = packet.pack_header(ack_format, seq_num=seq_num, ack=0, field=43690)
                        print("sending ack to ",client)
                        s.sendto(ack,client)
            else:
                print("Checksum is wrong discarding the packet")
                continue


s.close()
