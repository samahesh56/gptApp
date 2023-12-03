from openai import OpenAI
client = OpenAI()

def chat_gpt(prompt, model="gpt-3.5-turbo"):
    messages=[
        {"role": "system", "content": "You are an assistant, skilled in explaining and providing answers for any question given by a user."},
        {"role": "user", "content": prompt}
  ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7  
)
    
    reply = response.choices[0].message.content
    return reply

while True:
    user_input = input("Ask ChatGPT, enter 'exit' or 'quit' to stop: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    response = chat_gpt(user_input)

    print("ChatGPT:", response)