from struct import pack
from struct import unpack

class create_packet():

    def calc_checksum(self, packet):
        total = 0

        # Add up 16-bit words
        num_words = len(packet) // 2
        for chunk in unpack("!%sH" % num_words, packet[0:num_words*2]):
            total += chunk

        # Add any left over byte
        if len(packet) % 2:
            total += ord(packet[-1]) << 8

        # Fold 32-bits into 16-bits
        total = (total >> 16) + (total & 0xffff)
        total += total >> 16
        return (~total + 0x10000 & 0xffff)


    def unpack_header(self,format, packet):
        return unpack(format, packet)


    def pack_header(self, format, seq_num, field, message='', checksum='', ack=''):
        if checksum != '':
            return pack(format, seq_num, checksum, field, message)
        else:
            return pack(format, seq_num, ack, field)


    def get_checksum_seq_num(self, format, packet):
        checksum = self.calc_checksum(packet)
        recv_packet = self.unpack_header(format, packet)
        seq_num = recv_packet[0]
        field = recv_packet[2]
        msg = recv_packet[-1]
        original_msg = msg.decode('utf-8')
        return checksum, seq_num, field, original_msg