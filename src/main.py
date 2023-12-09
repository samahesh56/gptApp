import tkinter as tk
from conversation_logic import ConversationLogic
from gui import Main

if __name__ == "__main__": #main start method 
    root = tk.Tk()
    root.title("GPT App")

    conversation_logic = ConversationLogic()

    Main(root, conversation_logic).pack(side="top", fill="both", expand=True)
    root.mainloop()
