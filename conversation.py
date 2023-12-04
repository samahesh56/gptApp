import json
from openai import OpenAI
import tkinter as tk

client = OpenAI()

DEFAULT_CONVERSATION = {
    "messages": [
        {"role": "system", "content": "You are an assistant providing help with recipes"},
        {"role": "user", "content": "What can you help me with today?"}
    ]
}

def send_message(user_input, conversation_text_widget):
    last_conversation = get_last_gpt_response()
    prompt = f"{user_input}\n{last_conversation}"

    # Call the chat_gpt function or any other relevant logic
    gpt_response = chat_gpt(prompt)

    # Update the conversation state
    update_conversation_state(user_input, gpt_response)

    # Display the conversation in the text widget
    conversation_text_widget.insert(tk.END, f"User: {user_input}\n")
    conversation_text_widget.insert(tk.END, f"GPT: {gpt_response}\n\n")
    conversation_text_widget.see(tk.END)

def chat_gpt(prompt, model="gpt-3.5-turbo"):
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

def load_conversation():
    try:
        with open('conversation.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"messages": []}
    
def save_conversation(messages):
    with open('conversation.json', 'w') as file:
        json.dump({"messages": messages}, file)

def get_last_gpt_response():
    conversation_state = load_conversation()
    messages = conversation_state.get('messages', [])
    
    # Find the last assistant response in the conversation
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "assistant":
            return messages[i]["content"]
    
    return ""


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

conversation_state = load_conversation()