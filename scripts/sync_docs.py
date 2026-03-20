#!/usr/bin/env python3
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Please install it via 'pip install PyYAML'.")
    sys.exit(1)

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workflows_path = os.path.join(repo_root, 'workflows.yaml')
    skill_path = os.path.join(repo_root, 'SKILL.md')

    if not os.path.exists(workflows_path):
        print(f"Error: {workflows_path} not found.")
        sys.exit(1)

    if not os.path.exists(skill_path):
        print(f"Error: {skill_path} not found.")
        sys.exit(1)

    with open(workflows_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    workflows = data.get('workflows', [])
    if not workflows:
        print("No workflows found in workflows.yaml.")
        return

    # 1. Generate keywords string for the YAML frontmatter
    # We combine names and snippets of descriptions for maximum LLM semantic matching
    keywords = ", ".join([wf.get('name', '') for wf in workflows])
    
    # We use double quotes inside the exact description to prevent YAML parsing errors in the frontmatter
    frontmatter_desc = f'Run Cloud AI Workflows via RunningHub using ComfyKit. CURRENT CAPABILITIES INCLUDE: {keywords}. AI AGENT MUST READ workflows.yaml TO MAP USER INTENT TO WORKFLOW ID.'
    
    # 2. Update SKILL.md
    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()

    # Update frontmatter description safely
    skill_content = re.sub(
        r'^description:\s*.*$',
        f'description: "{frontmatter_desc}"',
        skill_content,
        flags=re.MULTILINE
    )

    # 3. Generate Markdown capability list
    marker_start = "<!-- WORKFLOW_CAPABILITIES_START -->"
    marker_end = "<!-- WORKFLOW_CAPABILITIES_END -->"

    body_text = "\n### 🛠️ Automatically Synced Capabilities\n"
    body_text += "*(This section is automatically updated from `workflows.yaml` by `scripts/sync_docs.py`)*\n\n"
    for wf in workflows:
        body_text += f"- **{wf.get('name')}** (ID: `{wf.get('id')}`): {wf.get('description')}\n"

    # Inject or replace Markdown capability list
    if marker_start in skill_content and marker_end in skill_content:
        skill_content = re.sub(
            f"{marker_start}.*?{marker_end}",
            f"{marker_start}\n{body_text}\n{marker_end}",
            skill_content,
            flags=re.DOTALL
        )
    else:
        # If markers don't exist, insert them right after `# call_runninghub` header
        parts = skill_content.split("# call_runninghub\n")
        if len(parts) > 1:
            parts[1] = f"\n{marker_start}\n{body_text}\n{marker_end}\n" + parts[1]
            skill_content = "# call_runninghub\n".join(parts)
        else:
            print("Warning: Could not find '# call_runninghub' header in SKILL.md. Capabilities list appended to the bottom.")
            skill_content += f"\n\n{marker_start}\n{body_text}\n{marker_end}\n"

    with open(skill_path, 'w', encoding='utf-8') as f:
        f.write(skill_content)
        
    print("✅ Successfully synchronized SKILL.md with workflows.yaml.")

if __name__ == '__main__':
    main()
