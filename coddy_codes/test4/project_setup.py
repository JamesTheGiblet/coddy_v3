import os

def create_project_structure(project_name):
    """Creates a basic project structure with folders and files.

    Args:
        project_name: The name of the project.
    """
    try:
        os.makedirs(project_name, exist_ok=True)
        os.makedirs(os.path.join(project_name, "data"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "src"), exist_ok=True)

        with open(os.path.join(project_name, "main.py"), "w") as f:
            f.write("""This is the main file.""")

        with open(os.path.join(project_name, "src", "riddle_manager.py"), "w") as f:
            f.write("""This file manages riddles.""")
        print(f"Project structure for '{project_name}' created successfully.")
    except OSError as e:
        print(f"Error creating project structure: {e}")

if __name__ == "__main__":
    project_name = input("Enter project name: ")
    create_project_structure(project_name)