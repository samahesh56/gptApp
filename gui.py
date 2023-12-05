import tkinter as tk
from conversation import send_message, reset_conversation, load_conversation

class Main(tk.Frame):
    def __init__(self, parent, *args, **kwargs): #*args allows for more inputs into the frame, **kwargs for dictionary value/pairs. 
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent # Instantiates frame to parent widget  
        
        self.user_input_entry = tk.Entry(self, width=80) # User-input 
        self.user_input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5) # "packs" input into parent frame

        self.load_button = tk.Button(self, text="Load", command=self.on_load_button_click)
        self.load_button.pack(expand=True, padx=5, pady=5)

        send_button = tk.Button(self, text="Send", command=self.on_send_button_click) #send button initiates call 
        send_button.pack(side=tk.RIGHT, padx=5, pady=5) # "packs" send button in frame 

        self.reset_button = tk.Button(self, text="Reset Conversation", command=self.on_reset_button_click)
        self.reset_button.pack(expand=True, padx=5, pady=5)

        # Main conversation text widget
        self.conversation_text = tk.Text(self.parent, state='normal', wrap=tk.WORD) 
        self.conversation_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True) # packs the textbox frame 

    def on_send_button_click(self):
        user_input = self.user_input_entry.get() # gets the user input 
        self.user_input_entry.delete(0, tk.END) # deletes the entry in the box 

        send_message(user_input, self.conversation_text) #conversation_text is gpt response it takes in (the base prompt)

    def on_reset_button_click(self):
        reset_conversation()
        self.conversation_text.delete("1.0", tk.END)

    def on_load_button_click(self):
        conversation = load_conversation()

        messages = conversation.get('messages', [])

        self.conversation_text.delete(1.0, tk.END)

        for message in messages:
            role = message["role"]
            content = message["content"]
            self.conversation_text.insert(tk.END, f"{role.capitalize()}: {content}\n")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("GPT App")
    Main(root).pack(side="top", fill="both", expand=True)
    root.mainloop()