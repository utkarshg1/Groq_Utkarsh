from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import gradio as gr

# Loading api key into environment
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

# Load the LLM model
model = ChatGroq(model_name="llama3-8b-8192")

# Store the chat history
store = {}
def get_session_history(session_id:str)->BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Write a function to get response from model
def get_response(message:str, history:str)->str:
    # Create a prompt 
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a very helpful assistant"
            ),
            MessagesPlaceholder(variable_name='history'),
            ("human", "{input}"),
        ]
    )
    # Create a runnable chain with prompt
    runnable = prompt | model 
    # Create a runnable with history
    with_message_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    # Configure session id
    config = {'configurable':{'session_id':'abc1'}}
    # Get the response
    response = with_message_history.invoke(
        {'input':message},
        config=config,
    )
    return response.content

# Build the Gradio app
demo = gr.ChatInterface(fn=get_response, title="Groq Llama3 by Utkarsh")

# Launch the gradio app
if __name__=='__main__':
    demo.launch()