
import socket

commands = {
    '''
    Notify the other side that the transfer has been received completely.
    '''
    "received" : 0,
    '''

    Notify the downloader to ensure the target subdirectory is existing.
    Followings:
        0: str(utf-8 bytes) - The subdirectory.
    '''
    "mkdir" : 1,

    '''
    Notify the downloader that a file will begin to transfer.
    Followings:
        0: str(utf-8) - The file's location.
        1: int(str(utf-8 bytes)) - The size (in bytes) of the data contained by this file to transfer.
        2: int(str(utf-8 bytes)) - The size (in bytes) of the data sent per time.
    '''
    "file_transfer_begin" : 2,
    
    '''
    Transfer the data of the file mentioned just now.
    Followings:
        0: bytes - The size of the data contained by this file to transfer.
    '''
    "file_data" : 1,

    '''
    Notify the downloader that a file will end its transfer.
    '''
    "file_transfer_end" : 0,

    '''
    Notify the downloader that all tasks are done and the connection will come to end.
    '''
    "bye" : 0
}

def send_data(s: socket.socket, data: bytes):
    lendata = len(data).to_bytes(8, "big")
    s.send(lendata)
    s.send(data)

def send_str_utf8(s: socket.socket, st: str):
    st_data = st.encode("utf-8")
    send_data(s, st_data)

def send_int_str_utf8(s: socket.socket, i: int):
    send_str_utf8(s, str(i))

def __recv_data(s: socket.socket, length: int = 0) -> bytes:
    result = b''
    remaining = length
    while remaining > 0:
        data = s.recv(length)
        result += data
        remaining -= len(data)
    return result

def recv_data(s: socket.socket, len: int = 0) -> bytes:
    lendata = s.recv(8)
    if len > 0:
        return __recv_data(s, len)
    else:
        my_len = int.from_bytes(lendata, "big")
        return __recv_data(s, my_len)

def recv_str_utf8(s: socket.socket) -> str:
    return recv_data(s).decode("utf-8")

def recv_int_str_utf8(s: socket.socket) -> int:
    return int(recv_str_utf8(s))

def send_command(s: socket.socket, command: str, *args):
    send_str_utf8(s, command)
    match command:
        case "mkdir":
            send_str_utf8(s, args[0])
        case "file_transfer_begin":
            send_str_utf8(s, args[0])
            send_int_str_utf8(s, args[1])
            send_int_str_utf8(s, args[2])
        case "file_data":
            send_data(s, args[0])
        case _:
            pass

def recv_command(s: socket.socket, file_data_recv_bytes_per_time: int = 0) -> tuple:
    command = recv_str_utf8(s)
    args = []
    match command:
        case "mkdir":
            args.append(recv_str_utf8(s))
        case "file_transfer_begin":
            args.append(recv_str_utf8(s))
            args.append(recv_int_str_utf8(s))
            args.append(recv_int_str_utf8(s))
        case "file_data":
            args.append(recv_data(s, file_data_recv_bytes_per_time))
        case _:
            pass
    return (command, *args)
