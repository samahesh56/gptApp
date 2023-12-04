import tkinter as tk
from conversation import send_message

class Main(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent # Instantiates frame to parent widget  
        
        self.user_input_entry = tk.Entry(self, width=80) # User-input 

        send_button = tk.Button(self, text="Send", command=self.on_send_button_click)

        # Layout the widgets
        self.user_input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Main conversation text widget
        self.conversation_text = tk.Text(self.parent, state='normal', wrap=tk.WORD)
        self.conversation_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def on_send_button_click(self):
        user_input = self.user_input_entry.get()
        self.user_input_entry.delete(0, tk.END)

        send_message(user_input, self.conversation_text) #conversation_text is gpt response it takes in (the base prompt)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("GPT App")
    Main(root).pack(side="top", fill="both", expand=True)
    root.mainloop()