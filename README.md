This is a simple MCP server to demonstrate task management
This uses a google sheet as database

1. Clone this project

2. Go to your project folder

3. Create virtual envrionment
```
python3 -m venv venv
```

4. Acticate virtual environment for mac
```
source venv/bin/activate 
```

for windows
```
venv\Scripts\activate
```

5. Setup service account in your google account
Activate google drive and google sheets apis

Download add googleserviceaccount.json to root folder

6. Create a google sheet by name "MyTasks" and share it with service account

7. Intall dependencies

```
uv add google-auth google-auth-oauthlib gspread mcp oauth2client
```

8. Add the MCP configuration to Claude Desktop
```
{
    "mcpServers": {
        "my_tasks": {
            "command": "uv",
            "args": [
                "--directory",
                "/path to your project/mcp_server/",
                "run",
                "main.py"
            ]
        }
    }
}
```