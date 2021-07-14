# Remote Folder

This is a basic remote folder application. The remote server runs on one shell and hosts the remote folder. A client can connect to the server from another shell in the network. The client has the ability to view files in the remote folder, upload files, download files, and delete files from the remote folder. The client interacts with the server using a command line interface. The project makes use of sockets programming to wirelessly transmit files during upload and download.

## Commands

Start the server

    python server.py
    
Start the client

    python client.py
    
The server stores files in the ``server`` directory and the client stores files in the ``client`` folder.

The client interacts with the server via the following commands:

**CONNECT** – This operation accepts the IP address and port to open a connection to the server. This function is called automatically by the client on launch. The server listens for a request connection and sets up a connection to the client.

**UPLOAD `<filename>`** – This operation accepts a file to be uploaded to the server from the client. The client sends the filename and size to be uploaded. When the server receives this data, it listens for each packet to be sent. The server writes these bytes of data to the file on the server until no more data is sent.

**DOWNLOAD `<filename>`** – This operation accepts a file to be downloaded from the server to the client. The client requests to download a file and sends the filename to the server. The server responds with the file size and starts sending the data. The client accepts the data until it has received the whole file.

**DELETE `<filename>`** – This operation accepts a file to be deleted from the server. The client sends to the server the file to be deleted and the server deletes it if it exists.

**DIR** – This operation displays the contents of the server folder including the names, sizes, and dates of each file. The client makes the request and the server returns the output.
