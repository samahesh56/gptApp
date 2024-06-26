import threading, json, os, tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog as simpledialog, messagebox as messagebox
from datetime import datetime
from threading import Thread
from conversation_logic import ConversationLogic
from configuration import ConfigManager

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
        self.filename = os.path.join('data', 'conversation.json') # initial conversation path

        # Tkinter variables for getting/setting dynamic information 
        self.model_var = tk.StringVar(value=self.conversation_logic.model)
        self.max_tokens_var = tk.IntVar(value=self.conversation_logic.max_tokens)
        self.filename_var = tk.StringVar(value=self.conversation_logic.filename)

        self.init_gui()

        # load the config's initial conversation file if found 
        loaded_conversation = self.conversation_logic.load_conversation(filename=self.filename)
        if loaded_conversation:
            self.conversation_text.yview(tk.END, self.load_conversation_text(loaded_conversation))

    def init_gui(self):
        """Initializes the graphical user interface (GUI) elements. Has 3 columns, 1 row structure. Split into more rows as needed.
        
        This includes setting up the grid elements for the menu bar, and other essential frames. """
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.columnconfigure(0, weight=0) # left-most frame does NOT stretch 
        self.columnconfigure(1, weight=1) # middle frame does stretch
        self.columnconfigure(2, weight=0) # right frame does NOT stretch
        self.rowconfigure(1, weight=1) # entire row (entire app) stretches 

        # GUI layout
        self.create_menu_bar()
        self.create_left_frame()
        self.create_middle_frame()
        self.create_toolbar_frame()
        self.create_right_frame()

    def create_menu_bar(self):
        """Create the Menu Bar with File and Settings options"""

        menu_bar = tk.Menu(self) # a Tkinter Menu holds a dropdown of contents for ease of access.
        self.parent.config(menu=menu_bar) # assigns the menu bar to the parent window(root). This sets the menu bar to the tkinter window.

        # File Menu (Menu Toolbar)
        file_menu = tk.Menu(menu_bar, tearoff=0) 
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Open Conversation", command=self.load_conversation_from_file)
        file_menu.add_command(label="Save As...", command=self.save_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings_menu)
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Menu Toolbar Commands
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_command(label="Load", command=self.load_conversation_from_file)
        menu_bar.add_command(label="ChatGPT Settings", command=self.open_settings_menu)

    def create_left_frame(self): 
        """ Creates the Left Frame, which holds the Title Frame and Conv History Frame.
        
        The Title frame holds dynamic labels, grid, and content/info specifications. """
        background_color = '#2c2f33' # for dark: #2c2f33 | light: #f3f4f6
        frame_color = '#23272a' # for dark: #23272a | light: #e1e4e8
        active_color = '#2c2f33' # for dark: #2c2f33 | light: #d1d6da

        # Left Frame
        left_frame = tk.Frame(self, bd=1, relief="flat", bg=frame_color) # add styling as needeed
        left_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Title Frame
        title_frame = tk.Frame(left_frame, bd=1, relief="raised", bg=active_color)
        title_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        title_frame.columnconfigure(0, weight=1) # Stretch elements within the first column of title frame
        title_frame.rowconfigure(1, weight=1)

        title_label = tk.Label(title_frame, text="Gpt App", font=("Helvetica", 16), bg=active_color, fg='#5865F2') #555 for light
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Filename Label
        self.filename_label = tk.Label(title_frame, text="Selected File: ", font=("Helvetica", 12), bg=active_color, fg='#ffffff') #333 for light
        self.filename_label.grid(row=1, column=0, padx=10, pady=0, sticky=tk.W)

        # Model Label  
        self.model_label = tk.Label(title_frame, font=("Helvetica", 12), bg=active_color, fg='#ffffff')
        self.model_label.grid(row=2, column=0, padx=10, pady=10, in_=title_frame, sticky=(tk.W))
        self.model_options = ['gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-4-1106-preview', 'gpt-4-turbo-preview', 'gpt-4']
        self.model_var.set(self.conversation_logic.model) # set the model var by retrieving the conversation logic
        
        # Create radio buttons for each model option, and display them in new rows. 
        for i, model in enumerate(self.model_options):
            rb = tk.Radiobutton(title_frame, text=model, variable=self.model_var, value=model, command=self.update_title_labels, fg="#ffffff", bg=active_color, selectcolor=background_color)
            rb.grid(row=i+3, column=0, padx=10, pady=2, sticky=tk.W)

        # Max Tokens Frame (A seperate frame to hold widgets together)
        max_tokens_frame = tk.Frame(title_frame, bg=active_color)
        max_tokens_frame.grid(row=len(self.model_options)+3, column=0, padx=10, pady=5, sticky=(tk.W, tk.E))
        max_tokens_frame.columnconfigure(0, weight=0) # Don't stretch first column
        max_tokens_frame.columnconfigure(1, weight=1) # stretch second column as needed

        # Max Tokens Label
        self.max_tokens_label = tk.Label(max_tokens_frame, text="Max Tokens: ", font=("Helvetica", 12), bg=active_color, fg='#ffffff')
        self.max_tokens_label.grid(row=0, column=0, sticky=tk.W)

        # Max Tokens Spinbox
        self.max_tokens_spinbox = tk.Spinbox(max_tokens_frame, from_=0, to=5000, textvariable=self.max_tokens_var, width=7, increment=250, 
                                             font=("Helvetica", 12), command=self.update_title_labels, bg=active_color, fg='#ffffff')
        self.max_tokens_spinbox.grid(row=0, column=1, sticky=tk.W)

        # Clear Conversation Button 
        self.clear_chat_button = tk.Button(max_tokens_frame, width=10, text="Clear Chat", command=self.on_reset_button_click)
        self.clear_chat_button.grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)

        # New Conversation Button
        self.new_chat_button = tk.Button(max_tokens_frame, width=10, text="New Chat", command=self.new_conversation)
        self.new_chat_button.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)

         # Conversation History Frame
        history_frame = tk.Frame(left_frame, bd=1, relief="raised", height=250, bg=active_color) 
        history_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

        # History Label
        conv_history_label = tk.Label(history_frame, text="Conversation History", font=("Helvetica", 16), bg=active_color, fg='#5865F2') #333 for light
        conv_history_label.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W))

        # Creates a Treeview within the history frame
        self.conversation_treeview = ttk.Treeview(history_frame)
        self.conversation_treeview.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.W))
        self.conversation_treeview["columns"] = ("filename") # define columns + column configs below 
        self.conversation_treeview.column("#0", width=0, minwidth=0, stretch=False) # Defines the structure of the treeview as a parent-child relationship. Stretch=false hides this branch structure
        self.conversation_treeview.column("filename", width=200, minwidth=150, stretch=True)
        self.conversation_treeview.heading("filename", text="Filename:", anchor=tk.W)
        self.configure_conversation_treeview() # calls config method for conversation state management in the gui 

        self.update_title_labels()

    def configure_conversation_treeview(self):
        """Configures the conversation history display (Treeview widget)."""
        
        def remove_conversation():
            # Get the selected item
            item_id = self.conversation_treeview.focus()
            if item_id:
                selected_filename = self.conversation_treeview.item(item_id, 'values')[0]
                full_path = os.path.join("data", selected_filename) 
                if messagebox.askyesno("Remove Conversation", f"Are you sure you want to remove '{selected_filename}'?"):
                    curr_conversation = self.conversation_logic.remove_conversation_from_file(full_path)
                    self.load_conversation_text(curr_conversation)
                    self.refresh_treeview()

        def rename_conversation(item_id):
            """ Renames a conversation file given the ID from the treeview.  
            Args:
                item_id: The ID of the item in the conversation treeview to rename. """
            
            current_name = self.conversation_treeview.item(item_id, 'values')[0] # Gets the shortened filename from treeview
            selected_filename = os.path.join("data", current_name) # concatenates data directory to current name.  
            
            current_name = os.path.splitext(os.path.basename(current_name))[0] # Removes .json ext from the filepath
            new_name = simpledialog.askstring("Rename Conversation", "Enter new conversation filename:", initialvalue=current_name)
            
            if new_name: # error handling to ensure user inputs are valid 
                new_name = new_name.replace(" ", "_") + ".json" 
                new_filename = os.path.join("data", new_name) 

                # Rename the file (unless it is conversation.json)
                self.conversation_logic.rename_filename(selected_filename, new_filename)
                
                # If renaming the currently open file, reload it in the GUI
                if selected_filename == self.conversation_logic.filename:
                    curr_conv = self.conversation_logic.load_conversation(new_filename) 
                    self.load_conversation_text(curr_conv)
                
                # Refresh the treeview to reflect changes
                self.refresh_treeview()

        self.refresh_treeview()
            
        # Right-click conversation menu options 
        conv_menu = tk.Menu(self.conversation_treeview, tearoff=0)
        conv_menu.add_command(label="Remove", command=remove_conversation)
        conv_menu.add_command(label="Rename", command=lambda: rename_conversation(self.conversation_treeview.focus()))

        def on_right_click(event):
            item_id = self.conversation_treeview.identify_row(event.y)
            if item_id:
                # Show the context menu
                conv_menu.post(event.x_root, event.y_root)
            self.conversation_treeview.selection_set(item_id)

        self.conversation_treeview.bind("<Button-3>", on_right_click) # <Button-2> or <Button-3> depending on platform

        # Function to load conversation when a filename is double clicked
        def on_double_click(event):
            item_id = self.conversation_treeview.focus() # holds ID of selected item 
            selected_filename = self.conversation_treeview.item(item_id, "values")[0] # retrieve filename of given id's associated value (file) 
            full_path = os.path.join("data", selected_filename) 
            curr_conversation = self.conversation_logic.load_conversation(full_path)
            self.load_conversation_text(curr_conversation)
        
        self.conversation_treeview.bind("<Double-1>", on_double_click) # Bind double click event (double-1 is event)

    def create_middle_frame(self):
        # Middle Frame
        middle_frame = tk.Frame(self, bd=2, relief="raised")
        middle_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(0, weight=1)

        # Display the conversation text section
        self.conversation_text = tk.Text(middle_frame, wrap="word", height=30,  font=("Helvetica", 12))
        self.conversation_text.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scroll Bar:     
        conversation_scroll = tk.Scrollbar(middle_frame, command=self.conversation_text.yview)
        conversation_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.conversation_text['yscrollcommand'] = conversation_scroll.set

    def create_right_frame(self):
        # Right Frame
        right_frame = tk.Frame(self, bd=2, relief="flat") # add styling as needeed
        right_frame.grid(row=1, column=2, rowspan=2, sticky=(tk.E, tk.W, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Prompt Frame 
        self.prompt_frame = tk.Frame(right_frame, bd=1, relief="raised")
        self.prompt_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.prompt_frame.columnconfigure([0, 1], weight=1)  # Stretch columns as needed

        self.prompt_1 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 1")
        self.prompt_1.grid(row=0, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_2 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 2")
        self.prompt_2.grid(row=0, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_3 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 3")
        self.prompt_3.grid(row=1, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_4 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 4")
        self.prompt_4.grid(row=1, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_5 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 5")
        self.prompt_5.grid(row=2, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_6 = tk.Button(self.prompt_frame, width=10, height=3, text="Prompt 6")
        self.prompt_6.grid(row=2, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.prompt_text = tk.Text(self.prompt_frame, wrap="word", width=38, height=8,  font=("Helvetica", 12))
        self.prompt_text.grid(row=3, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        #self.MAX_BUTTON_WIDTH = 15  # Maximum button width, adjust as necessary

        # Token Calculator Frame
        self.token_calc_frame = tk.Frame(right_frame, bd=1, relief="raised")
        self.token_calc_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.token_calc_frame.columnconfigure(0, weight=1)
        self.token_calc_frame.rowconfigure(1, weight=1)

        self.token_calc_label = tk.Label(self.token_calc_frame, text="Token Cost Calculator", font=("Helvetica", 16))
        self.token_calc_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    def create_toolbar_frame(self):
        """Create the Toolbar Section"""

        # Toolbar that holds user input, reset button, and send button. 
        toolbar = tk.Frame(self, bd=1, bg="grey", height=50)
        toolbar.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5, pady=5)
        toolbar.columnconfigure(0, weight=1)  # Makes the user_input_entry expand horizontally.
        
        # User Input 
        self.user_input_entry = tk.Text(toolbar, wrap="word", height=6) 
        self.user_input_entry.grid(row=0, column=0,sticky=(tk.E,tk.W), padx=5, pady=5) 

        # Scroll Bar    
        input_scroll = tk.Scrollbar(toolbar, command=self.user_input_entry.yview)
        input_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.user_input_entry['yscrollcommand'] = input_scroll.set

        # Button Frame and associated Buttons 
        button_frame = tk.Frame(toolbar, bg="grey")
        button_frame.grid(row=0, column=2, sticky=tk.E)

        send_button = tk.Button(button_frame, text="Send", command=self.on_send_button_click, width=15, height=2)
        send_button.grid(row=0, column=0, padx=5, pady=10)

        self.reset_button = tk.Button(button_frame, text="Reset Conversation", command=self.on_reset_button_click, width=15, height=2)
        self.reset_button.grid(row=1, column=0, padx=5, pady=10)

        # Status Bar
        self.status_var = tk.StringVar()
        current_time = datetime.now().strftime("%H:%M")
        self.status_var.set(f"Waiting for API call... Last Updated: {current_time} | ChatGPT can make mistakes. Consider double checking important information.") # Set initial status 
        self.status_bar = tk.Label(toolbar, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=5)

    def on_send_button_click(self):
        """Handles the action when the Send button is clicked.
        
        Performs and creates a threead to handle API call """

        user_input = self.user_input_entry.get("1.0", "end-1c") # takes in the user input 
        self.user_input_entry.delete("1.0", tk.END) 
        threading.Thread(target=self.perform_api_call, args=(user_input,)).start()
        self.status_var.set("API call in progress...")

    def perform_api_call(self, user_input):
        """Handles the API call by calling the necessary logic, and uses user-inputs 
        to update and display conversation information to the GUI """
        gpt_response, error_response = self.conversation_logic.chat_gpt(user_input)
        current_time = datetime.now().strftime("%H:%M")
        
        # Check if response is an error message
        if gpt_response is not None:
            # Updates conversation to the conversation_text field
            self.conversation_text.insert(tk.END, f"User: {user_input}\n")
            self.conversation_text.insert(tk.END, f"GPT: {gpt_response}\n\n")
            self.conversation_text.see(tk.END)
            
            # Status bar information  
            self.status_var.set(f"Call Successful! "
                f"Tokens Used: {self.conversation_logic.total_tokens_used} | "
                f"Input Tokens: {self.conversation_logic.input_tokens} | "
                f"Stop Reason: {self.conversation_logic.stop_reason} | "
                f"Model: {self.conversation_logic.model} | "
                f"Time: {current_time}")
        else:
            # Display the error message in the GUI
            if "401" or "APIConnectionError" in error_response:
                messagebox.showinfo("Authentication Error", "Invalid or expired API key. Please check your API key.")
                self.status_var.set(f"API Call Failed! Please check your API Key, or other settings. Time: {current_time} ")

    def on_reset_button_click(self):
        """Handles the action when the Reset Conversation button is clicked.

        Resets the conversation in the conversation text widget (clears the conversation in the gui) """

        if messagebox.askyesno("Clear Chat", f"Are you sure you want to clear '{self.conversation_logic.filename}'?\n You cannot undo this action."):
            curr_conv = self.conversation_logic.reset_conversation() # reset function call
            #self.conversation_text.delete("1.0", tk.END)
            self.load_conversation_text(curr_conv)

    def load_conversation_text(self, conversation):
        """Updates the conversation text in the GUI based on the loaded conversation from a file"""

        messages = conversation.get('messages', [])
        self.conversation_text.delete(1.0, tk.END)
        self.update_title_labels()

        for message in messages[2:]:  # Assuming you want to skip the system and user messages to be displayed in the text-field
            role = message["role"]
            content = message["content"]
            self.conversation_text.insert(tk.END, f"{role.capitalize()}: {content}\n")

    def load_conversation_from_file(self):
        """ Opens the data/ directory to view and load a .json conversation.
        
        filedialog loads a window to choose from existing .json files, thus returning a filename when chosen
        If the loaded filename is different from the default filename (which is set to data/conversation.jon), the filename is changed in real time """

        filename = filedialog.askopenfilename(  
            initialdir="data/conversation", # where to open to 
            title="Open Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")) 
        )
        if filename: 
            curr_conversation = self.conversation_logic.load_conversation(filename) # load the given file's conversation
            self.filename_var.set(filename)
            self.update_title_labels()
            self.load_conversation_text(curr_conversation) # display the conversation in the gui.

    def save_conversation(self):
        """Opens a window to "Save As" the current conversation to a JSON file."""

        filename = filedialog.asksaveasfilename(
            initialdir="data/",
            title="Save Conversation",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"

            current_messages = self.conversation_logic.load_conversation().get('messages', []) # Methods used to save the conversation. Load the current conversation, and save it to file. 
            self.conversation_logic.save_conversation_to_file(filename, current_messages)
            self.refresh_treeview()
            messagebox.showinfo("Save", "The conversation has been saved.")

    def open_settings_menu(self):
        """Opens the settings window for configuring ChatGPT settings
        
        Apply button applies the changes in real time through the update_settings() method in ConversationLogic()"""

        settings_window = tk.Toplevel(self.parent) # This creates a sub-window to pop up.
        settings_window.geometry('400x300')
        settings_window.title('Settings') 

        configs = self.conversation_logic.config # loads the current configs in the user's configs.json 

        # Function to update config display on 'apply'
        def update_config():
            configs['model'] = self.model_var.get()
            configs['max_tokens'] = self.max_tokens_var.get()
            configs['system_message'] = system_message_var.get()
            configs['OPENAI_API_KEY'] = api_key_var.get()

            # ... Update other settings here

            self.conversation_logic.update_configs(configs) # updates settings in real-time
            self.update_title_labels()
            settings_window.destroy()  #Disable this if you want to close the settings menu open after apply is pressed. Otherwise, add an alert that says "Settings Changed"

        # Apply button
        apply_button = tk.Button(settings_window, text='Apply', command=update_config) 
        apply_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Model selection
        tk.Label(settings_window, text='Model:').grid(row=0, column=0)
        model_select = ttk.Combobox(settings_window, textvariable=self.model_var) # Dropdown menu for changing models. Text is held in model_var
        model_select['values'] = ('gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-4-1106-preview', 'gpt-4-turbo-preview', 'gpt-4')  # Set available models here 
        model_select.grid(row=0, column=1) # assigns it to column 1. 
        self.model_var.set(configs.get('model'))

        # Max Tokens
        tk.Label(settings_window, text='Max Tokens:').grid(row=1, column=0)
        max_tokens_entry = tk.Entry(settings_window, textvariable=self.max_tokens_var)
        max_tokens_entry.grid(row=1, column=1)
        self.max_tokens_var.set(configs.get('max_tokens'))  # Sets config max tokens

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

    def new_conversation(self):
        """ Function call to handle new unique conversations
        This method handles unique file name generation, filename setting, and 
        resets the prompt to its original state. Updates the GUI as needed. 
        """
        new_filename = self.conversation_logic.create_new_conversation() # create new conv
        curr_conv = self.conversation_logic.load_conversation(new_filename) # load conv 

        # Refresh the GUI with the text, and new file in treeview
        self.load_conversation_text(curr_conv)
        self.refresh_treeview()
        
        # Return the filename in case further action is needed
        return new_filename

    def update_title_labels(self):
        """Updates (and sets) the title frame labels with the correct formatting
        This method displays the necessary instance variables to the GUI.
        """

        configs = self.conversation_logic.config
        new_model = self.model_var.get()
        new_max_tokens = self.max_tokens_var.get()

        def update_config():
            configs['model'] = new_model
            configs['max_tokens'] = new_max_tokens
            self.conversation_logic.update_configs(configs)

        if configs['model'] != new_model or configs['max_tokens'] != new_max_tokens:
            update_config()
        
        current_model_text = "Model: " + self.model_var.get()
        self.model_label.config(text=current_model_text)

        # Token Limit Label 
        #self.conversation_logic.max_tokens = self.max_tokens_var.get() # updates max token instance based on current value in spinbox
        #self.max_tokens_var.set(self.conversation_logic.max_tokens)
        #current_max_tokens_text = "Token Limit: " + str(self.max_tokens_var.get())
        #self.max_tokens_label.config(text=current_max_tokens_text)

        # Selected File: 
        self.filename_var.set(self.conversation_logic.filename)
        current_file_text = "File: " + os.path.basename(self.filename_var.get())
        self.filename_label.config(text=current_file_text)

    def refresh_treeview(self):
        # Refresh the treeview after add/remove/rename operations
        self.conversation_treeview.delete(*self.conversation_treeview.get_children())
        convo_files = self.conversation_logic.get_conversation_files()

        # Populating the treeview with given filenames 
        for filename in convo_files:
            self.conversation_treeview.insert("", tk.END, values=(filename,))

    def exit_application(self):
        # Save if needed, then exit
        self.conversation_logic.save_conversation_to_file(self.conversation_logic.filename, self.messages)
        self.parent.quit()


if __name__ == "__main__": 
    """Start method for testing GUI changes"""
    root = tk.Tk()
    root.title("GPT App") # set the name of the app
    #root.geometry('800x600') # sets size of the window 
    conversation_logic = ConversationLogic(ConfigManager(config_path='configs.json'))

    Main(root, conversation_logic).pack(side="top", fill="both", expand=True)
    root.mainloop()