import json
from openai import OpenAI

class ConversationLogic:
    def __init__(self):
        self.client = OpenAI() # allows OpenAI instance "self.client" to run, allowing OpenAI Methods 

    def chat_gpt(self, user_input, model, max_tokens=100):
        ''' 
        conversation_state = self.load_conversation()
        messages = conversation_state.get('messages', [])

        Truncate conversation history if it exceeds max_tokens
        total_tokens = 0
        truncated_messages = []

        for message in reversed(messages):
            # Calculate the tokens in the message
            role_tokens = len(message["role"]) + 2  # role + ": "
            content_tokens = len(message["content"].split())
            total_tokens += role_tokens + content_tokens

            # Check if adding this message exceeds the limit
            if total_tokens > max_tokens:
                break

            truncated_messages.insert(0, message)

        # Use the truncated conversation history
        messages = truncated_messages
        ''' 

        last_conversation = self.get_last_gpt_response() # loads the last response, appends to the user input for the basic prompt
        prompt = f"{user_input}\n{last_conversation}"

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

        self.update_conversation_state(user_input, response)

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
