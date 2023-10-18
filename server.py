
import socket
import util
import os
import tqdm

HOST = "localhost"
PORT = 11451
FILE_DIR_LOC = "/opt/nvidia/" # Should end with a slash ('/' or '\')
BYTES_PER_TIME = 1024 * 64 # 64 KB per time by default, can be adjusted on your own. Don't set it to a big number because it depends on Python's runtime memory.

class ExitingException(Exception):
    def __init__(self):
        super.__init__("Caught bye command from the client. Exiting...")

def send_command_safely(s: socket.socket, command: str, *args):
    global running
    while True:
        util.send_command(s, command, *args)
        rcv_cmd_tuple = util.recv_command(s)
        if rcv_cmd_tuple[0] == "received":
            break
        elif rcv_cmd_tuple[0] == "bye":
            raise ExitingException()
        else:
            print("Failed to send data to the client. Retrying...")

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print("Server is running...")
        client_socket, addr = server_socket.accept()
        print("Client connected")
        
        try: 
            running = True
            while running:
                try:
                    for root, dirs, files in os.walk(FILE_DIR_LOC):
                        print("Entering directory:", root)
                        send_command_safely(client_socket, "mkdir", root[len(FILE_DIR_LOC):])
                        for (i, file) in enumerate(files):
                            dirfile = os.path.join(root, file)
                            dirfile_size = os.stat(dirfile).st_size
                            print("Begin to transfer:", dirfile, end=' ')
                            print("(", i, "/", len(files), ")", sep='')
                            print("Size (B):", dirfile_size)
                            send_command_safely(client_socket, "file_transfer_begin", dirfile[len(FILE_DIR_LOC):], dirfile_size)
                            with open(dirfile, "rb") as f:
                                with tqdm.tqdm(total=dirfile_size) as pbar:
                                        while True:
                                            fdata = f.read(BYTES_PER_TIME)
                                            if len(fdata) == 0:
                                                break
                                            send_command_safely(client_socket, "file_data", fdata)
                                            pbar.update(BYTES_PER_TIME)
                            send_command_safely(client_socket, "file_transfer_end")
                except ExitingException as ex:
                    print(ex)
                    running = False
        finally:
            client_socket.close()
    finally:
        server_socket.close()

def main():
    run_server()

if __name__ == "__main__":
    main()
