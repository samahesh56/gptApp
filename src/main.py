import logging, os
import tkinter as tk
from conversation_logic import ConversationLogic
from configuration import ConfigManager
from gui import Main

if __name__ == "__main__": #main start method for the program 
    logging.basicConfig(filename='gpt_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Initialize python logging. 
    
    root = tk.Tk() # assembles the tkinter root
    root.title("GPT App") # change title here

    config_manager = ConfigManager(config_path=os.path.join("", 'configs.json')) # change initial config path if necessaary. Creates instance of ConfigManager 

    conversation_logic = ConversationLogic(config_manager) # creates an instance of ConversationLogic(), with config file path sent in.

    Main(root, conversation_logic).pack(side="top", fill="both", expand=True) # Creates an instance of Main (GUI) 
    root.mainloop() # starts GUI  
