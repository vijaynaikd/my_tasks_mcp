from typing import List
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from google_sheets_client import sheet

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def get_tasks() -> List[dict]:
    """
    Retrieve all tasks from the Google Sheet.
    """
    records = sheet.get_all_records()
    return records


@mcp.tool()
def create_task(task: str, due_date: str, status: str = "pending") -> str:
    """
    Add a new task to the Google Sheet.
    """
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return "Error: due_date must be in YYYY-MM-DD format."

    sheet.append_row([task, due_date, status])
    return f"Task '{task}' added successfully with due date {due_date} and status '{status}'."


@mcp.tool()
def update_task(task: str, due_date: str = None, status: str = None) -> str:
    """
    Update an existing task's due date and/or status in the Google Sheet.
    """
    records = sheet.get_all_records()
    for idx, record in enumerate(records, start=2):  # start=2 accounts for header row
        if record['task'] == task:
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    return "Error: due_date must be in YYYY-MM-DD format."
                sheet.update_cell(idx, 2, due_date)  # Column 2: due_date
            if status:
                sheet.update_cell(idx, 3, status)  # Column 3: status
            return f"Task '{task}' updated successfully."
    return f"Task '{task}' not found."


@mcp.prompt()
def create_task_prompt(task: str, due_date: str) -> str:
    """
    A prompt to:
    1. Add a user-defined task with a due date.
    2. Show all tasks in a table format.
    3. Provide a summary by status.
    
    Args:
        task: The description of the task to add.
        due_date: The due date of the task (in YYYY-MM-DD format).
    """
    return f"""
        1. Add a new task using:  
        create_task(task="{task}", due_date="{due_date}", status="pending")

        2. Retrieve the list of all tasks using:  
        get_tasks()

        3. Display the list of tasks as a table with columns:  
        **Task**, **Due Date**, **Status**

        4. Show a summary of the number of tasks grouped by status (e.g., pending, completed).
        """    


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

    # print(create_task("Search papers", "2025-06-05"))
    # print(update_task("Write abstract", "2025-06-05", "completed"))
    # for task in get_tasks():
    #     print(task)
