import json
import subprocess
import re
from datetime import datetime

def run_gh_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        return []
    return json.loads(result.stdout)

def get_activity():
    # Fetch merged PRs
    print("Fetching merged PRs...")
    # Use --merged flag instead of --state merged
    merged_prs = run_gh_command('gh search prs --author "@me" --merged --sort updated --limit 10 --json title,repository,url,updatedAt,state')
    
    # Fetch open PRs
    print("Fetching open PRs...")
    open_prs = run_gh_command('gh search prs --author "@me" --state open --sort updated --limit 5 --json title,repository,url,updatedAt,state')
    
    all_prs = merged_prs + open_prs
    # Sort by update time desc
    all_prs.sort(key=lambda x: x['updatedAt'], reverse=True)
    return all_prs

def format_activity(prs):
    lines = ["| Project | PR | Status | Date |", "|---|---|---|---|"]
    for pr in prs[:10]: # Limit to top 10
        repo_name = pr['repository']['nameWithOwner']
        title = pr['title']
        url = pr['url']
        state = "🟣 Merged" if pr['state'] == 'MERGED' else "🟢 Open"
        date = datetime.strptime(pr['updatedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        
        # Clean title of generic prefixes if desired, or keep as is
        lines.append(f"| [{repo_name}](https://github.com/{repo_name}) | [{title}]({url}) | {state} | {date} |")
    
    return "\n".join(lines)

def update_readme(content):
    readme_path = "README.md"
    try:
        with open(readme_path, "r") as f:
            current_content = f.read()
    except FileNotFoundError:
        print("README.md not found, creating basic one.")
        current_content = "# Context \n\n<!-- START_ACTIVITY -->\n<!-- END_ACTIVITY -->\n"

    start_marker = "<!-- START_ACTIVITY -->"
    end_marker = "<!-- END_ACTIVITY -->"
    
    if start_marker not in current_content or end_marker not in current_content:
        print("Markers not found in README.md. Appending them.")
        current_content += f"\n## Recent Contributions\n{start_marker}\n{end_marker}\n"
    
    pattern = re.compile(f"{re.escape(start_marker)}.*{re.escape(end_marker)}", re.DOTALL)
    new_block = f"{start_marker}\n{content}\n{end_marker}"
    
    new_content = pattern.sub(new_block, current_content)
    
    with open(readme_path, "w") as f:
        f.write(new_content)
    print("README.md updated successfully.")

def main():
    prs = get_activity()
    if not prs:
        print("No activity found or error occurred.")
        return
        
    markdown_table = format_activity(prs)
    update_readme(markdown_table)

if __name__ == "__main__":
    main()
