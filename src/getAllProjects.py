import http.client
import json
import sys
import argparse
import os
from dotenv import load_dotenv
import logging
import tkinter as tk
from tkinter import ttk

# Check if .env file exists in same folder!
wdir = os.path.dirname(os.path.realpath(__file__))
envFile = wdir + "\\.env"
if os.path.isfile(envFile):
    load_dotenv()
    KB_SITE=os.getenv("KB_SITE")
    KB_TOKEN=os.getenv("KB_TOKEN")
else:
    print(f"ERROR: MISSING REQUIRED '{envFile}' file")
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


def getAllProjects(api):
    payload = json.dumps({"jsonrpc": "2.0", "method": "getAllProjects", "id": 1})

    api.conn.request("GET", "/jsonrpc.php", payload, api.headers)
    res = api.conn.getresponse()
    data = res.read()

    all_projects = json.loads(data)["result"]

    return all_projects


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
    parser.add_argument("-m", "--method", default="gp", help="API Method", type=str)
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

    if args.method:
        if args.method == "gp":
            _method = "gp"
        else:
            print("Invalid Method")
            sys.exit(0)

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
        print(f"  Method:{_method}")
        if _method == "gp":
            if _project_id > -1:
                selected_project = all_projects[_project_id]
            else:
                print("  Select a Project:")
                selected_project = selectAProject(all_projects)
                _project_id = selected_project["id"]
            print(f"  Project ID:{_project_id}")
            print(f"  Project Name:{selected_project['name']}")
