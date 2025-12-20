import json
import re
import sys
from urllib.request import urlopen, Request
from datetime import datetime

USERNAME = "kelvinvelasquez-SDE"
URL = f"https://api.github.com/users/{USERNAME}/events"

def fetch_events():
    try:
        req = Request(URL, headers={"User-Agent": "Python/ProfileUpdater"})
        with urlopen(req) as response:
            data = json.load(response)
        return data
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def format_event(event):
    type = event.get("type")
    repo = event.get("repo", {}).get("name")
    payload = event.get("payload", {})
    created_at = event.get("created_at")
    
    # Format date
    date_obj = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    date_str = date_obj.strftime("%d %b")

    if type == "PullRequestEvent":
        action = payload.get("action")
        if action == "opened":
            url = payload.get("pull_request", {}).get("html_url")
            title = payload.get("pull_request", {}).get("title")
            return f"- 🚀 **PR Opened** in [{repo}]({url}): {title} ({date_str})"
        elif action == "closed" and payload.get("pull_request", {}).get("merged"):
            url = payload.get("pull_request", {}).get("html_url")
            title = payload.get("pull_request", {}).get("title")
            return f"- 🎉 **PR Merged** in [{repo}]({url}): {title} ({date_str})"
            
    elif type == "IssuesEvent" and payload.get("action") == "opened":
        url = payload.get("issue", {}).get("html_url")
        title = payload.get("issue", {}).get("title")
        return f"- 🐛 **Issue Opened** in [{repo}]({url}): {title} ({date_str})"
        
    elif type == "PushEvent":
        # Group pushes? for now just ignore or distinct?
        # Pushes are noisy. Let's skip them unless they are to main/master of interesting repos?
        pass

    return None

def update_readme(lines):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!--START_SECTION:activity-->"
    end_marker = "<!--END_SECTION:activity-->"
    
    activity_content = "\n" + "\n".join(lines) + "\n"
    
    pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    replacement = f"{start_marker}{activity_content}{end_marker}"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    events = fetch_events()
    activity_lines = []
    
    # Process mostly recent events, limit to 5-10
    count = 0
    for event in events:
        line = format_event(event)
        if line:
            activity_lines.append(line)
            count += 1
            if count >= 7:
                break
    
    if activity_lines:
        print(f"Found {len(activity_lines)} activities. Updating README...")
        update_readme(activity_lines)
    else:
        print("No significant activity found.")

if __name__ == "__main__":
    main()
