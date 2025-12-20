import json
import re
import sys
from urllib.request import urlopen, Request
from datetime import datetime

USERNAME = "kelvinvelasquez-SDE"
URL = f"https://api.github.com/users/{USERNAME}/events"

def fetch_json(url):
    try:
        req = Request(url, headers={"User-Agent": "Python/ProfileUpdater"})
        with urlopen(req) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_pr_details(api_url):
    data = fetch_json(api_url)
    if data:
        return data.get("title"), data.get("html_url")
    return None, None

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
        pr_api_url = payload.get("pull_request", {}).get("url")
        
        # If title/html_url missing, fetch them
        title = payload.get("pull_request", {}).get("title")
        html_url = payload.get("pull_request", {}).get("html_url")
        
        if not title or not html_url:
             print(f"Fetching details for PR in {repo}...")
             title, html_url = get_pr_details(pr_api_url)

        if action == "opened":
            return f"- 🚀 **PR Opened** in [{repo}]({html_url}): {title} ({date_str})"
        elif action == "closed" or action == "merged":
            # Check if merged if action is closed, or if action is explicitly merged
            is_merged = payload.get("pull_request", {}).get("merged") or action == "merged"
            if is_merged:
                 return f"- 🎉 **PR Merged** in [{repo}]({html_url}): {title} ({date_str})"
            
    elif type == "IssuesEvent" and payload.get("action") == "opened":
        issue_url = payload.get("issue", {}).get("html_url")
        title = payload.get("issue", {}).get("title")
        return f"- 🐛 **Issue Opened** in [{repo}]({issue_url}): {title} ({date_str})"

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
    events = fetch_json(URL)
    if not events:
        return

    activity_lines = []
    
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
