import json, tiktoken
from openai import OpenAI

class ConversationLogic:
    def __init__(self):
        self.client = OpenAI() # allows OpenAI instance "self.client" to run, allowing OpenAI Methods


    def chat_gpt(self, user_input, model, max_tokens=1000, max_messages=4):
        conversation_state = self.load_conversation()
        messages = conversation_state.get('messages', [])


        #Truncate conversation history if it exceeds max_tokens
        #total_tokens = 0
        #truncated_messages = []
    
        #Use the truncated conversation history
        #messages = truncated_messages

        prompt = f"{user_input}"
        
        #last_conversation = self.get_last_gpt_response() # loads the last response, appends to the user input for the basic prompt

        #improved_prompt = "I am working on a gpt-API script in python. I am using the GPT model to assist me with building and debugging my code. Provide me with guidance, suggestions, and any necessary code samples to help me resolve this issue? I would appreciate detailed explanations and examples to help me understand the solution better. Thank you!"
        #improved_prompt = "I am working on a 300-500 word essay. Provide me with guidance, suggestions, and any necessary help I require. Thank you!"
        messages.append({"role": "system", "content": "You are an assistant providing help with any issues."})
        messages.append({"role": "user", "content": prompt })

        response = self.client.chat.completions.create( 
            model=model,
            messages=messages,
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
        system_message = "You are an assistant providing help with any issues." # Edit this as the main prompt 
        user_message = "What can you help me with today?" # Edit this as the main prompt response 
        messages = [
            
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
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
        
    def calculate_token_costs(self, token_counts, model_type):
        """
        Calculate the costs associated with the tokens used in a program.

        Parameters:
        token_counts (list): The counts of tokens used for each API call.
        model_type (str): The type of GPT model used, can be 'gpt-3.5', 'gpt-4.5-turbo', or 'gpt-4'.

        Returns:
        float: The total cost of the conversation.
        """
        
        # Total token count for the conversation
        total_tokens = sum(token_counts)
        
        # Pricing per 1000 tokens for different models
        pricing = {
            'gpt-3.5': {'input': 0.0010, 'output': 0.0020},
            'gpt-4.5-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-4': {'input': 0.03, 'output': 0.06}
        }
        
        # Check if provided model_type is valid
        if model_type not in pricing:
            raise ValueError("Invalid model_type provided. Please use 'gpt-3.5', 'gpt-4.5-turbo', or 'gpt-4'.")
        
        # Calculate costs for both input and output
        input_cost_per_1000 = pricing[model_type]['input']
        output_cost_per_1000 = pricing[model_type]['output']

        # Calculate the total cost based on input/output
        total_cost = (total_tokens / 1000) * (input_cost_per_1000 + output_cost_per_1000)
        
        return total_cost

    def test_token_costs(self, token_counts, model_type):
        # Use this method for testing the token cost calculation
        total_cost = self.calculate_token_costs(token_counts, model_type)
        print(f"Total cost of the conversation: ${total_cost:.4f}")

if __name__ == "__main__":
    logic = ConversationLogic()
    logic.test_token_costs([57, 79, 274, 296, 329], 'gpt-3.5')

