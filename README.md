# Call RunningHub Skill

This repository contains a standalone AI Skill wrapper for triggering cloud workflows via [RunningHub](https://www.runninghub.ai/) using the `comfykit` library.

It securely bridges arbitrary frontend parameters (like `prompt`, `width`, local `image` files) into the precise structured API calls required by RunningHub.

## 🚀 Features
- **Zero-Config Parameter Mapping**: Dynamically translates basic parameters (`prompt="cat"`) to complex ComfyUI Variable formats internally mapped to `nodeId`/`fieldName`.
- **Automatic File Handling**: If a parameter corresponds to an image/video node and contains a local file path, the script intercepts it and handles the `POST /task/openapi/upload` automatically.
- **Secure by Default**: Prevents API Key leakage by strictly enforcing key reading via the Operating Server Environment (`RUNNINGHUB_API_KEY`) or local ignored `.env` files.

## 🛠️ Installation
```bash
pip install -r requirements.txt
```

## 📖 Usage
Please see `SKILL.md` for detailed instructions on how AI Agents should consume this skill.

```bash
# Set your API Key
export RUNNINGHUB_API_KEY="your_api_key_here"

# Execute
python scripts/run_workflow.py \
  --workflow "1983427617984585729" \
  --params-json '{"prompt": "A futuristic city in the rain, cyberpunk style", "width": 1024, "height": 768}'
```
