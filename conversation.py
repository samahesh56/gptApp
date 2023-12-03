import json

def load_conversation():
    try:
        with open('conversation.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def save_conversation(state):
    with open('conversation_state.json', 'w') as file:
        json.dump(state, file)

def get_last_gpt_response():
    conversation_state = load_conversation()
    return conversation_state.get('gpt_response', '')


def update_conversation_state(user_input, gpt_response):
    # Load existing conversation state
    conversation = load_conversation()

    # Update with new information
    conversation['user_input'] = user_input
    conversation['gpt_response'] = gpt_response

    # Save the updated state
    save_conversation(conversation) #Calls save_conservation to write updated state 