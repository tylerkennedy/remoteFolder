import os
import socket
import tqdm
import time
import csv

IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
CLIENT_PATH = "clientFolder"

def main():
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    while True:  ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        data = input("> ") 
        data = data.split(" ")

        cmd = data[0]
        cmd = cmd.upper() # Commands work in either upper or lower case

        # HELP command - lists all command options
        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))

        # LOGOUT command - disconnects client from server
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        
        # UPLOAD command - uploads a new file from the client to the server folder
        elif cmd == "UPLOAD":

            files = os.listdir(CLIENT_PATH) # Get files in the client folder
            fileName = data[1] # Get the file name to be sent
            filePath = CLIENT_PATH + "/" + fileName # Path to file in client folder

            if fileName in files: # Check that the file is in the client folder
                fileSize = int(os.path.getsize(filePath)) # Get the size of the file in bytes

                client.send(f"{cmd}@{fileName}@{fileSize}".encode(FORMAT)) # Send command, file name and file size to server

                progressBar = tqdm.tqdm(range(fileSize), f"Uploading {fileName}", unit="B", unit_scale=True, unit_divisor=1024, mininterval=0) # Progress bar for upload

                with open("fileUploadTime.csv", 'a', encoding='UTF8') as timeFile: # Open file for saving upload times

                    writer = csv.writer(timeFile) # Handles writes to csv file

                    startTime = time.perf_counter() # Get the start time (0)
                    ogFileSize = fileSize # Keep an unaltered original file size
                    writer.writerow(['Time', 'Bytes']) # Write the header to the csv file
                    writer.writerow([startTime, -(fileSize - ogFileSize)]) # Write the start time and the number of bytes sent
                    # Open the file to be uploaded
                    with open(filePath, "rb") as f: 
                        while fileSize > 0: # Loop until file is read completely
                            readBytes = f.read(SIZE) # Read in bytes of the buffer size
                            client.sendall(readBytes) # Send the bytes
                            progressBar.update(len(readBytes)) # Update the progress bar

                            elaspsed = time.perf_counter() - startTime # Get the number of seconds since the start
                            writer.writerow([elaspsed, -(fileSize - ogFileSize)]) # Write the elapsed time and the number of bytes sent

                            fileSize -= SIZE # Decrement the number of bytes left to be read
                progressBar.close()
                print()

            else: # File not found in client folder
                fileName = "NOFILE" 
                fileSize = "0"
                client.send(f"{cmd}@{fileName}@{fileSize}".encode(FORMAT)) # Send that this file does not exists and let the server know

        # DOWNLOAD command - downloads a file from the server folder to the client folder
        elif cmd == "DOWNLOAD":
            fileName = data[1] # Get the file name to be sent
            filePath = CLIENT_PATH + "/" + fileName # Path to file in client folder

            client.send(f"{cmd}@{fileName}".encode(FORMAT)) # Send command and file name to server

            recievedSize = client.recv(SIZE) # Get a response from the server with the size of the file to be downloaded
            fileSize = int(recievedSize)

            if(fileSize > 0): # Make sure the file exists on the server
                progressBar = tqdm.tqdm(range(fileSize), f"Downloading {fileName}", unit="B", unit_scale=True, unit_divisor=1024) # Progress bar for download

                with open("fileDownloadTime.csv", 'a', encoding='UTF8') as timeFile: # Open file for saving download times

                    writer = csv.writer(timeFile) # Handles writes to csv file

                    startTime = time.perf_counter() # Get the start time (0)
                    ogFileSize = fileSize # Keep an unaltered original file size
                    writer.writerow(['Time', 'Bytes']) # Write the header to the csv file
                    writer.writerow([startTime, -(fileSize - ogFileSize)]) # Write the start time and the number of bytes received

                    with open(os.path.join(CLIENT_PATH,fileName), 'wb') as f: 
                        while fileSize > 0: # Loop until file is received completely
                            readBytes = client.recv(SIZE) # Read bytes from the server
                            f.write(readBytes) # Write the bytes to the file
                            progressBar.update(len(readBytes)) # Update the progress bar

                            elaspsed = time.perf_counter() - startTime # Get the number of seconds since the start
                            writer.writerow([elaspsed, -(fileSize - ogFileSize)]) # Write the elapsed time and the number of bytes received

                            fileSize -= SIZE # Decrement the number of bytes received
                progressBar.close()
                print()

        # DELETE command - delete a file from the server folder
        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))

        # DIR command - list all files in the server folder
        elif cmd == "DIR":
            client.send(cmd.encode(FORMAT))

        # HELP command - lists all command options
        else:
            print("Command not found, please enter a valid option")
            cmd = "HELP"
            client.send(cmd.encode(FORMAT))


    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()