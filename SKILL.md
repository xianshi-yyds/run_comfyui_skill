---
name: call_runninghub
description: "Run Cloud AI Workflows via RunningHub using ComfyKit. CURRENT CAPABILITIES INCLUDE: image_flux, video_wan2.1_fusionx. AI AGENT MUST READ workflows.yaml TO MAP USER INTENT TO WORKFLOW ID."
---

# call_runninghub

<!-- WORKFLOW_CAPABILITIES_START -->

### 🛠️ Automatically Synced Capabilities
*(This section is automatically updated from `workflows.yaml` by `scripts/sync_docs.py`)*

- **image_flux** (ID: `1983427617984585729`): Generates high quality text-to-images using Flux. Trigger when the user asks for art, images, avatars, or general pictures.
- **video_wan2.1_fusionx** (ID: `1985909483975188481`): Generates videos using the Wan2.1 framework. Used for action transfer, animating images, or creating videos. Trigger when the user asks to animate a photo or create a video.

<!-- WORKFLOW_CAPABILITIES_END -->

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
2. If any parameter requires an absolute file path, locate it and pass it.
3. Construct the JSON string payload.
4. **CRITICAL: Asynchronous Execution vs Synchronous**
   - If generating an Image or quick task: run SYNCHRONOUSLY.
   - If generating a **Video** or **Long Task**: ALWAYS run ASYNCHRONOUSLY by passing `--async-mode`.
   - Never wait more than a few minutes synchronously. A video takes 10-30 minutes and will crash the Agent context if waited sequentially.
   
```bash
# Synchronous (Images)
python scripts/run_workflow.py \
  --workflow "1983427617984585729" \
  --params-json '{"prompt": "A city in the rain"}'

# Asynchronous (Videos)
python scripts/run_workflow.py \
  --workflow "1985909483975188481" \
  --params-json '{"image": "/tmp/source.jpg"}' \
  --async-mode
```

### Step 4: Polling the Video (If Async)
1. The `--async-mode` will instantly print a `Task ID` (e.g., `188981249712...`) and exit.
2. Inform the USER that the video generation is in progress.
3. In subsequent turns, check the status using:
```bash
python scripts/check_status.py --task-id <TASK_ID>
```
4. If completed, the script will automatically transcode the downloaded video using `ffmpeg` to ensure maximum third-party chat compatibility.

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
