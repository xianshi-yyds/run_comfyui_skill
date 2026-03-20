---
name: call_runninghub
description: Run Cloud AI Workflows via RunningHub using ComfyKit
---

# call_runninghub

This skill enables an AI Agent to dynamically query, inspect, and trigger RunningHub cloud workflows (such as Image generation, Video generation, TTS, etc.). The underlying `comfykit` library fully manages parameter tracking and automatic local file uploads.

## 🌟 The 3-Step "Dynamic Adaption" Methodology
Because RunningHub workflow IDs and parameter schemas frequently change, AI Agents MUST strictly follow this 3-step routing and execution pattern:

### Step 1: Intent Routing (Find the Right Workflow ID)
Do NOT guess workflow IDs. Always read the `workflows.yaml` file in this repository first. 
1. Match the user's natural language request (e.g. "Create an action transfer video") to the `description` fields in `workflows.yaml`.
2. Extract the corresponding `id` (e.g., `1985909483975188481`).

### Step 2: Parameter Inspection (Find the Required Inputs)
You must understand what variables the target workflow accepts before invoking it. Use the provided inspection tool:

```bash
python scripts/inspect_workflow.py --workflow <WORKFLOW_ID>
```
**Output Example:**
```text
=== Workflow Inspection: 1983427617984585729 ===
 - Parameter Name : 'prompt' 
   Node Type      : KSampler
 - Parameter Name : 'image' 📁 [REQUIRES ABSOLUTE FILE PATH]
   Node Type      : LoadImage
```

### Step 3: Local Preparation & Execution
1. Take the identified parameters (from Step 2) and the user's instructions.
2. If any parameter is flagged with `[REQUIRES ABSOLUTE FILE PATH]`, ensure you locate that asset on the local disk (e.g. `/tmp/photo.jpg`) and pass its **absolute path**.
3. Construct a standard JSON string payload.
4. Execute using the run script. Under the hood, if the engine sees a valid local file path, it will **automatically and securely invoke the RunningHub Upload API** without any additional code required from you.

```bash
python scripts/run_workflow.py \
  --workflow "1983427617984585729" \
  --params-json '{"prompt": "A futuristic city in the rain", "image": "/tmp/my_photo.jpg"}'
```

---

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
