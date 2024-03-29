import json, os
from openai import OpenAI

class ConfigManager:
    def __init__(self, config_path):
        """
        Initializes the ConfigManager instance.

        Args:
        - config_path (str): The path to the configuration file. """

        self.config_path = config_path
        self.config = {} 

        if not os.path.exists(self.config_path):
            # If config path DNE, create initial files with default configurations
            default_config = {
                "model": "gpt-3.5-turbo-1106",
                "max_tokens": 500,
                "system_message": "You are an assistant providing help for any task, utilizing context for the best responses",
                "user_message": "What can you help me with today?",
                "assistant_message": "Hi there! How can I help you today?",
                "filename": os.path.join('data', 'conversation.json'),
                "OPENAI_API_KEY": "YOUR_API_KEY_HERE",
            }
            default_messages = [
                {"role": "system", "content": default_config['system_message']},
                {"role": "user", "content": default_config['user_message']},
                {"role": "assistant", "content": default_config['assistant_message']}
            ]
            self.create_initial_files(default_config, default_messages)
            
        # Load the configuration settings
        self.config = self.load_config()

    def load_config(self):
        """
        Loads the configuration settings from the configs.json file.

        Returns:
        - dict: A dictionary {} containing the loaded configuration settings. """

        with open(self.config_path, 'r') as file:
            return json.load(file)
        
    def save_config(self):
        """
        Saves the current configuration settings to the configs.json file. """
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file)

    def create_initial_files(self, default_config, default_messages):
        """
        Creates the initial configuration and conversation files with default values.

        Args:
        - default_config (dict): Default configuration settings.
        - default_messages (list): Default conversation messages. """

        self.create_config_file(default_config)
        self.create_conversation_file(default_messages)

    def create_config_file(self, default_config):
        """
        Creates the configuration file with default settings.

        - default_config (dict): Default configuration settings. """

        with open(self.config_path, 'w') as file:
            json.dump(default_config, file)
            print(f"Config file created: {self.config_path}")

    def create_conversation_file(self, default_messages):
        """
        Creates the conversation file with default messages.

        - default_messages (list): Default conversation messages. """

        data_folder = 'data' # creates a data directory/folder if it DNE 
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        filename = self.config.get('filename', os.path.join(data_folder, 'conversation.json'))
        with open(filename, 'w') as file:
            json.dump({"messages": default_messages}, file)
            print(f"Conversation file created: {filename}")

    def update_configs(self, new_configs):
        """
        Updates the configuration settings with new values and saves the changes locally (configs.json) .

        Parameters:
        - new_configs (dict): Dictionary containing any set of new configuration values. """

        # Update Configs 
        self.config['model'] = new_configs.get('model', self.config['model'])
        self.config['max_tokens'] = new_configs.get('max_tokens', self.config['max_tokens'])
        self.config['system_message'] = new_configs.get('system_message', self.config['system_message'])
        self.config['user_message'] = new_configs.get('user_message', self.config['user_message'])
        self.config['assistant_message'] = new_configs.get('assistant_message', self.config['assistant_message'])
        self.config['OPENAI_API_KEY'] = new_configs.get('OPENAI_API_KEY', self.config['OPENAI_API_KEY'])
        self.config['filename'] = new_configs.get('filename', self.config['filename'])

        # Update and add other settings as needed
        self.save_config()