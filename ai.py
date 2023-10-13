import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts.chat import ChatPromptTemplate
from database import fetch_tasks_formatted

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)


def generate_schedule_from_hobby(hobby, number_of_sessions):
    ## TODO: Improve the templates in the future
    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    human_template = "I want to learn {hobby}, help me schedule {number_of_sessions} sessions for the week."
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    return chain.invoke(
        {"hobby": hobby, "number_of_sessions": number_of_sessions}
    ).content


def plan_tasks(telegram_user_id):
    ## TODO: fetch next day events from calendar
    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    tasks = fetch_tasks_formatted(telegram_user_id)
    human_template = "These are what I want to do tomorrow, with 1 as the most important:\n{tasks}\nHelp me create a schedule for me to complete them tomorrow. Give a reasonable estimate and you do not have to add all if there is no time. Return it in parsable JSON format containing id, task name and time slot and nothing else."
    # It returns in this format:
    # {
    #     "tasks": [
    #         {
    #         "id": 1,
    #         "task_name": "run",
    #         "time_slot": "6:00 AM - 7:00 AM"
    #         },
    #         {
    #         "id": 2,
    #         "task_name": "eat",
    #         "time_slot": "7:30 AM - 8:00 AM"
    #         },
    #         {
    #         "id": 3,
    #         "task_name": "gym",
    #         "time_slot": "8:30 AM - 9:30 AM"
    #         },
    #         {
    #         "id": 4,
    #         "task_name": "school",
    #         "time_slot": "10:00 AM - 4:00 PM"
    #         }
    #     ]
    # }
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            ("human", human_template),
        ]
    )
    chain = chat_prompt | chat_model
    ## TODO: mark task as added in database if it has been added to schedule
    return chain.invoke(
        {"tasks": tasks}
    ).content

