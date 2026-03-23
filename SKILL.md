---
name: call_runninghub
description: "Run Cloud AI Workflows via RunningHub using ComfyKit. CURRENT CAPABILITIES INCLUDE: 爆款复刻 (Trending Clone). AI AGENT MUST READ workflows.yaml TO MAP USER INTENT TO WORKFLOW ID."
---

# call_runninghub

<!-- WORKFLOW_CAPABILITIES_START -->

### 🛠️ Automatically Synced Capabilities
*(This section is automatically updated from `workflows.yaml` by `scripts/sync_docs.py`)*

- **爆款复刻 (Trending Clone)** (ID: `2035920199475535874`): 专门用于一键制作“爆款复刻”视频。当用户请求制作爆款复刻、数字人视频复刻时触发此工作流。 【强制入参要求】：此工作流强制要求用户提供 3 个本地文件的绝对路径素材（如果用户没给齐，Agent 必须主动向用户索要）： 1. 一张人物图 (例如：/tmp/person.jpg) 2. 一张产品图 (例如：/tmp/product.png) 3. 要复刻的爆款视频源文件 (例如：/tmp/trending_source.mp4)


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
4. If completed, the script automatically transcodes the downloaded video using `ffmpeg` for maximum chat compatibility and prints both the local path and the `Original URL`.

### 🚨 Step 5: Final Response Rules (CRITICAL)
- **Video Rendering Constraints:** Many third-party chat software (Dify, etc.) fail to render local video paths and show error placeholders or static images.
- Therefore, when returning Video results to the user, you **MUST** provide the `Original URL` directly in the chat as a clickable link.
- **Format:** `[点击这里查看/下载生成的完整视频](Original URL)`
- Never just return a local `/tmp/...` path for videos. Always prioritize outputting the remote URL.

---

## 🔐 Security & API Key Protection
To prevent critical API keys from leaking into shell history logs, terminal outputs, or LLM context windows, **command-line passing of the API key is strictly disabled**.

### How to set the API Key:
1. **Environment Variable (Recommended for Prod):**
   ```bash
   export RUNNINGHUB_API_KEY="your_api_key_here"
   ```
2. **.env file (Recommended for Local Chat):**
   Create a `.env` file in the directory where you run the script:
   ```env
   RUNNINGHUB_API_KEY=your_api_key_here
   ```
*(Note: Never commit your `.env` file to version control. It is ignored in the provided `.gitignore`)*

### 🤖 AI Agent Onboarding Instruction (Handling Missing Keys)
If you (the AI Agent) attempt to run `inspect_workflow.py` or `run_workflow.py` and receive the error **"Security Error: RunningHub API Key is missing!"**, you MUST automatically execute the following conversational onboarding:
1. STOP execution and ask the user: *"I need your RunningHub API Key to proceed. Please paste it in the chat, and I will securely configure it for you."*
2. When the user provides the key, YOU (the AI Agent) must use your file-writing tools to create or overwrite the `.env` file in this repository's root directory with the content:
   `RUNNINGHUB_API_KEY="<THE_KEY_PROVIDED>"`
3. Inform the user that the key was saved securely and automatically resume their original workflow request.
4. **DO NOT** pass the key using command line variables to the scripts. Always write to `.env`!

## Prerequisites
- Python 3.8+
- Installed dependencies: `pip install -r requirements.txt`
