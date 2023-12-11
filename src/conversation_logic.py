import json, tiktoken, os 
from openai import OpenAI
from models import Message 

class ConversationLogic:
    def __init__(self, config_path='configs.json'):
        self.config=self.load_config(config_path)
        self.conversation_file_path = self.config.get('conversation_file_path', os.path.join('data', 'conversation.json'))

        self.client = OpenAI() # allows OpenAI instance "self.client" to run, allowing OpenAI Methods
        self.model = self.config.get('model', 'gpt-3.5-turbo-1106') 
        self.system_message = self.config.get('system_message', 'You are an assistant providing help with any issues.') 
        self.user_message = self.config.get('user_message','What can you help me with today?' ) 
        self.max_tokens = self.config.get('max_tokens', 750)


    def chat_gpt(self, user_input, model, max_tokens):
        conversation_state = self.load_conversation() # loads the current conversation
        messages = conversation_state.get('messages', []) # gets the conversation from json file

        new_input_tokens = self.count_tokens_in_messages([{"role": "user", "content": user_input}], model=self.model) # calculates the ~amount of input tokens prior to the API call
        remaining_tokens = max_tokens - new_input_tokens # This is a prompt safeguard that handles (all) large user inputs. If the user's prompt is large, the power of the api call is reduced at an equal amount of tokens to help reduce the size of incoming responses slightly. 

        #improved_prompt = "I am working on a gpt-API script in python. I am using the GPT model to assist me with building and debugging my code. Provide me with guidance, suggestions, and any necessary code samples to help me resolve this issue? I would appreciate detailed explanations and examples to help me understand the solution better. Thank you!"
        #improved_prompt = "I am working on a 300-500 word essay. Provide me with guidance, suggestions, and any necessary help I require. Thank you!"

        messages = self.trim_conversation_history(messages, remaining_tokens) # Performs the conversation truncation, sends in conversation and the tokens left to use. This new message holds what the api call can handle, and omits the oldest message according to the tokens allowed

        messages.append({"role": "system", "content": self.system_message}) # appends system behavior to the conversation call
        messages.append({"role": "user", "content": user_input }) # appends the newest message to the conversation (messages)

        response = self.client.chat.completions.create( #this is the client call to chatGPT
            model=model, #inputs model type 
            messages=messages, # inputs the conversation details
            max_tokens=max_tokens, # a "limiter" that helps truncate conversations
        )

        total_tokens_used = response.usage.total_tokens # calculates total tokens used in api call using chatgpt call for total tokens 
        input_tokens = response.usage.prompt_tokens
        response_tokens = response.usage.completion_tokens

        print(f"Total tokens used for this call: {total_tokens_used} Total Input: {input_tokens} Total Reponse: {response_tokens}")

        response = response.choices[0].message.content # this is the API call to get the latest gpt response 


        self.update_conversation_state(user_input, response) # updates the conversation with the latest input and response 

        #tiktoken_use = self.count_tokens_in_messages(messages, model)
        #print(f"Total Tiktokens: {tiktoken_use}")

        return response # returns the gpt repsonse 

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
            with open('data\conversation.json', 'r') as file: # opens conversation.json file, reads it 
                return json.load(file) # returns JSON, the dictionary structure which holds the conversation details 
            # Attempts to read the conversaition.json file
            # Loads this content as a JSON object, which is a key/value pair
            # messages is the list of messages in the conversation like this: [messages: {"role": ~, "content":, ~}, {}, etc]
            # the messages hold the API model references (role, content) that contribute to prompt phrasing. 
            # prompt is read in the JSON file, assigning either user/assistant pairs to be interpreted by the GPT
        except FileNotFoundError:
            return {"messages": []}
        
    def save_conversation(self, messages):
        with open('data\conversation.json', 'w') as file:
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

    def count_tokens_in_messages(self, messages, model):
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        if model == model:
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
        
    def trim_conversation_history(self, messages, remaining_tokens):
        # Truncate or omit parts of the conversation to fit within max_tokens
        tokens_used = 0 # initial token amount
        truncated_messages = [] # new list to hold conversation 
 
        for message in reversed(messages): # REVERSES order of reading messages, looking at the newest information in the conversation first. (appends newest -> oldest in the conversation)
            message_tokens = self.count_tokens_in_messages([message], model=self.model) # calculates the current ~amount of tokens in the current message, using the model type (different amount of token costs)
            if tokens_used + message_tokens <= remaining_tokens: # if the tokens used (tokens in the conversation that accumulate during the loop) + the amount of the current message is less than the max_tokens allowed by the api call, that message is added to this conversation
                truncated_messages.insert(0, message) #inserts the newest message to the new conversation list 
                tokens_used += message_tokens # increases the tokens used (in the conversation) per message added to the list (Reversed)
            else:
                break # stops adding messages if the next message were to exceed the token limit 

        return truncated_messages
    
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Config file not found. Using defailt configs")
            return {}
                
