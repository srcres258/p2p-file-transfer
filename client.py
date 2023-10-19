
import socket
import util
import os
import tqdm

HOST = "localhost"
PORT = 11451
FILE_DIR_LOC = "/home/srcres/Coding/Projects/p2p-file-transfer/receive"

def recv_command_safely(s: socket.socket, file_data_recv_bytes_per_time: int) -> tuple:
    cmd_tuple = util.recv_command(s, file_data_recv_bytes_per_time)
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
        recv_bytes_per_time = 0
        while running:
            cmd_tuple = recv_command_safely(client_socket, recv_bytes_per_time)
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
                    recv_bytes_per_time = cmd_tuple[3]
                    receiving = True
                case "file_data":
                    recv_f.write(cmd_tuple[1])
                    pbar.update(len(cmd_tuple[1]))
                case "file_transfer_end":
                    print("Finished receiving a file from the server:", recv_f_path)
                    print("Total size (B):", recv_f_size)
                    print("Received size (B):", pbar.n)
                    recv_bytes_per_time = 0
                    receiving = False
                case "bye":
                    print("Finished the entire file transfer. Quitting...")
                    running = False
                case "received":
                    pass
                case _:
                    if len(cmd_tuple[0]) == 0:
                        print("Warning: Received null command from the server. Is the network broken? Retrying.")
                    else:
                        raise Exception("Unknown command from the server: {}. This should not happen.".format(cmd_tuple[0]))
    finally:
        client_socket.close()

def main():
    run_client()

if __name__ == "__main__":
    main()
