import tkinter as tk
from conversation_logic import ConversationLogic
from gui import Main

if __name__ == "__main__": #main start method for the program 
    root = tk.Tk() # assembles the tkinter root
    root.title("GPT App") # change title here

    conversation_logic = ConversationLogic() # creates an instance of ConversationLogic() class that conversation_logic functionality 

    Main(root, conversation_logic).pack(side="top", fill="both", expand=True) # Main is called, starting the program
    root.mainloop() # starts root program 
