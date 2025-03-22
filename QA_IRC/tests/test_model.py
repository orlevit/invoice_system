from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Create a ChatOpenAI model
model = Ollama(model="qwen:0.5b")

chat_history = []  # Use a list to store messages

# Chat loop
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=query))  # Add user message

    # Get AI response using history
    result = model.invoke(chat_history)
    response = result
    chat_history.append(AIMessage(content=response))  # Add AI message

    print(f"AI: {response}")


print("---- Message History ----")
print(chat_history)
