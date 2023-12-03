import tkinter as tk

from openai import OpenAI
from conversation import load_conversation, save_conversation, update_conversation_state, get_last_gpt_response

client = OpenAI()

def chat_gpt(prompt, model="gpt-3.5-turbo"):
    messages=[
        {"role": "system", "content": "You are an assistant providing help with an API script program. This API scipt program utilizes chatGPT's api inside a python script. "},
        {"role": "user", "content": prompt}
  ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
)
  
    reply = response.choices[0].message.content
    return reply
''' THIS ALLOWS THE USER BASIC FUNCTIONALITY IN THE TERMINAL
while True:
    user_input = input("Ask ChatGPT, enter 'exit' or 'quit' to stop: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    response = chat_gpt(user_input)

    print("ChatGPT:", response)
    '''

def send_message():
    user_input = user_input_entry.get()
    user_input_entry.delete(0, tk.END)

    conversation_text.insert(tk.END, f"Ask ChatGPT what you want: {user_input}\n")

    last_conversation = get_last_gpt_response()

    prompt = f"{user_input}\n{last_conversation}"

    gpt_response = chat_gpt(prompt)
    conversation_text.insert(tk.END, f"GPT: {gpt_response}\n\n")
    conversation_text.see(tk.END)

    update_conversation_state(user_input, gpt_response)

# Initialize the main application window
root = tk.Tk()
root.title("Chat with GPT")

# Create the main layout frames
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP)
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Create the widgets for the top frame
user_input_entry = tk.Entry(top_frame, width=80)
send_button = tk.Button(top_frame, text="Send", command=send_message)

# Layout the widgets in the top frame
user_input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Create the Text widget for showing the conversation
conversation_text = tk.Text(bottom_frame, state='normal', wrap=tk.WORD)
conversation_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# Function to make the conversation text widget autoscroll
def scroll_text(*args):
    conversation_text.see(tk.END)

conversation_text.bind("<KeyPress>", scroll_text)  # Bind the scrolling behaviour        

# Start the main loop
root.mainloop()