import json, os, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from conversation_logic import ConversationLogic

class Main(tk.Frame): 
    """A class that creates the main GUI frame for the ChatGPTApp"""

    def __init__(self, parent, conversation_logic, *args, **kwargs): 
        """Initializes the GUI frame

        Args:
        parent (tk.Tk or tk.Toplevel): The parent widget
        conversation_logic (ConversationLogic): An instance of the ConversationLogic class
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments """

        super().__init__(parent, **kwargs) 
        self.parent = parent 
        self.conversation_logic = conversation_logic 
        self.filename = os.path.join('data', 'conversation.json') # initial conversation location 
        self.init_gui()

        if self.filename: # loads the current conversation to the text window. (conversation.json)
            self.conversation_logic.load_conversation()
            self.update_conversation_text()


    def init_gui(self):
        """Initializes the graphical user interface (GUI) elements
        
        This includes the menu bar, conversation text widget, and toolbar """

        # Menu Bar
        menu_bar = tk.Menu(self.parent) # a Tkinter Menu holds a dropdown of contents for ease of access. Pass the parent root (self.parent) heree
        self.parent.config(menu=menu_bar) # assigns the menu bar to the parent window(root). This sets the menu bar to the tkinter window.

        # File Menu (Menu Toolbar)
        file_menu = tk.Menu(menu_bar, tearoff=0) 
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Open Conversation", command=self.load_conversation)
        file_menu.add_command(label="Save As...", command=self.save_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings_menu)
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Menu Toolbar Commands
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_command(label="Load", command=self.load_conversation)
        menu_bar.add_command(label="ChatGPT Settings", command=self.open_settings_menu)

        # Main conversation text widget
        self.scrollbar = tk.Scrollbar(self.parent, orient=tk.VERTICAL) 
        self.conversation_text = tk.Text(self.parent, state='normal', wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.conversation_text.yview) # provides scroll wheel for the conversation_text. 

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # pack scroll wheel inside the conversation text 
        self.conversation_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
        
        # Toolbar that holds user input, reset button, and send button. 
        self.toolbar = tk.Frame(self.parent, bd=1, bg="grey")
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.user_input_entry = tk.Entry(self.toolbar, width=80) # User-input 
        self.user_input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5) # "packs" input into parent frame

        send_button = tk.Button(self.toolbar, text="Send", command=self.on_send_button_click) #send button initiates call 
        send_button.pack(side=tk.RIGHT, padx=5, pady=5) # "packs" send button in frame 

        self.reset_button = tk.Button(self.toolbar, text="Reset Conversation", command=self.on_reset_button_click)
        self.reset_button.pack(fill=tk.X, padx=5, pady=5)

    def on_send_button_click(self):
        """Handles the action when the Send button is clicked.
        
        Processes user input and displays GPT response in the conversation text widget """

        user_input = self.user_input_entry.get() # takes in the user input 
        self.user_input_entry.delete(0, tk.END) 
        gpt_response, error_response = self.conversation_logic.chat_gpt(user_input) # performs the API call (chat gpt function call, class conversation_logic)
        
        # Check if response is an error message
        if gpt_response is not None:
            # Updates conversation to the conversation_text field
            self.conversation_text.insert(tk.END, f"User: {user_input}\n")
            self.conversation_text.insert(tk.END, f"GPT: {gpt_response}\n\n")
            self.conversation_text.see(tk.END)
        else:
            # Display the error message in the GUI
            if "401" or "APIConnectionError" in error_response:
                messagebox.showinfo("Authentication Error", "Invalid or expired API key. Please check your API key.")
            
    def on_reset_button_click(self):
        """Handles the action when the Reset Conversation button is clicked.

        Resets the conversation in the conversation text widget (clears the conversation in the gui """

        self.conversation_logic.reset_conversation() # reset function call
        self.conversation_text.delete("1.0", tk.END)

    def update_conversation_text(self):
        """Updates the conversation text in the GUI based on the loaded conversation from a file"""

        conversation = self.conversation_logic.load_conversation(self.conversation_logic.filename)  # loads the current file (and filename) being used
        messages = conversation.get('messages', [])

        self.conversation_text.delete(1.0, tk.END)

        for message in messages[2:]:  # Assuming you want to skip the system and user messages to be displayed in the text-field
            role = message["role"]
            content = message["content"]
            self.conversation_text.insert(tk.END, f"{role.capitalize()}: {content}\n")
  
    def new_conversation(self):
        messagebox.showinfo("New Conversation", "Create a new conversation")
        # Implement the logic for creating a new conversation in ConversationLogic

    def load_conversation(self):
        """ Extremely important loading function.
        
        filedialog loads a window to choose from existing .json files, thus returning a filename when chosen
        If the loaded filename is different from the default filename (which is set to data/conversation.jon), the filename is changed in real time """

        filename = filedialog.askopenfilename(  
            initialdir="data/conversation", # where to open to 
            title="Open Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")) 
        )
        if filename: 
            self.conversation_logic.filename = filename # set the given filename to the filename in ConversationLogic() class to dynamically change filenames.
            self.conversation_logic.load_conversation(filename) # load the given file's conversation
            self.update_conversation_text() # display the conversation in the gui.

    def save_conversation(self):
        """Opens a window to "Save As" the current conversation to a JSON file."""

        filename = filedialog.asksaveasfilename(
            initialdir="data/conversation",
            title="Save Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"

            current_messages = self.conversation_logic.load_conversation().get('messages', []) # Methods used to save the conversation. Load the current conversation, and save it to file. 
            self.conversation_logic.save_conversation_to_file(filename, current_messages)
            messagebox.showinfo("Save", "The conversation has been saved.")

    def open_settings_menu(self):
        """Opens the settings window for configuring ChatGPT settings
        
        Apply button applies the changes in real time through the update_settings() method in ConversationLogic()"""

        settings_window = tk.Toplevel(self.parent) # This creates a sub-window to pop up.
        settings_window.geometry('400x300')
        settings_window.title('Settings') 

        configs = self.conversation_logic.config # loads the current configs in the user's configs.json 

        # Function to update config on 'apply'
        def update_config():
            configs['model'] = model_var.get()
            configs['max_tokens'] = max_tokens_var.get()
            configs['system_message'] = system_message_var.get()
            configs['OPENAI_API_KEY'] = api_key_var.get()

            # ... Update other settings here

            # Save back to configs.json
            with open('configs.json', 'w') as f:
                json.dump(configs, f)

            self.conversation_logic.update_settings(configs) # updates settings in real-time
            settings_window.destroy()  #Disable this if you want to close the settings menu open after apply is pressed. Otherwise, add an alert that says "Settings Changed"

        # Apply button
        apply_button = tk.Button(settings_window, text='Apply', command=update_config) 
        apply_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Model selection
        tk.Label(settings_window, text='Model:').grid(row=0, column=0)
        model_var = tk.StringVar() # creates a selection of String data to get/set. 
        model_select = ttk.Combobox(settings_window, textvariable=model_var) # Dropdown menu for changing models. Text is held in model_var
        model_select['values'] = ('gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-4-1106-preview', 'gpt-4')  # Set available models here 
        model_select.grid(row=0, column=1) # assigns it to column 1. 
        model_var.set(configs.get('model'))

        # Max Tokens
        tk.Label(settings_window, text='Max Tokens:').grid(row=1, column=0)
        max_tokens_var = tk.IntVar() # holds the max token entry as an int
        max_tokens_entry = tk.Entry(settings_window, textvariable=max_tokens_var)
        max_tokens_entry.grid(row=1, column=1)
        max_tokens_var.set(configs.get('max_tokens'))  # Sets config max tokens

        # System Message
        tk.Label(settings_window, text='System Message:').grid(row=2, column=0)
        system_message_var = tk.StringVar()
        system_message_entry = tk.Entry(settings_window, textvariable=system_message_var)
        system_message_entry.grid(row=2, column=1)
        system_message_var.set(configs.get('system_message'))  # Set current system message

        # API key input 
        tk.Label(settings_window, text='Your API key here:').grid(row=3, column =0)
        api_key_var = tk.StringVar()
        api_key_entry = tk.Entry(settings_window, textvariable=api_key_var)
        api_key_entry.grid(row=3, column=1)
        api_key_var.set(configs.get('OPENAI_API_KEY'))

    def exit_application(self):
        # Save if needed, then exit
        self.conversation_logic.save_conversation_to_file(self.conversation_logic.filename, self.messages)
        self.parent.quit()


if __name__ == "__main__": 
    """Start method for testing GUI changes"""
    root = tk.Tk()
    root.title("GPT App") # set the name of the app
    #root.geometry('800x600') # sets size of the window 
    conversation_logic = ConversationLogic()

    Main(root, conversation_logic).pack(side="top", fill="both", expand=True)
    root.mainloop()