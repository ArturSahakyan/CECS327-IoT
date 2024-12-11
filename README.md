# CECS327-IoT
Python scripts written to handle communication between Dataniz IoT systems and MongoDB database. A part of CECS327 class @ CSULB.

## Database
First you will need a MongoDB database using Atlas that's already connected to Dataniz. Make sure to remember the username and password for the connection string as you will need it later

## Server
On your server's terminal you will first need to do some setup

You need a command for setting an environment variable

If on Windows your \<Command> will be "set"

If on Linux your \<Command> will be "export"

#
Run the following first:

\<Command> PORT=\<choose one, i.e. 3000>

\<Command> DBUSER=\<your username from before>

\<Command> DBPASS=\<your password from before>
#
Now you are good to run the script on that same terminal

"python" on Windows or "python3" on Linux

python iot_server.py
#
## Client
On your client you are free to just run the script from the get-go

Windows: python iot_client.py

Linux: python3 iot_client.py

It will prompt you for the IP then the Port so fill those in as needed
Once connected it will prompt you to input a number 1, 2, or 3 representing each query

ONLY INPUT THE NUMBER, do not type anything besides just the number 1, 2, or 3

Type 4 to quit
