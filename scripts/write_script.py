#!/usr/bin/env python3
import os
import sys
import json
import argparse
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
    from duckduckgo_search import DDGS
except ImportError:
    print("Error: Missing dependencies for write_script.py. Please run: pip install openai duckduckgo-search", file=sys.stderr)
    sys.exit(1)

def get_web_context(topic, max_results=3):
    print(f"🔍 Searching the web for: {topic}...")
    try:
        results = DDGS().text(topic, max_results=max_results)
        context = []
        for r in results:
            context.append(f"- [{r.get('title')}] {r.get('body')}")
        print("✅ Search completed.")
        return "\n".join(context)
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        return "No recent web context available."

def load_knowledge_base(kb_path):
    if not kb_path or not os.path.exists(kb_path):
        return ""
        
    kb_content = []
    print(f"📚 Loading Knowledge Base templates from {kb_path}...")
    if os.path.isfile(kb_path):
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb_content.append(f.read())
    else:
        for f in os.listdir(kb_path):
            if f.endswith('.txt') or f.endswith('.md'):
                with open(os.path.join(kb_path, f), 'r', encoding='utf-8') as file:
                    kb_content.append(f"--- KNOWLEDGE: {f} ---\n{file.read()}")
    return "\n\n".join(kb_content)

def main():
    parser = argparse.ArgumentParser(description="Knowledge-Augmented Script Writer")
    parser.add_argument("--topic", required=True, help="Topic constraint to search and generate.")
    parser.add_argument("--kb-path", required=False, help="Path to your custom knowledge/style .md files")
    parser.add_argument("--output", required=False, default="script.json", help="Output filename")
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1"
    model = os.environ.get("LLM_MODEL") or "gpt-4o-mini"
    
    if not api_key:
        print("❌ Error: You must set LLM_API_KEY (and optionally LLM_BASE_URL, LLM_MODEL) in your .env", file=sys.stderr)
        sys.exit(1)

    web_facts = get_web_context(args.topic)
    kb_rules = load_knowledge_base(args.kb_path)

    system_prompt = f"""You are a professional self-media storyboard writer and script director.
You MUST output strictly in VALID JSON format. Do NOT wrap your output in markdown ```json blocks. Print ONLY the raw json string.

### YOUR RULES AND STYLE KNOWLEDGE BASE:
{kb_rules if kb_rules else "Write an engaging, fast-paced script for short-form video content."}

### BACKGROUND RESEARCH FACTS FOR CONTEXT:
Here is the latest data searched from the web on this topic:
{web_facts}
"""

    user_prompt = f"Topic to write about: {args.topic}\n\nPlease generate the JSON storyboard heavily adhering to my style knowledge and utilizing the recent web facts."

    print(f"🤖 Generating Script via {model} at {base_url}...")
    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" } if "gpt-" in model.lower() else None, 
            temperature=0.7
        )
        
        result_json = response.choices[0].message.content.strip()
        # Clean up Markdown wrapper if present
        if result_json.startswith("```json"):
            result_json = result_json[7:-3].strip()
        elif result_json.startswith("```"):
            result_json = result_json[3:-3].strip()

        # Enforce validation
        json.loads(result_json)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result_json)
            
        print(f"\n🎉 SUCCESS! Storyboard script generated and saved to: {args.output}")
        print("Preview:")
        print(result_json)

    except Exception as e:
         print(f"❌ Failed to generate script: {e}", file=sys.stderr)
         sys.exit(1)

if __name__ == "__main__":
    main()
