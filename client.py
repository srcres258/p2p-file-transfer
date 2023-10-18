
import socket
import util
import os
import tqdm

HOST = "localhost"
PORT = 11451
FILE_DIR_LOC = "/home/srcres/Coding/Projects/p2p-file-transfer/receive"

def recv_command_safely(s: socket.socket) -> tuple:
    cmd_tuple = util.recv_command(s)
    util.send_command(s, "received")
    return cmd_tuple

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to the server.")

        running = True
        receiving = False
        pbar = None
        recv_f_path = ""
        recv_f_size = 0
        recv_f = None
        while running:
            cmd_tuple = recv_command_safely(client_socket)
            # print("Received command:", cmd_tuple[0])
            match cmd_tuple[0]:
                case "mkdir":
                    target_dir = os.path.join(FILE_DIR_LOC, cmd_tuple[1])
                    if os.path.exists(target_dir):
                        print("Directory already exists:", target_dir)
                    else:
                        print("Making directory:", target_dir)
                        os.makedirs(target_dir)
                case "file_transfer_begin":
                    target_path = os.path.join(FILE_DIR_LOC, cmd_tuple[1])
                    target_size = cmd_tuple[2]
                    print("Begin to receive a file from the server:", target_path)
                    print("Size (B):", target_size)
                    recv_f_path = target_path
                    recv_f_size = target_size
                    recv_f = open(target_path, "wb")
                    pbar = tqdm.tqdm(total=target_size)
                    receiving = True
                case "file_data":
                    recv_f.write(cmd_tuple[1])
                    pbar.update(len(cmd_tuple[1]))
                case "file_transfer_end":
                    print("Finished receiving a file from the server:", recv_f_path)
                    print("Total size (B):", recv_f_size)
                    print("Received size (B):", pbar.n)
                    receiving = False
                case "bye":
                    print("Finished the entire file transfer. Quitting...")
                    running = False
                case "received":
                    pass
                case _:
                    raise Exception("Unknown command from the server: {}. This should not happen.".format(cmd_tuple[0]))
    finally:
        client_socket.close()

def main():
    run_client()

if __name__ == "__main__":
    main()
