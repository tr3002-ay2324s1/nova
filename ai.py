import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts.chat import ChatPromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

def generate_schedule(hobby, number_of_sessions):
    ## TODO: Improve the templates in the future
    template = "You are a helpful personal secretary that helps to schedule daily tasks."
    human_template = "I want to learn {hobby}, help me schedule {number_of_sessions} sessions for the week."
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])
    chain = chat_prompt | chat_model
    return chain.invoke({"hobby": hobby, "number_of_sessions" : number_of_sessions}).content