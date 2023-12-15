import json, tiktoken, os 
from openai import OpenAI, APIConnectionError, AuthenticationError
from models import Message #Not working currently, import fix in the future 

class ConversationLogic:
    def __init__(self):
        self.config_path='configs.json' # change config path as needed
        self.createfiles() # creates .env and .configs file for the user's first launch 
        self.config=self.load_config(self.config_path) # load current config settings 
        self.api_key=self.config.get('OPENAI_API_KEY', 'YOUR_DEFAULT_API_KEY_HERE')
        self.client = OpenAI(api_key=self.api_key) # starts an instance of OpenAI's client 
        self.conversation_file_path = self.config.get( 
            'conversation_file_path', os.path.join('data', 'conversation.json')
            ) # conversation_file_path connects the current file path to the main conversation file.

        # These are general values. The config files overrwrites the general values, if they are different. 
        self.filename=self.config.get('conversation_file_path', 'data/conversation.json') # sets the filename for the main prompt 
        self.model = self.config.get('model', 'gpt-3.5-turbo-1106') 
        self.system_message = self.config.get('system_message', 'You are an assistant providing help with any issues.') 
        self.user_message = self.config.get('user_message','What can you help me with today?') 
        self.assistant_message = self.config.get('assistant_message', 'Hi, how can I help you today?')
        self.max_tokens = self.config.get('max_tokens', 750)

    def chat_gpt(self, user_input):
        """Performs the API call, and inputs the given user input from the GUI to perform the call.
        
        'messages' is the root of the json conversation file. It has one key, 'messages'. 
        messages is a list that contains dictionaries, each one represent a message in the entire conversation
        Each message in the list is a dictionary with two key-value pairs, "role" and "content"
            Role: specifies the role of the entity sending the message. This can either be 'system', 'user', or 'assistant' 
            Content: specifies the context of the message given by the entity (role)

        Remember that the GPT reads the length of 'messages' when trying to providing responses. Basic conversation trimming is performed to reduce the size of input calls in lengthy conversations. 
            
        Below is an example message '[]' held in the .json 
            {
                "messages": [
                    {
                    "role": "system",
                    "content": "You are an assistant providing help for any task, utilizing context for the best responses"
                    },
                    {
                    "role": "user",
                    "content": "What can you help me with today?"
                    },
                    {
                    "role": "assistant",
                    "content": "Hi there! How can I help you today?"
                    }
                ]
            }  
        """

        conversation_state = self.load_conversation() # loads the current conversation
        messages = conversation_state.get('messages', []) # gets the conversation from json file

        new_input_tokens = self.count_tokens_in_messages([{"role": "user", "content": user_input}], model=self.model) # calculates the ~amount of input tokens prior to the API call
        remaining_tokens = self.max_tokens - new_input_tokens # This is a prompt safeguard that handles (all) large user inputs. If the user's prompt is large, the conversation is truncated more harshly. This helps reduce costs slightly, at the cost of reducing early context for the GPT. 
        print(f"\n~ input tokens: {new_input_tokens} ~ remaining tokens: {remaining_tokens}")

        messages = self.trim_conversation_history(messages, remaining_tokens) # Performs the conversation truncation, sends in conversation and the tokens left to use. This new message holds what the api call can handle, and omits the oldest message according to the tokens allowed
        messages.append({"role": "user", "content": user_input }) # appends the newest message to the conversation (messages)
        # IMPORTANT: Due to the trim function, chatGPT may lose context of the system message. In the future, introduce a method for checking if the system message is in the input, and reintroduce it if neceessary. 

        try:
            response = self.client.chat.completions.create( # This is the client call to chatGPT
                model=self.model, # inputs given model type 
                messages=messages, # inputs the given conversation (truncated)
                max_tokens=self.max_tokens, # a "limiter" that helps truncate conversations
            )

            total_tokens_used = response.usage.total_tokens # calculates total tokens used in api call using chatgpt call for total tokens. LOG THESE FOR DEBUGGING, ETC
            input_tokens = response.usage.prompt_tokens
            response_tokens = response.usage.completion_tokens
            model_type = response.model
            stop_reason = response.choices[0].finish_reason
            print(f"Total tokens used for API call: {total_tokens_used} | Total Input: {input_tokens} | Total Reponse: {response_tokens}\nModel Used: {model_type} | API Stop Reason: {stop_reason}")

            response = response.choices[0].message.content # this is the API call to get the latest gpt response 
            self.update_conversation_state(user_input, response) # updates the conversation with the latest input and response

            return response, None # response is returned to display in gui, None is returned to signal no errors. 
        except AuthenticationError as auth_error:
            return None, (str(auth_error))
        except APIConnectionError as conn_error:
            return None, (str(conn_error))

    def load_conversation(self, filename=None): # Attempts to load the given file 
        """Attempts to read the conversaition.json file

        Loads this content as a JSON object, which is a key/value pair
        messages is the list of messages in the conversation like this: [messages: {"role": ~, "content":, ~}, {}, etc]
        the messages hold the API model references (role, content) that contribute to prompt phrasing. 
        prompt is read in the JSON file, assigning either user/assistant pairs to be interpreted by the GPT"""

        if filename is None:
            filename = self.filename # if there is no file found, it is given the configured path. In this case, its data\conversation

        try:
            with open(filename, 'r') as file: 
                loaded_conversation = json.load(file) # loads the contents of given file 
                if filename != self.conversation_file_path: # if the given file path (conversation) does not match the current file path, a new file path is set to the filepath.
                    self.conversation_file_path = filename  # Update the conversation_file_path if a different file is loaded
                return loaded_conversation # returns the given conversation of the file 
        except FileNotFoundError: # if it cannot find the given file, it creates a new conversation.json file for the user. 
            print(f"Conversation file not found. Creating a new one.")
            self.reset_conversation() # Resets the conversation to default settings 
        
    def save_conversation_to_file(self, filename, messages): # Writes a conversation to save it, according to the given filename. Saves to data/. 
        with open(filename, 'w') as file:
            json.dump({"messages": messages}, file)

    def update_conversation_state(self, user_input, gpt_response):
        messages = self.load_conversation().get('messages', [])

        # Update with new information
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": gpt_response})

        # Save the updated state
        self.save_conversation_to_file(self.filename, messages)

    def reset_conversation(self):
        # Update the conversation state with the default messages
        messages = [        
            {"role": "system", "content": self.system_message}, # CHANGE THIS TO A DEFAULT MESSAGE (otherwise config changes will change this system message)
            {"role": "user", "content": self.user_message},
            {"role": "assistant", "content": self.assistant_message}
        ]
        # Save the updated state
        self.save_conversation_to_file(self.filename, messages)

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
    
    def load_config(self, config_path): # loads the configs 
        with open(config_path, 'r') as file:
            return json.load(file)
        
    def update_settings(self, new_settings):
        self.model = new_settings.get('model', self.model)
        self.max_tokens = new_settings.get('max_tokens', self.max_tokens)
        self.system_message = new_settings.get('system_message', self.system_message)
        self.user_message = new_settings.get('user_message', self.user_message)
        self.assistant_message = new_settings.get('assistant_message', self.assistant_message)
        self.api_key = new_settings.get('OPENAI_API_KEY', self.api_key)
        self.client = OpenAI(api_key=self.api_key)

        # Update other settings as needed

    def createfiles(self):
        default_config = {
            "model": "gpt-3.5-turbo-1106",
            "max_tokens": 500,
            "system_message": "You are an assistant providing help for any task, utilizing context for the best responses",
            "user_message": "What can you help me with today?",
            "assistant_message": "Hi there! How can I help you today?",
            "conversation_file_path": "data/conversation.json",
            "OPENAI_API_KEY": "YOUR_API_KEY_HERE",
            }

        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as file:
                json.dump(default_config, file)
                print(f"Config file created: {self.config_path}")

