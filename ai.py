import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts.chat import ChatPromptTemplate
from database import fetch_tasks_formatted, fetch_user, mark_task_as_added
from google_cal import add_calendar_event, get_calendar_events
from datetime import datetime, timedelta, date
from json import dumps, loads

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)


# Define a function to convert the time string to a datetime object
def time_slot_to_datetime(time_slot):
    # Create a datetime object for tomorrow's date
    tomorrow = date.today() + timedelta(days=1)

    # Extract the start time and end time from the time_slot string
    start_time_str, end_time_str = time_slot.split(" - ")

    # Convert the start time and end time strings to datetime.time objects
    start_time = datetime.strptime(start_time_str, "%I:%M%p").time()
    end_time = datetime.strptime(end_time_str, "%I:%M%p").time()

    # Combine the date object and the time objects to create datetime.datetime objects
    start_datetime = datetime.combine(tomorrow, start_time)
    end_datetime = datetime.combine(tomorrow, end_time)

    return start_datetime, end_datetime


def generate_schedule_from_hobby(hobby, number_of_sessions):
    # TODO: Improve the templates in the future
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
    users = fetch_user(telegram_user_id=telegram_user_id)
    first_user = users[0]
    refresh_token = first_user.get("google_refresh_token", "")
    # Get events from tomorrow 12am to tomorrow 11:59pm
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0)
    events = get_calendar_events(
        refresh_token=refresh_token,
        timeMin=tomorrow_midnight.isoformat() + "Z",
        timeMax=(tomorrow_midnight + timedelta(days=1)).isoformat() + "Z",
        k=20,
    )

    formatted_events = [
        {
            "start_time": datetime.fromisoformat(event["start"]["dateTime"]).strftime(
                "%I:%M%p"
            ),
            "end_time": datetime.fromisoformat(
                event.get("end")["dateTime"]
                if not event.get("endTimeUnspecified", False)
                else datetime.utcnow().isoformat()
            ).strftime("%I:%M%p"),
            "description": event.get("summary", ""),
            "id": event["id"],
        }
        for event in events
    ]

    formatted_events_str = dumps(formatted_events)
    print("formatted_events_str", formatted_events_str)

    template = (
        "You are a helpful personal secretary that helps to schedule daily tasks."
    )
    tasks = fetch_tasks_formatted(telegram_user_id)
    print(tasks)
    if not tasks:
        return None
    human_template = "This is my schedule for tomorrow (which cannot be changed): \n{formatted_events_str}\nThese are extra tasks I want to do tomorrow, with the lowest id as the most important:\n{tasks}\nHelp me add to my schedule with as many of these tasks as possible. Give a reasonable estimate and you do not have to add all if there is no time. Do NOT create new tasks. Do not return the events or tasks in my existing schedule. Return it in parsable JSON format that can be immediately parsed. The return value should contain id, task name and time slot and nothing else, no other sentences ONLY."
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
    res = chain.invoke(
        {"formatted_events_str": formatted_events_str, "tasks": tasks}
    ).content
    print("AI RESPONSE", res)
    resParsed: dict = loads(res)
    print("AI RESPONSE PARSED", resParsed)
    tasks = (
        resParsed["tasks"]
        if "tasks" in resParsed
        else (
            resParsed["events"]
            if "events" in resParsed
            else resParsed[[k for k in resParsed][0]]  # Take the first key
        )
    )

    if tasks:
        # add to calendar
        for task in tasks:
            task_desc = task.get('task', task.get('description', task.get('task_name', '')))
            print(f"Adding {task_desc} to calendar")
            # Split the time_slot into start and end times
            time_slot = task["time_slot"]
            start_time, end_time = time_slot_to_datetime(time_slot=time_slot)
            add_calendar_event(
                refresh_token=refresh_token,
                start_time=start_time,
                end_time=end_time,
                summary=task_desc,
            )
        # for loop to mark tasks as added
        for task in tasks:
            mark_task_as_added(task["id"])
            print(f"Marked added {task['id']}")


print(plan_tasks(873852340))
