---
name: call_runninghub
description: Run Cloud AI Workflows via RunningHub using ComfyKit
---

# call_runninghub

This skill enables an AI Agent to directly trigger RunningHub cloud workflows (such as Image generation, Video generation, TTS, etc.) by passing simple frontend-style parameters. The underlying `comfykit` library dynamically handles parameter mapping (variable names -> nodeId/fieldName definitions) and handles local file uploads automatically.

## 🔐 Security & API Key Protection
To prevent critical API keys from leaking into shell history logs, terminal outputs, or LLM context windows, **command-line passing of the API key is strictly disabled**.

### How to set the API Key:
1. **Environment Variable (Recommended):**
   ```bash
   export RUNNINGHUB_API_KEY="your_api_key_here"
   ```
2. **.env file:**
   Create a `.env` file in the directory where you run the script:
   ```env
   RUNNINGHUB_API_KEY=your_api_key_here
   ```
*(Note: Never commit your `.env` file to version control. It is ignored in the provided `.gitignore`)*

## Prerequisites
- Python 3.8+
- Installed dependencies: `pip install -r requirements.txt`
- **Workflow ID or File**: A RunningHub numeric ID (e.g. `"1983427617984585729"`) or the relative path to an exported JSON wrapper.

## Usage

Use the provided wrapper script to execute RunningHub workflows. When parameters include local file paths (like images), the underlying logic will automatically upload them to RunningHub and inject the returned URLs/keys before execution.

```bash
python scripts/run_workflow.py \
  --workflow "<workflow_id_or_json_path>" \
  --params-json '{"prompt": "A futuristic city in the rain, cyberpunk style", "width": 1024, "height": 768}'
```

### Example: Generate an Image by Workflow ID
```bash
# Provide API key securely
export RUNNINGHUB_API_KEY="sk-..."

python scripts/run_workflow.py \
  --workflow "1983427617984585729" \
  --params-json '{"prompt": "A cute cat wearing a spacesuit", "width": 1024, "height": 1024}'
```

## Internal Mechanism
1. The script initializes `comfykit.ComfyKit` utilizing the API key from the environment.
2. It fetches the ComfyUI workflow definition using the RunningHub REST API.
3. ComfyKit's `WorkflowParser` matches the passed JSON parameter keys to predefined ComfyUI variables (e.g., node titles ending in `~prompt`). 
4. Local valid file paths are intercepted and uploaded via `POST /task/openapi/upload`.
5. The task is executed via `POST /task/openapi/create` and natively monitored for completion.
