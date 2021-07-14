import os
import socket
import threading
import time


IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "serverFolder"

### to handle the clients
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))

    while True:
        data =  conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        send_data = "OK@"

        # HELP command - lists all command options
        if cmd == "HELP": 
            send_data += "LOGOUT - Logout from the server.\n"
            send_data += "UPLOAD <filename> - Upload a new file to the server.\n"
            send_data += "DOWNLOAD <filename> - Download a file from the server.\n"
            send_data += "DELETE <filename> - Delete a file from the server.\n"
            send_data += "DIR - Return the contents of the shared server folder.\n"

            conn.send(send_data.encode(FORMAT))

        # LOGOUT command - disconnects client from server
        elif cmd == "LOGOUT":
            break 

        # UPLOAD command - uploads a new file from the client to the server folder
        elif cmd == "UPLOAD":
            files = os.listdir(SERVER_PATH) # Get all files in the server folder
            fileName = data[1] # Get the file name being uploaded
            fileSize = int(data[2]) # Get the size of the file being uploaded


            # Respond to client when the file did not exist to upload
            if(fileName == "NOFILE" and fileSize == 0):
                send_data += "File entered not found. Enter a valid file from the client folder."

            # Receive file from client
            else:
                if fileName in files: # Check if the file already exists
                    send_data += "File already exists."
                else: # Write the received data to the file
                    with open(os.path.join(SERVER_PATH,fileName), 'wb') as f: 
                        while fileSize > 0: # Loop until file is received completely
                            readBytes = conn.recv(SIZE) # Read bytes from the client
                            f.write(readBytes) # Write the bytes to the file
                            fileSize -= SIZE # Decrement the number of bytes read
                    send_data += "File uploaded"

            conn.send(send_data.encode(FORMAT)) # Respond to client

        # DOWNLOAD command - downloads a file from the server folder to the client
        elif cmd == "DOWNLOAD":
            files = os.listdir(SERVER_PATH) # Get all files in the server folder
            fileName = data[1] # Get the file name being uploaded
            filePath =  SERVER_PATH + "/" + fileName # Path to file in serverfolder

            # Check if the file exists
            if fileName  in files:
                fileSize = os.path.getsize(filePath)

            # Respond to client if the file does not exist
            else:
                fileSize = -1
                send_data += fileName + " NOT FOUND. Enter a valid file (Use DIR to see available files)"

            conn.send(f"{fileSize}".encode(FORMAT))

            # Send file if it exists
            if fileSize > 0:
                # Open file to be downloaded
                with open(filePath, "rb") as f: 
                    while fileSize > 0: # Loop until file is read completely
                        readBytes = f.read(SIZE) # Read in bytes of the buffer size
                        conn.sendall(readBytes) # Send the bytes
                        fileSize -= SIZE # Decrement the number of bytes read
                send_data += "File downloaded"

            conn.send(send_data.encode(FORMAT)) # Respond to client
            print()
        # DELETE command - delete a file from the server folder
        elif cmd == "DELETE":
            files = os.listdir(SERVER_PATH) # Get all files in the server folder
            file_name = data[1] # Get the file to be deleted

            if file_name in files: # Check if the file is in the server folder
                os.remove(SERVER_PATH + "/" + file_name) # Delete the file
                send_data += file_name + " was deleted from the server."
            else: # File does not exist
                send_data += file_name + " NOT FOUND. Enter a valid file (Use DIR to see available files)"

            conn.send(send_data.encode(FORMAT)) # Send client reponse

        # DIR command - list all files in the server folder
        elif cmd == "DIR":

            send_data += "FILENAME------------ FILESIZE------------ UPLOAD DATE-------- \n" # Directory header

            files = os.listdir(SERVER_PATH) # Get all files in server folder

            for filename in files:  # Loop each file in the server folder

                # Get the size of the file
                file_size = os.path.getsize(SERVER_PATH + "/" + filename) # Get size in bytes from system
                file_size = file_size / SIZE # Convert to KB
                file_size = round(file_size, 2) # Round to 2 digits
                print_file_size = "{:.2f} KB"
                print_file_size = print_file_size.format(file_size) # Format output

                # Get the date the file was uploaded
                file_date = os.path.getmtime(SERVER_PATH + "/" + filename) # Get date in epoch from system
                file_date = time.gmtime(file_date) # Convert to struct of time elements
                print_file_date = "{}/{}/{} {}:{}" # Format outout using struct elements
                print_file_date = print_file_date.format(file_date[1], file_date[2], file_date[0], file_date[3], file_date[4])

                file_row = "{} {} {}\n" # Format and justify with even spacing
                file_row = file_row.format(filename.ljust(20), print_file_size.ljust(20), print_file_date.ljust(20))

                send_data += file_row # Add the row to the output
            conn.send(send_data.encode(FORMAT)) # Send the directory listing to the client

    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()


if __name__ == "__main__":
    main()

