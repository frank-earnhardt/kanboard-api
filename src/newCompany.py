import http.client
import json
import sys
import argparse
import os
from dotenv import load_dotenv
import logging
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
import datetime
import numpy as np

dttm = datetime.datetime.now().replace(microsecond=0).isoformat()

# Check if .env file exists in same folder!
if os.path.isfile(".env"):
    load_dotenv()
    KB_SITE=os.getenv("KB_SITE")
    KB_TOKEN=os.getenv("KB_TOKEN")
else:
    print("ERROR: MISSING REQUIRED '.env' file")
    print("The .env file is missing, please add it to the same folder as this script")
    sys.exit(1)

# Check of KB_SITE and KB_TOKEN veraibles have values
if KB_SITE == "" or KB_SITE == None or KB_TOKEN == "" or KB_TOKEN == None:
    print("************************************************************")
    print("ERROR: MISSING REQUIRED ENVIRONMENT VARIABLES FROM .env FILE")
    print("************************************************************")
    print("  Please add the following variables to the.env file")
    print("  -- KB_SITE=https://<kanboard-site>")
    print("  -- KB_TOKEN=<kanboard-token>")
    sys.exit(1)

_debug = 0
_method = ""
_project_id = -1


class APIConnector:
    def __init__(self):
        self.conn = http.client.HTTPSConnection(KB_SITE)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + KB_TOKEN,
        }

    def callback(self):
        self.entry.delete(0, tk.END)

def GET_RPC(payload):
    if _debug >0:
      print(f" DEBUG: GET_RPC(PAYLOAD): {payload}")

    # Create an instance of the APIConnector class
    api = APIConnector()
    api.conn.request("GET", "/jsonrpc.php", payload, api.headers)
    res = api.conn.getresponse()
    data = res.read()
    rpc_results = json.loads(data)["result"]
    if _debug >0:
      print(rpc_results)
    return rpc_results

def getAllProjects(api):
    payload = json.dumps({"jsonrpc": "2.0", "method": "getAllProjects", "id": 1})

    api.conn.request("GET", "/jsonrpc.php", payload, api.headers)
    res = api.conn.getresponse()
    data = res.read()

    all_projects = json.loads(data)["result"]

    return all_projects

def createCategory(project_id, name):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "createCategory",
            "id": 1,
            "params": {"project_id": project_id, "name": name},
        }
    )

    category = GET_RPC(payload)
    return category

def getCategory(project_id, category_id):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "getCategory",
            "id": 1,
            "params": {"project_id": project_id, "category_id": category_id},
        }
    )

    category = GET_RPC(payload)
    return category

def getAllCategories(project_id):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "getAllCategories",
            "id": 1,
            "params": {"project_id": project_id},
        }
    )

    all_categories = GET_RPC(payload)
    return all_categories 

def getCategoryByName(project_id, category_name):
    #TODO: API Does not support this method:
    # payload = json.dumps(
    #     {
    #         "jsonrpc": "2.0",
    #         "method": "getCategoryByName",
    #         "id": 1,
    #         "params": {"project_id": project_id, "category_name": category_name},
    #     }
    # )

    # category = GET_RPC(payload)
    # return category

    # Work Around
    all_categories = getAllCategories(project_id)
    for category in all_categories:
        if _debug > 0:
          print("Category Name: " + category['name'])
        if category['name'] == category_name:
            #print("Category ID: " + str(category['id']))
            return category

    return None

# Define a data class with the attributes and default values
@dataclass
class ExtLinkType:
    Auto: str = "auto"
    Attachment: str = "attachment"
    File: str = "file"
    Web: str = "weblink"

@dataclass
class Task:
    id: int = 0
    title: str = ""
    project_id: int = 0
    color_id: str = "green"
    column_id: int = 1
    owner_id: int = 1
    creator_id: int = 1
    due_date: str = None
    description: str = ""
    category_id: int = 0
    score: int = 0
    swimlane_id: int = 1
    priority: int = 0
    recurrence_status: int = 0
    recurrence_trigger: int = 0
    recurrence_factor: int = 0
    recurrence_timeframe: int = 0
    recurrence_basedate: str = None
    reference: str = ""
    tags: np.ndarray = None
    date_started: str = str(dttm)

    # Initialize the tags attribute as en empty list of not provided
    def __post_init__(self):
        if self.tags is None:
            self.tags = np.empty(0, dtype=str)

# Task API
def createTask(Task):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "createTask",
            "id": 1,
            "params": {
                "title": Task.title,                                             # (string, required)
                "project_id": Task.project_id,                                   # (integer, required)
                #"color_id": Task.color_id,                                       # (string, optional)
                "column_id": Task.column_id,                                     # (integer, optional)
                "owner_id": Task.owner_id,                                       # (integer, optional)
                "creator_id": Task.creator_id,                                   # (integer, optional)
                #"due_date": Task.due_date,                                       # ISO8601 format (string, optional)
                "description": Task.description,                                 # Markdown content (string, optional)
                "category_id": Task.category_id,                                 # (integer, optional)
                #"score": Task.score,                                             # (integer, optional)
                "swimlane_id": Task.swimlane_id,                                 # (integer, optional)
                #"priority": Task.priority,                                       # (integer, optional)
                #"recurrence_status": Task.recurrence_status,                     # (integer, optional)
                #"recurrence_trigger": Task.recurrence_trigger,                   # (integer, optional)
                #"recurrence_factor": Task.recurrence_factor,                     # (integer, optional)
                #"recurrence_timeframe": Task.recurrence_timeframe,               # (integer, optional)
                #"recurrence_basedate": Task.recurrence_basedate,                 # (integer, optional)
                "reference": Task.reference,                                     # (string, optional)
                "tags": Task.tags,                                               # ([]string, optional)
                #"date_started": Task.date_started,                               # ISO8601 format (string, optional)
            },
        }
    )
    print(payload)
    task = GET_RPC(payload)
    return task

def getAllTasks(project_id=1, status_id=1): # Get all available tasks
    #status 1 for Active Tasks, 0 for Inactive
    print("Get All Tasks")
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "getAllTasks",
            "id": 1,
            "params": {"project_id": project_id,"status_id":status_id},
        }
    )

    all_tasks = GET_RPC(payload)
    return all_tasks

def getTaskByName(project_id, task_name):
    #TODO: API Does not support this method:
    # payload = json.dumps(
    #     {
    #         "jsonrpc": "2.0",
    #         "method": "getTaskByName",
    #         "id": 1,
    #         "params": {"project_id": project_id, "task_name": task_name},
    #     }
    # ) 

    # task = GET_RPC(payload)
    # return task 
    
    # Work Around
    task_list = []
    all_tasks = getAllTasks(project_id)
    for task in all_tasks:
        if _debug > 0:
          print(f"Task Name: ",task['title']," ID: ",task['id'])
        if task['title'] == task_name:
            print("Task ID: " + str(task['id']), "  Task Name: " + task['title'])
            task_list.append(task)
        #    return task
    for task in task_list:
        print("Task ID: " + str(task['id']), "  Task Name: " + task['title'])
    
    return task_list

def remoteTask(task_id): # Remove a task
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "removeTask",
            "id": 1,
            "params": {"task_id": task_id},
        }
    )

    task = GET_RPC(payload)
    return task

def createExternalTaskLink(project_id, task_id, url, dependency, type, title):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "createExternalTaskLink",
            "id": 1,
            "params": {
                "project_id": project_id,           # (integer, required)
                "task_id": task_id,                 # (integer, required)
                "url": url,                         # (string, required)
                "dependency": dependency,           # (string, required)
                "link_type": type,                       # (string, optional)
                #"title": title,                     # (string, optional)
            },
        }
    )

    extTaskLink = GET_RPC(payload)
    return extTaskLink

def updateExternalTaskLink(project_id, task_id, link_id, title):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "updateExternalTaskLink",
            "id": 1,
            "params": {
                "project_id": project_id,
                "task_id": task_id,
                "link_id": link_id,
                "title": title,
                #"url": url,
                #"dependency": dependency,
            },
        }
    )

    upExtTaskLink = GET_RPC(payload)
    return upExtTaskLink


def promptForInput(prompt_text):
    input_loop = True
    while input_loop:
        user_input = input(prompt_text)
        if user_input == "x":
            print(f"  User Entered:{user_input}\n", "...Exiting...")
            input_loop = False
            sys.exit()
        else:
            return user_input

def selectAProject(all_projects):
    loop = True
    while loop:
        for i, project in enumerate(all_projects):
            print("  " + str(i) + ". " + project["name"])

        print("\n")
        print(f"  Select a Project:")
        user_input = input("  Enter number (x to exit): ")

        if user_input == "x":
            print(f"  User Entered:{user_input}\n", "...Exiting...")
            loop = False

        else:
            try:
                num = int(user_input)

                # selected_project = all_projects[num]['name']
                selected_project = all_projects[num]  # Return full object

                if _debug > 5:
                    print(
                        f"  user_input:{user_input}\n",
                        "*******************\n",
                        f"{selected_project}\n",
                        "*******************\n",
                    )

                return selected_project
            except ValueError:
                print(f"  Invalid Entry:{user_input}, try again.")

    sys.exit(0)


def function():
    """
    This is the main function.

    Usage:
      python3 getAllProjects.py -d 1 -p 100 -n "Test Project"

    Arguments:
      -d, --debug: Enable debug output
      -p, --project: Project ID
      -n, --name: Project Name
      -h, --help: Show this help message and exit
      -v, --version: Show version and exit
    """
    pass


# Treeview sort column variable
default_sort_column = "one"


def sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children("")]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, "", index)

    # set sort column binding
    tv.heading(col, command=lambda: sort_column(tv, col, not reverse))


def callback(event):
    selection = combobox.get()


#  entry.delete(0, tk.END)
#  entry.insert(0, selection)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kan Board API Client")
    parser.add_argument("-d", "--debug", default=0, help="Enable debug output", type=int)
    parser.add_argument("-m", "--method", default="", help="API Method", type=str)
    parser.add_argument("-p", "--project_id", help="Project ID", type=int)
    parser.add_argument("-n", "--name", help="Project Name", type=str)
    # parser.add_argument('-h', '--help', help='Show this help message and exit', action='store_true')
    parser.add_argument(
        "-v", "--version", help="Show version and exit", action="store_true"
    )
    parser.add_argument("-g", "--gui", help="Run GUI", action="store_true")
    args = parser.parse_args()

    if args.debug:
        if args.debug > 0:
            _debug = args.debug
            print("  Debug enabled:{_debug}".format(**locals()))

    if args.version:
        print("0.0.1")
        sys.exit(0)

    if args.method == "":
        print(args.method)
        _method = "gp"
    else:
        _method = args.method
        print("Method:", _method)


    if args.project_id != None:
        if args.project_id == 0:
            if _debug > 0:
                print(type(args.project_id), args.project_id)
            _project_id = int(args.project_id)
            print("Project ID:", _project_id)
        else:
            if _debug > 0:
                print(type(args.project_id), args.project_id)
            if int(args.project_id) > 0:
                _project_id = int(args.project_id)
                print("Project ID:", _project_id)

    if args.name:
        print("Project Name:", args.name)

    # print(type(args.project_id), args.project_id)
    api = APIConnector()
    all_projects = getAllProjects(api)

    if args.gui:
        root = tk.Tk()
        root.title("Kan Board API Client")
        root.geometry("800x600")
        tree = ttk.Treeview(root)
        tree["columns"] = ("one", "two")
        tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
        tree.column("one", width=150, minwidth=150, stretch=tk.NO)
        tree.column("two", width=400, minwidth=200)

        tree.heading("#0", text="Project ID", anchor=tk.W)
        tree.heading("one", text="Name", anchor=tk.W)

        for project in all_projects:
            tree.insert("", tk.END, text=project["id"], values=(project["name"]))

        tree.pack(pady=20)

        # Set sort to Project ID on startup
        sort_column(tree, default_sort_column, False)
        # Bind left click to sort
        tree.bind(
            "<Button-1>",
            lambda evt: sort_column(tree, tree.identify_column(evt.x), False),
        )

        project_var = tk.StringVar(root)
        project_var.set(all_projects[0]["name"])

        option_menu = tk.OptionMenu(root, project_var, *all_projects)
        option_menu.pack()

        button = tk.Button(
            root, text="Select A Project", command=lambda: selectAProject(all_projects)
        )
        button.pack()

        combobox = ttk.Combobox(root, values=all_projects)
        combobox.pack(pady=10)
        combobox.bind("<<ComboboxSelected>>", callback)

        project_cb = ttk.Combobox(root, values=[p["name"] for p in all_projects])
        project_cb.pack()

        # Table
        table = ttk.Treeview(root)

        table["columns"] = ("id", "name")
        table.column("#0", width=0, stretch=tk.NO)
        table.column("id", anchor="center", width=80)
        table.column("name", anchor="center", width=80)

        table.heading("id", text="ID", anchor="center")
        table.heading("name", text="Task", anchor="center")

        table.pack()

        project_label = ttk.Label(root, text="Project:")
        project_label.pack()

        def on_project_change(event):
            selected_project = project_cb.get()
            project_label.config(text="Project: " + selected_project)
            for project in all_projects:
                if project["name"] == selected_project:
                    table.delete(*table.get_children())
                    # for task in project['tasks']:
                    #    table.insert('', 'end', values=(task['id'], task['name']))
                    break

        project_cb.bind("<<ComboboxSelected>>", on_project_change)
        root.mainloop()
    else:
        print(f"  RUN Method:{_method}")
        if _method == "test":
            #extTaskLink = createExternalTaskLink(1,303,"https://zillow.com/careers","related","weblink","careers")
            #print(extTaskLink)
            #test = updateExternalTaskLink(1,305,336,"Career Site")
            test = getTaskByName(1,"Zillow")
            for task in test:
                #print(task)
                print(f"  Task ID:{task['id']}")
                rm_tsk = remoteTask(task['id'])
        if _method == "gp":
            if _project_id > -1:
                selected_project = all_projects[_project_id]
            else:
                print("  Select a Project:")
                selected_project = selectAProject(all_projects)
                _project_id = selected_project["id"]
            print(f"  Project ID:{_project_id}")
            print(f"  Project Name:{selected_project['name']}")
            input_company = promptForInput("  Enter Company Name (x to exit): ")
            print(f"  Company Name:{input_company}")
            input_url = promptForInput("  Enter Company URL (x to exit): ")
            print(f"  Company URL:{input_url}")
            new_category = createCategory(_project_id, input_company)
            if new_category == False:
                print(f"Category already exists:",input_company)
                new_category = getCategoryByName(_project_id, input_company)
            
            print(f"  Category ID:",str(new_category['id']))
            print(f"  Category Name:",new_category['name'])
            tsk = Task(title=input_company,project_id=_project_id,description=input_company,category_id=new_category["id"],tags=["Company"])
            print(tsk)

            new_task = createTask(tsk)
            print(type(new_task),new_task)
            #print(f"  Task ID:",str(new_task['id']))
            # project_id, task_id, url, dependency, type, title
            print(f"  Task ID:{new_task}")
            #new_url = input_url.replace('/','\/')
            #print(new_url)
            extTaskLink = createExternalTaskLink(_project_id,new_task,input_url,"related",ExtLinkType.Web,"Career Site")
            print(extTaskLink)

            fixExtTaskLinkTitl= updateExternalTaskLink(_project_id,new_task,extTaskLink,input_company + " Career Site")
            print(fixExtTaskLinkTitl)