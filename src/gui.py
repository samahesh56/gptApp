import tkinter as tk
from tkinter import filedialog, messagebox
from conversation_logic import ConversationLogic

class Main(tk.Frame):
    def __init__(self, parent, conversation_logic, file_to_load=None, *args, **kwargs): #*args allows for more inputs into the frame, **kwargs for dictionary value/pairs. 
        super().__init__(parent, **kwargs)
        self.parent = parent # Instantiates frame to parent widget  
        self.conversational_logic = conversation_logic #Creates an instance of ConversationLogic functions
        self.init_gui()

        if file_to_load:
            self.conversational_logic.load_conversation(file_to_load)
            self.update_conversation_text()

        self.parent.bind("<Visibility>", self.on_load_button_click)  # Bind on_load_button_click to Visibility event

    def init_gui(self):
        
        menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_conversation)
        file_menu.add_command(label="Open", command=self.load_conversation)
        file_menu.add_command(label="Save", command=self.save_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.toolbar = tk.Frame(self.parent, bd=1, relief=tk.RAISED, bg="grey")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.new_button = tk.Button(self.toolbar, text="New", command=self.new_conversation)
        self.new_button.pack(side=tk.LEFT, padx=2, pady=2)

        open_button = tk.Button(self.toolbar, text="Open", command=self.load_conversation)
        open_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.save_button = tk.Button(self.toolbar, text="Save", command=self.save_conversation)
        self.save_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.exit_button = tk.Button(self.toolbar, text="Exit", command=self.exit_application)
        self.exit_button.pack(side=tk.LEFT, padx=2, pady=2)
        
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
        user_input = self.user_input_entry.get() # takes in the user input 
        self.user_input_entry.delete(0, tk.END) 
        gpt_response = self.conversational_logic.chat_gpt(user_input, model=self.conversational_logic.model, max_tokens=self.conversational_logic.max_tokens) # performs the API call (chat gpt function call, class conversation_logic)

        self.conversation_text.insert(tk.END, f"User: {user_input}\n")
        self.conversation_text.insert(tk.END, f"GPT: {gpt_response}\n\n")
        self.conversation_text.see(tk.END)

    def on_reset_button_click(self):
        self.conversational_logic.reset_conversation() # reset function call
        self.conversation_text.delete("1.0", tk.END)

    def update_conversation_text(self):
        conversation = self.conversational_logic.load_conversation()  # Modify this based on your ConversationLogic class
        messages = conversation.get('messages', [])

        self.conversation_text.delete(1.0, tk.END)

        for message in messages[2:]:  # Assuming you want to skip the system and user messages
            role = message["role"]
            content = message["content"]
            self.conversation_text.insert(tk.END, f"{role.capitalize()}: {content}\n")
  

    def on_load_button_click(self):
        filename = filedialog.askopenfilename(
            initialdir="data/conversation",
            title="Open Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.conversational_logic.load_conversation(filename)
            self.update_conversation_text()

    def new_conversation(self):
        messagebox.showinfo("New Conversation", "Create a new conversation")
        # Implement the logic for creating a new conversation in ConversationLogic

    def load_conversation(self):
        filename = filedialog.askopenfilename(
            initialdir="data/conversation",
            title="Open Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.conversational_logic.load_conversation(filename)
            self.on_load_button_click()

    def save_conversation(self):
        # You may want to ask the user for a filename or use a default one
        filename = filedialog.asksaveasfilename(
            initialdir="data/conversation",
            title="Save Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.conversational_logic.save_conversation_to_file(filename)
            messagebox.showinfo("Save", "The conversation has been saved.")

    def exit_application(self):
        # Save if needed, then exit
        self.conversational_logic.save_conversation_to_file()
        self.parent.quit()


if __name__ == "__main__": #main start method 
    root = tk.Tk()
    root.title("GPT App") # set the name of the app
    root.geometry('800x600') # sets size of the window 
    Main(root).pack(side="top", fill="both", expand=True)
    root.mainloop()