import socket
import struct
import random

ID_UNCONNECTED_PING = 0x01
ID_UNCONNECTED_PONG = 0x1c
MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

def unconnected_ping(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    # Encode UnconnectedPing
    send_packet_buffer = bytearray()
    send_packet_buffer.append(ID_UNCONNECTED_PING)  # UnconnectedPing packet id
    send_packet_buffer.extend(struct.pack('Q', random.randint(0, 100000)))  # Ping id
    send_packet_buffer.extend(MAGIC)  # Magic
    send_packet_buffer.extend(struct.pack('Q', 730730))  # Client id

    sock.sendto(send_packet_buffer, (host, port))

    try:
        receive_packet_buffer, _ = sock.recvfrom(1024)
    except socket.timeout:
        return False

    # Decode UnconnectedPong
    pid = receive_packet_buffer[0]
    if pid != ID_UNCONNECTED_PONG:
        return False

    send_ping_time, server_id = struct.unpack_from('>QQ', receive_packet_buffer, 1)
    magic = receive_packet_buffer[17:33]
    if magic != MAGIC:
        return False

    length = struct.unpack_from('>H', receive_packet_buffer, 33)[0]
    if length == 0:
        return False

    server_data = receive_packet_buffer[35:35 + length].decode('utf-8')
    info = server_data.split(';')
    if len(info) == 0 or info[0] != 'MCPE':
        return False

    return info

result = unconnected_ping('sg.hivebedrock.network', 19132)
if result is None:
    print('Failed to get information')
else:
    print(result)
    # PocketMine-MP
    # i.g. 'MCPE', '§eBowyers§l§6MC§r', '671', '1.20.80', '3', '40', '2513297365544966483', 'PocketMine-MP', 'Adventure', ''
    # mcpe, motd, protocol, version, logginged_players, max_players, unknown, software, default_gamemode, unknown2 = result

    # Internal Server
    # i.g. 'MCPE', '§b§lASIA §7§l» BEDWARS! \ue107', '121', '1.0', '6471', '100001', '6789065943391985534', 'Hive Games', 'Survival'
    # mcpe, motd, unknown, unknown2, logginged_players, max_players, unknown3, software, default_gamemode = result
