import json, tkinter as tk
from openai import OpenAI

client = OpenAI()

DEFAULT_CONVERSATION = {
    "messages": [
        {"role": "system", "content": "You are an assistant providing help with programming"},
        {"role": "user", "content": "What can you help me with today?"}
    ]
}

def send_message(user_input, conversation_text):
    last_conversation = get_last_gpt_response() # 
    prompt = f"{user_input}\n{last_conversation}" # concatenates the user_input with the chat-gpt response as a basic prompt for the GPT to read

    # Call the chat_gpt function or any other relevant logic
    gpt_response = chat_gpt(prompt, model="gpt-3.5-turbo-1106") # change model here

    # Update the conversation state
    update_conversation_state(user_input, gpt_response)

    # Display the conversation in the text widget
    conversation_text.insert(tk.END, f"User: {user_input}\n")
    conversation_text.insert(tk.END, f"GPT: {gpt_response}\n\n")
    conversation_text.see(tk.END)

def chat_gpt(prompt, model):
    #improved_prompt = "I am working on a gpt-API script in python. I am using the GPT model to assist me with building and debugging my code. Provide me with guidance, suggestions, and any necessary code samples to help me resolve this issue? I would appreciate detailed explanations and examples to help me understand the solution better. Thank you!"

    messages = [
        {"role": "system", "content": "You are an assistant providing help with any issues. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    response = response.choices[0].message.content
    return response

def get_last_gpt_response():
    conversation_state = load_conversation() # loads the latest conversation, which is read as the latest dictionary key/value pairs (.json file)
    messages = conversation_state.get('messages', []) # extracts the 'messages' key using get() method. defaults to [] if no keys present
    
    # Find the last assistant response in the conversation
    for i in range(len(messages) - 1, -1, -1): # Iterates over the messages in reverse order, reading the latest message an index length(messages-1), incrementing by -1 to check each message's "role" value 
        if messages[i]["role"] == "assistant": # if the role is an assistant, it is the latest gpt response, and so that content is returned 
            return messages[i]["content"]
    
    return "" # returns "" if no gpt-response is found. 

def load_conversation():
    try:
        with open('conversation.json', 'r') as file: # opens conversation.json file, reads it 
            return json.load(file) # returns JSON, the dictionary structure 
        # Attempts to read the conversaition.json file
        # Loads this content as a JSON object, which is a key/value pair
        # messages is the list of messages in the conversation like this: [messages: {"role": ~, "content":, ~}, {}, etc]
        # the messages hold the API model references (role, content) that contribute to prompt phrasing. 
        # prompt is read in the JSON file, assigning either user/assistant pairs to be interpreted by the GPT
    except FileNotFoundError:
        return {"messages": []}
    
def save_conversation(messages):
    with open('conversation.json', 'w') as file:
        json.dump({"messages": messages}, file)

def update_conversation_state(user_input, gpt_response):
    messages = load_conversation().get('messages', [])

    # Update with new information
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": gpt_response})

    # Save the updated state
    save_conversation(messages)

def reset_conversation():
    # Update the conversation state with the default messages
    save_conversation(DEFAULT_CONVERSATION["messages"])

reset_conversation()

get_last_gpt_response()