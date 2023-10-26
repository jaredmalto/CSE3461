import configparser
import logging
import socket as s
import json


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
def build_response(command, parameter):
    # if quit: "response": QUITTING, "parameter": None
    # if NOT quit: "response": COMMAND, "parameter": PARAMETER
    if command.upper() == "QUIT":
        response = "QUITTING"
        return json.dumps({"response": response, "parameter": None})
    else:
        response = command
        return json.dumps({"response": response, "parameter": parameter})


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
                json_response = build_response(command, parameter)
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

