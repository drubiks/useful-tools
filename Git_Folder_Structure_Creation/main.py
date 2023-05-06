import json
import os
from tkinter import filedialog, Tk, Entry, Label, Button, Frame, StringVar

import git
from git import Repo, Actor


def create_structure(base_path, structure):
    for key, value in structure.items():
        if isinstance(value, str):
            file_path = os.path.join(base_path, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Add this line
            with open(file_path, "w") as f:
                f.write("")
        else:
            path = os.path.join(base_path, key)
            os.makedirs(path, exist_ok=True)

            if isinstance(value, list):
                for file_name in value:
                    if file_name != "":
                        file_path = os.path.join(path, file_name)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Add this line
                        with open(file_path, "w") as f:
                            f.write("")
            elif isinstance(value, dict):
                create_structure(path, value)


def initialize_and_commit_repo(local_path, name, email):
    repo = Repo.init(local_path)
    author = Actor(name, email)
    repo.index.add("*")
    commit_message = "Initial commit with directory structure"
    repo.index.commit(commit_message, author=author)
    return repo


def create_and_update_branches(repo):
    for branch_name in ["dev", "stage", "production", "feature"]:  # Add "feature" to the list
        try:
            branch = repo.heads[branch_name]
            branch.set_commit(repo.head.commit)
        except IndexError:
            branch = repo.create_head(branch_name)


def delete_all_branches_except_dev(repo):
    for branch in repo.branches:
        if branch.name != "dev":
            repo.delete_head(branch, force=True)


def push_structure_to_dev(repo):
    try:
        repo.git.push("--set-upstream", "origin", "dev")
    except git.GitCommandError as e:
        print("Error pushing to the remote 'origin':", e)
        print("Please make sure the repository exists and you have the correct access rights.")


def add_remote_and_push_to_github(repo, github_repo_url):
    try:
        remote = repo.remotes.origin
        remote.set_url(github_repo_url)
    except AttributeError:
        remote = repo.create_remote("origin", github_repo_url)

    try:
        for branch in repo.branches:  # Loop through all branches
            remote.push(branch)  # Push each branch
    except git.GitCommandError as e:
        print("Error pushing to the remote 'origin':", e)
        print("Please make sure the repository exists and you have the correct access rights.")


def browse_files():
    file_path = filedialog.askopenfilename(
        title="Select a JSON file",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
    )
    return file_path


def load_structure_from_json_file(file_path):
    with open(file_path, "r") as f:
        structure = json.load(f)
    return structure


def on_apply_button_click():
    local_path = local_path_entry.get().strip()
    github_repo_url = github_repo_url_entry.get().strip()
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    json_file_path = json_file_path_var.get().strip()

    if not json_file_path:
        print("No JSON file selected. Exiting.")
        return

    structure = load_structure_from_json_file(json_file_path)
    create_structure(local_path, structure)
    repo = initialize_and_commit_repo(local_path, name, email)
    create_and_update_branches(repo)
    dev_branch = repo.heads["dev"]
    dev_branch.checkout()
    delete_all_branches_except_dev(repo)
    push_structure_to_dev(repo)
    add_remote_and_push_to_github(repo, github_repo_url)
    root.destroy()


def on_browse_button_click():
    json_file_path = browse_files()
    json_file_path_var.set(json_file_path)


def on_browse_repo_button_click():
    repo_path = filedialog.askdirectory()
    local_path_var.set(repo_path)


root = Tk()
root.title("Directory Structure Setup")

frame = Frame(root)
frame.pack(padx=10, pady=10)

local_path_label = Label(frame, text="Local repository path:")
local_path_label.grid(row=0, column=0, sticky="e")
local_path_var = StringVar()
local_path_entry = Entry(frame, textvariable=local_path_var)
local_path_entry.grid(row=0, column=1)

browse_repo_button = Button(frame, text="Browse", command=on_browse_repo_button_click)
browse_repo_button.grid(row=0, column=2, padx=(5, 0))

github_repo_url_label = Label(frame, text="GitHub repository URL:")
github_repo_url_label.grid(row=1, column=0, sticky="e")
github_repo_url_entry = Entry(frame)
github_repo_url_entry.grid(row=1, column=1)

name_label = Label(frame, text="Your name:")
name_label.grid(row=2, column=0, sticky="e")
name_entry = Entry(frame)
name_entry.grid(row=2, column=1)

email_label = Label(frame, text="Your email:")
email_label.grid(row=3, column=0, sticky="e")
email_entry = Entry(frame)
email_entry.grid(row=3, column=1)

json_file_path_label = Label(frame, text="JSON file path:")
json_file_path_label.grid(row=4, column=0, sticky="e")
json_file_path_var = StringVar()
json_file_path_entry = Entry(frame, textvariable=json_file_path_var)
json_file_path_entry.grid(row=4, column=1)

browse_button = Button(frame, text="Browse", command=on_browse_button_click)
browse_button.grid(row=4, column=2, padx=(5, 0))

apply_button = Button(frame, text="Apply", command=on_apply_button_click)
apply_button.grid(row=5, column=0, columnspan=3, pady=(10, 0))

root.mainloop()
