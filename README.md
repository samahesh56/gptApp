# An api-based ChatGPT App

The ChatGPT App is a tool that allows users to interact with OpenAI's latest GPT language models through a simple and convenient Python interface. 
This script enables developers to integrate the newest models while efficiently utilizing api costs. 

## Features
- Seamless integration with the OpenAI API. 
- Support for various use cases, including text generation, completion, conversation modeling, as well as conversation history. 
- Customization options for fine-tuning the model's behavior and output.
- Option to save, name, and load conversations of your choosing.

## Getting Started/Contributing
To get started with the this app, follow these steps:
1. Clone the repository by forking this repository. 
1. Install the required Python dependencies.
    - (Recommended) Activate your virtual enviroment 
    - Ensure you have all dependancies by typing `pip install -r requirements.txt`
3. Set up your environment and personal config settings
    - A configs.json file will be created for you. You may change these settings as you see fit. Ensure this is .gitignored. 
5. Begin using the script using main.py, gui.py, or type 'python main.py' in the terminal.

## An Introduction to Prompt Engineering and ChatGPT
It is extremely important to understand the basics of prompt engineering to maximize the effectiveness of this GPT-API App.

### What is Prompt Engineering?
Prompt engineering is the process of crafting an input message used to guide an AI model to generate the best possible response. Think of it as
a way of providing a clear set of instrruction to the AI to best help it understand your query. 

### The Importance of Context
In order to receive the best responses from the AI, you must provide as much context and information to the AI as possible. This helps it
provide meaningful replies that relies on the fine-details of your query. 

### API Costs
Head to "https://openai.com/pricing" for precise, model-specific API pricing. Keep in mind that more input information (conversation history) 
can result in high token usage and costs. The best practice is to balance the amount of information provided to avoid unnecessary costs

### Conversation History and Truncation
This script provides a basic "trimming" function that removes older messages that may otherwise exceed the tokens allowed for the given
api call. Take a closer look into `trim_conversation_history()` function to see how this works. This ultimately 
helps reduce the amount of tokens used to provide the best (and most) context to the GPT while providing low-cost inputs. 

Undersanding the key ideeas of prompt eengineering will help give you the best possible answers when interacting with the API model. 
In the future, this will be more easily implemented by providing static prompts, or utilizing summation methods to reduce costs and give quality responses.
 

