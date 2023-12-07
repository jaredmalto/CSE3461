import configparser
import logging
import socket as s
import json
import os


PROJECT_2 = "project2"
LOGGING = 'logging'

address_family = s.AF_INET
socket_type = s.SOCK_STREAM

# AUTHOR: JARED MALTO.2

# Parses request and returns the command and parameter fields.
def parse_json(request):
    data = json.loads(request)
    command = data.get("command")
    parameter = data.get("parameter")
    return command, parameter

# Builds a JSON file from the command and parameter request.
# Handles all valid commands.
def build_response_and_handle_commands(command, parameter, user_list):
    response_response = None
    response_parameter = None
    # Upon quit, the current list will be stored in a file for future use.
    if command.upper() == "QUIT":
        response_response = "QUITTING"
        with open('list.txt', 'w') as file:
            file.write(','.join(user_list))
    # During create will officially assign the list with the parameter being
    # the first element to keep track of the list name
    elif command.upper() == "CREATE":
        if not user_list or user_list == ['']:
            print(user_list)
            if not user_list:
                user_list.append(parameter)
            elif user_list == ['']:
                user_list[0] = parameter
            response_response = "CREATE successful"
            response_parameter = f"Created list {parameter}"
        else:
            response_response = "CREATE Unsuccessful"
            response_parameter = f"Active list exists"
    # Adds an element not already in the list
    elif command.upper() == "ADD":
        if parameter not in user_list and user_list:
            user_list.append(parameter)
            print(user_list)
            response_response = "ADD successful"
            response_parameter = f"Added {parameter} to list"
        else:
            response_response = "ADD unsuccessful"
            response_parameter = f"Item {parameter} is in list or list does not yet exist"
    # Deletes a list with a given name
    elif command.upper() == "DELETE":
        if user_list[0] == parameter or not user_list:
            user_list.clear()
            print(user_list)
            response_response = "DELETE successful"
            response_parameter = f"List {parameter} deleted"
        else:
            response_response = "DELETE unsuccessful"
            response_parameter = f"List {parameter} does not exist"
    # Removes an element already in the list
    elif command.upper() == "REMOVE":
        if parameter in user_list and user_list:
            user_list.remove(parameter)
            print(user_list)
            response_response = "REMOVE successful"
            response_parameter = f"Item {parameter} removed"
        else:
            response_response = "REMOVE unsuccessful"
            response_parameter = f"Item not in list or no list exists"
    # Shows the current state of the list
    elif command.upper() == "SHOW":
        if user_list:
            response_response = "SHOW successful"
            response_parameter = ','.join(user_list)
        else:
            response_response = "SHOW unsuccessful"
            response_parameter = "No active list"

    return json.dumps({"response": response_response, "parameter": response_parameter})

def main():
    # open and read config file
    config_file = configparser.ConfigParser()
    config_file.read('server_config.ini')

    # setup log server log file from config
    server_host = config_file.get(PROJECT_2, "serverHost")
    server_port = config_file.get(PROJECT_2, "serverPort")
    log_file = config_file.get(LOGGING, "logFile")
    log_level = config_file.get(LOGGING, "logLevel")
    log_mode = config_file.get(LOGGING, "LogFileMode")

    logging.basicConfig(filename=log_file, level=log_level, filemode=log_mode)

    # setup sockets and establish connection
    server_socket = s.socket(address_family, socket_type)
    server_socket.bind((server_host, int(server_port)))
    server_socket.listen(1)

    print(f"Listening on {server_host}:{server_port}")
    logging.info(f"Listening on {server_host}:{server_port}")

    quit_flag = False

    # Initialize a list
    user_list = []

    # Check if a list exists already
    # if yes, we want to access it
    if os.path.exists('list.txt'):
        with open('list.txt', 'r') as file:
            user_list = file.read().split(',')

    while not quit_flag:
        # establish a connection when there is a request
        connection, address = server_socket.accept()
        try:
            print(f"Connection from {address} has been established")
            logging.info(f"Connection from {address} has been established")

            while not quit_flag:
                # Allow 1024 bits to come in and print when we receive
                request = connection.recv(1024)
                print(f"Received: ", request)
                logging.info(f"Received: " + request.decode())

                # process the request
                command, parameter = parse_json(request)
                logging.info("Building response...")

                json_response = build_response_and_handle_commands(command, parameter, user_list)
                # send back the request
                connection.send(json_response.encode())
                print("Response sent: " + json_response)
                logging.info("Response sent: " + json_response)

                # when the user wants to quit
                if command.upper() == "QUIT":
                    print("Shutting down...")
                    logging.info("Shutting down...")
                    connection.close()
                    quit_flag = True



        except Exception as e:
            print(f"Error: {e}")
            logging.error(e)


if __name__ == '__main__':
    main()

