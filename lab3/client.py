import configparser
import logging
import socket
import json

# Reads and prints each field of the config file to the
# console and the log file

PROJECT_2 = "project2"
LOGGING = 'logging'

address_family = socket.AF_INET
socket_type = socket.SOCK_STREAM

# List of valid commands
commands = ['ADD', 'CREATE', 'DELETE', 'HELP', 'QUIT', 'REMOVE', 'SHOW']

HELP_STRINGS = ["add <list item>        - Adds an item to the current list",
                "create <list>          - Creates a new list",
                "delete <list>          - Deletes a list",
                "help                   - Displays a message showing all available commands",
                "quit                   - Gracefully shuts down both server and client applications",
                "remove <list item>     - Removes an item from the current list",
                "show                   - Displays a numbered list of the list items"
                ]

# AUTHOR MALTO.2

# Builds the string with the first token capitalized. # Returns a list with the
# first element being the command
def process_string(tokens):
    server_request = []
    parameter = ''

    # Check if there is a 0 index, if yes we make it uppercase
    if len(tokens) > 0:
        request = tokens.pop(0)
        server_request.append(request.upper())

    # while there are tokens in the list,
    # we can empty it with spaces in between
    while len(tokens) > 0:
        word = tokens.pop(0)
        parameter += word
        if len(tokens) > 0:
            parameter += ' '

    server_request.append(parameter)

    return server_request

# Verifies request before sending
def verify_request(request):
    valid = True
    if request not in commands:
        valid = False
    return valid


# creates a socket so we can connect
def create_connection(host, port):
    server_socket = socket.socket(address_family, socket_type)
    try:
        server_socket.connect((host, int(port)))
        print(f"Connected to address {host}:{port}")
        logging.info(f"Connected to address {host}:{port}")
        return server_socket
    except Exception as e:
        print(f"Error connecting to server: {e}")
        logging.error(f"Error connecting to server: {e}")
        return None

# turn the user input into JSON
def request_to_json(request_arr):
    # first arg is command, rest is parameter
    command = request_arr.pop(0)
    parameter = request_arr.pop(0)
    json_request = json.dumps({"command": command, "parameter": parameter})
    return json_request

def main():
    # open and read config file
    config_file = configparser.ConfigParser()
    config_file.read('client_config.ini')

    # setup log file from the config
    server_host = config_file.get(PROJECT_2, "serverHost")
    server_port = config_file.get(PROJECT_2, "serverPort")
    log_file = config_file.get(LOGGING, "logFile")
    log_level = config_file.get(LOGGING, "logLevel")
    log_mode = config_file.get(LOGGING, "LogFileMode")

    # setup logger
    logging.basicConfig(filename=log_file, level=log_level, filemode=log_mode)

    connection = create_connection(server_host, server_port)

    quit_entered = False

    # we want to keep prompting until the user enters quit as the first token
    while not quit_entered:

        # keep prompting for string
        user_string = input('Enter a string: ')
        # check for empty string and re-prompt if so
        if len(user_string) == 0:
            print("ERROR: String is empty.")
            logging.error("String is empty.")
        else:
            # log the original string
            logging.info("Original String: " + user_string)
            # tokenize the input, using only whitespace as separators
            tokens = user_string.split()

            # if not, process the string
            server_request = process_string(tokens)
            # We want to check for a help first, as everything we need is stored here.
            if verify_request(server_request[0]):
                if server_request[0] == "HELP":
                    print("usage:")
                    for string in HELP_STRINGS:
                        print("\t" + string)
                elif (server_request[0] == "CREATE" or server_request[0] == "ADD" or server_request[0] == "DELETE"
                        or server_request[0] == "REMOVE") and server_request[1] == '':
                    print("Missing element in command: " + server_request[0])
                    for string in HELP_STRINGS:
                        print("\t" + string)
                else:
                    json_request = request_to_json(server_request)
                    connection.send(json_request.encode())
                    response_str = connection.recv(1024).decode()
                    response_json = json.loads(response_str)
                    logging.info("Response: " + response_str)

                    # response == QUITTING and null param means user entered quit
                    if response_json.get("response") == "QUITTING" and response_json.get("parameter") is None:
                        print("Shutting down...")
                        connection.close()
                        quit_entered = True
                    # If we have something to show
                    if response_json.get("response") == "SHOW successful" and response_json.get("parameter") is not None:
                        # Split the string to something we can iterate over
                        user_list = response_json.get("parameter").split(',')
                        # first element is the name of the list
                        print(user_list[0])
                        index = 1
                        # Print out the items on the list
                        while index < len(user_list):
                            print(index, "\t" + user_list[index])
                            index += 1
                    else:
                        print("Response: " + response_json.get("response"))
            else:
                logging.error("Invalid command. Type 'help' for a list of valid commands.")
                print("Invalid command. Type 'help' for a list of valid commands.")


if __name__ == '__main__':
    main()

