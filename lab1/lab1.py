import configparser
import logging

# Reads and prints each field of the config file to the
# console and the log file
def print_to_console_and_logger(config_file):
    # print config file to screen and logger
    for section in config_file.sections():
        print(f"[{section}]")
        logging.info(f"[{section}]")
        for key, value in config_file.items(section):
            print(f"{key}= {value}")
            logging.info(f"{key}= {value}")
        print("\n")

# Exits the program.
def shut_down():
    print("Shutting down ...")
    logging.info("Shutting down ...")
    exit()

# Builds the string with the first token capitalized.
def process_string(tokens):
    processed_string = ''

    # Check if there is a 0 index, if yes we make it uppercase
    if len(tokens) > 0:
        tokens[0] = tokens[0].upper()

    # while there are tokens in the list, 
    # we can empty it with spaces in between
    while len(tokens) > 0:
        word = tokens.pop(0)
        processed_string += word
        if len(tokens) > 0:
            processed_string += ' '

    return processed_string


def main():
    # open and read config file
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')

    # setup logger
    logging.basicConfig(filename="logger.log", level=logging.INFO)
    logging.info('hello')

    print_to_console_and_logger(config_file)
    
    quit_entered = False

    # we want to keep prompting until the user enters quit as the first token
    while not quit_entered:

        user_string = input('Enter a string: ')
        print()
    
        # tokenize the input, using only whitespace as separators
        tokens = user_string.split()

        # check if first token is quit. if yes, quit
        if tokens[0].lower() == 'quit': 
            quit_entered = True
            shut_down()

        # if not, process the string
        processed_string = process_string(tokens)

        # output the strings
        print('You entered: ' + user_string)
        logging.info('You entered: ' + user_string + '\n')

        print('Processed string: ' + processed_string + '\n')
        logging.info('Processed string: ' + processed_string + '\n')

if __name__ == '__main__':
    main()

