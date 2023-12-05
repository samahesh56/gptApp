import json
from openai import OpenAI

class ConversationLogic:
    def __init__(self):
        self.client = OpenAI()

    def send_message(self, user_input):
        last_conversation = self.get_last_gpt_response()
        prompt = f"{user_input}\n{last_conversation}"

        gpt_response = self.chat_gpt(prompt, model="gpt-3.5-turbo-1106")
        self.update_conversation_state(user_input, gpt_response)

        return gpt_response

    def chat_gpt(self, prompt, model):
        #improved_prompt = "I am working on a gpt-API script in python. I am using the GPT model to assist me with building and debugging my code. Provide me with guidance, suggestions, and any necessary code samples to help me resolve this issue? I would appreciate detailed explanations and examples to help me understand the solution better. Thank you!"
        #improved_prompt = "I am working on a 300-500 word essay. Provide me with guidance, suggestions, and any necessary help I require. Thank you!"

        messages = [
            {"role": "system", "content": "You are an assistant providing help with any issues. "},
            {"role": "user", "content": prompt }
        ]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )

        response = response.choices[0].message.content
        return response

    def get_last_gpt_response(self):
        conversation_state = self.load_conversation() # loads the latest conversation, which is read as the latest dictionary key/value pairs (.json file)
        messages = conversation_state.get('messages', []) # extracts the 'messages' key using get() method. defaults to [] if no keys present
        
        # Find the last assistant response in the conversation
        for i in range(len(messages) - 1, -1, -1): # Iterates over the messages in reverse order, reading the latest message an index length(messages-1), incrementing by -1 to check each message's "role" value 
            if messages[i]["role"] == "assistant": # if the role is an assistant, it is the latest gpt response, and so that content is returned 
                return messages[i]["content"]
        
        return "" # returns "" if no gpt-response is found. 

    def load_conversation(self):
        try:
            with open('conversation.json', 'r') as file: # opens conversation.json file, reads it 
                return json.load(file) # returns JSON, the dictionary structure which holds the conversation details 
            # Attempts to read the conversaition.json file
            # Loads this content as a JSON object, which is a key/value pair
            # messages is the list of messages in the conversation like this: [messages: {"role": ~, "content":, ~}, {}, etc]
            # the messages hold the API model references (role, content) that contribute to prompt phrasing. 
            # prompt is read in the JSON file, assigning either user/assistant pairs to be interpreted by the GPT
        except FileNotFoundError:
            return {"messages": []}
        
    def save_conversation(self, messages):
        with open('conversation.json', 'w') as file:
            json.dump({"messages": messages}, file)

    def update_conversation_state(self, user_input, gpt_response):
        messages = self.load_conversation().get('messages', [])

        # Update with new information
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": gpt_response})

        # Save the updated state
        self.save_conversation(messages)

    def reset_conversation(self):
        # Update the conversation state with the default messages
        system_message = "You are an assistant providing help with any issues." # Edit this as the main prompt 
        user_message = "What can you help me with today?" # Edit this as the main prompt response 
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        # Save the updated state
        self.save_conversation(messages)

ConversationLogic().reset_conversation()