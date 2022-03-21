from dotenv import dotenv_values
import requests
from habitipy import Habitipy, load_conf, DEFAULT_CONF
from datetime import datetime
from pprint import pprint

AM_BASE_URL = "https://serv.amazingmarvin.com/api/"
config = dotenv_values(".env")

assert requests.post(AM_BASE_URL + "test",
                     headers={
                         "X-API-Token": config["AM_API_TOKEN"]
                     }).status_code == 200, "Invalid AM API Token"
habitica_api = Habitipy(load_conf(DEFAULT_CONF))

# remove incompleted todos on Habitica
print("Removing incompleted todos from Habitica...")
incompleted_tasks = habitica_api.tasks.user.get(type="todos")
if incompleted_tasks:
    for incompleted_task in incompleted_tasks:
        try:
            assert requests.delete(
                url=
                f"https://habitica.com/api/v3/tasks/{incompleted_task['id']}",
                headers={
                    "x-api-user": config["USER_ID"],
                    "x-api-key": config["API_TOKEN"]
                }).status_code == 200
        except AssertionError:
            print(f"Problem in removing task named {incompleted_task['text']}")
print("Done!")

# add today's tasks from Amazing Marvin as Habitica todos
print("Fetching today's tasks from Amazing Marvin...")
todays_tasks = requests.get(AM_BASE_URL + "todayItems",
                            headers={
                                "X-API-Token": config["AM_API_TOKEN"],
                                "X-Date": datetime.now().isoformat()
                            }).json()
print("Done!")
print("Adding the tasks to Habitica...")
for task in todays_tasks:
    subtasks = [{
        'text': subtask_dict["title"],
        'completed': subtask_dict["done"]
    } for subtask_id, subtask_dict in task["subtasks"].items()
               ] if "subtasks" in task else []

    habitica_api.tasks.user.post(text=task["title"],
                                 type="todo",
                                 checklist=subtasks,
                                 date=task["day"])
print("Done! View on https://habitica.com")
