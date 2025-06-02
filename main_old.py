import arxiv
import json
import os
from typing import List
from mcp.server.fastmcp import FastMCP
from datetime import datetime


PAPER_DIR = "papers"

tasks = [
    {
        "task": "Search papers",
        "due_date": "2025-06-10",
        "status": "pending"
    },
    {
        "task": "Extract paper information",
        "due_date": "2025-06-12",
        "status": "pending"
    },
    {
        "task": "List available topics",
        "due_date": "2025-06-08",
        "status": "completed"
    },
    {
        "task": "Get papers by topic",
        "due_date": "2025-06-15",
        "status": "pending"
    }
]

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def get_tasks() -> List[str]:
    """
    Return the list of predefined tasks available in the system.
    """
    return tasks


@mcp.tool()
def create_task(task: str, due_date: str, status: str = "pending") -> str:
    """
    Create a new task and add it to the tasks list.

    Args:
        task: Description of the task
        due_date: Due date in 'YYYY-MM-DD' format
        status: Status of the task (default: 'pending')

    Returns:
        Success message or error message if date format is wrong.
    """
    # Validate due_date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return "Error: due_date must be in YYYY-MM-DD format."

    new_task = {
        "task": task,
        "due_date": due_date,
        "status": status
    }

    tasks.append(new_task)
    return f"Task '{task}' added successfully with due date {due_date} and status '{status}'."


@mcp.tool()
def update_task(task: str, due_date: str = None, status: str = None) -> str:
    """
    Update an existing task's due date and/or status based on the task description.

    Args:
        task: Description of the task to update (must match exactly)
        due_date: New due date in 'YYYY-MM-DD' format (optional)
        status: New status (optional)

    Returns:
        Success or error message.
    """
    # Find the task in the list
    for t in tasks:
        if t["task"] == task:
            # Validate due_date if provided
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    return "Error: due_date must be in YYYY-MM-DD format."
                t["due_date"] = due_date
            
            if status:
                t["status"] = status
            
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


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv to find the papers 
    client = arxiv.Client()

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = topic,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
    
    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info  
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info
    
    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)
    
    print(f"Results are saved in: {file_path}")
    
    return paper_ids

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
 
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue
    
    return f"There's no saved information related to paper {paper_id}."

@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory.
    
    This resource provides a simple list of all available topic folders.
    """
    folders = []
    
    # Get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)
    
    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"
    
    return content

@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic.
    
    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")
    
    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."
    
    try:
        with open(papers_file, 'r') as f:
            papers_data = json.load(f)
        
        # Create markdown content with paper details
        content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total papers: {len(papers_data)}\n\n"
        
        for paper_id, paper_info in papers_data.items():
            content += f"## {paper_info['title']}\n"
            content += f"- **Paper ID**: {paper_id}\n"
            content += f"- **Authors**: {', '.join(paper_info['authors'])}\n"
            content += f"- **Published**: {paper_info['published']}\n"
            content += f"- **PDF URL**: [{paper_info['pdf_url']}]({paper_info['pdf_url']})\n\n"
            content += f"### Summary\n{paper_info['summary'][:500]}...\n\n"
            content += "---\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"# Error reading papers data for {topic}\n\nThe papers data file is corrupted."
    


@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool. Follow these instructions:
    1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
    2. For each paper found, extract and organize the following information:
       - Paper title
       - Authors
       - Publication date
       - Brief summary of the key findings
       - Main contributions or innovations
       - Methodologies used
       - Relevance to the topic '{topic}'
    
    3. Provide a comprehensive summary that includes:
       - Overview of the current state of research in '{topic}'
       - Common themes and trends across the papers
       - Key research gaps or areas for future investigation
       - Most impactful or influential papers in this area
    
    4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.
    
    Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
