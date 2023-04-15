def parse_user_details(message) :
    # Get the user's first name
    first_name = message.from_user.first_name
    # Get the user's last name
    last_name = message.from_user.last_name
    # Get the user's username
    username = message.from_user.username
    # Get the user's id
    telegram_user_id = message.from_user.id

    return first_name, last_name, username, telegram_user_id

def parse_arguments(message):
    # Get the user's message
    message_text = message.text
    # Get the user's message split into a list
    message_text_list = message_text.split()

    # Get the arguments
    arguments = message_text_list[1:]

    return arguments
