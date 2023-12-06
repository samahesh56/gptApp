import json, tiktoken
from openai import OpenAI

class ConversationLogic:
    def __init__(self, model='gpt-3.5-turbo-1106'):
        self.client = OpenAI() # allows OpenAI instance "self.client" to run, allowing OpenAI Methods
        self.model = model 
        self.system_message = "You are an assistant providing help with any issues."
        self.user_message = "What can you help me with today?"


    def chat_gpt(self, user_input, model, max_tokens=1000, max_messages=4):
        conversation_state = self.load_conversation()
        messages = conversation_state.get('messages', [])

         #Truncate conversation history if it exceeds max_tokens
        #total_tokens = 0
        #truncated_messages = []
    
        #Use the truncated conversation history
        #messages = truncated_messages
        
        #last_conversation = self.get_last_gpt_response() # loads the last response, appends to the user input for the basic prompt

        #improved_prompt = "I am working on a gpt-API script in python. I am using the GPT model to assist me with building and debugging my code. Provide me with guidance, suggestions, and any necessary code samples to help me resolve this issue? I would appreciate detailed explanations and examples to help me understand the solution better. Thank you!"
        #improved_prompt = "I am working on a 300-500 word essay. Provide me with guidance, suggestions, and any necessary help I require. Thank you!"
 
        max_tokens = 1000 - 50

        truncated_messages = self.trim_conversation_history(messages, max_tokens)

        messages = truncated_messages
 
        messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": user_input })

        response = self.client.chat.completions.create( 
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )

        total_tokens_used = response.usage.total_tokens

        print(f"Total tokens used for this call: {total_tokens_used}")

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
        messages = [
            
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": self.user_message}
        ]

        # Save the updated state
        self.save_conversation(messages)

    def count_tokens_in_messages(self, messages, model="gpt-3.5-turbo-1106"):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        if model == "gpt-3.5-turbo-1106":
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # If there's a name, the role is omitted
                        num_tokens += -1  # Role is always required and always 1 token
            num_tokens += 2  # Every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""count_tokens_in_messages() is not presently implemented for model {model}.
    See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
    def trim_conversation_history(self, messages, total_tokens_used):
        # Truncate or omit parts of the conversation to fit within max_tokens
        total_tokens = 0
        truncated_messages = []

        for message in reversed(messages):
            # Include system and user messages
            if message["role"] in ["system", "user"]:
                total_tokens += self.count_tokens_in_messages([message], model=self.model)

                if total_tokens <= total_tokens_used:
                    truncated_messages.insert(0, message)
                else:
                    break

        return truncated_messages
