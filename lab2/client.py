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
            else:
                print("Parameter: " + response_json.get("parameter"))


if __name__ == '__main__':
    main()

