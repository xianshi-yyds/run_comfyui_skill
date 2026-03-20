#!/usr/bin/env python3
import asyncio
import argparse
import json
import os
import sys

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file securely
    load_dotenv()
except ImportError:
    pass

try:
    from comfykit import ComfyKit
except ImportError:
    print("Error: 'comfykit' library is not installed or not found in the environment.", file=sys.stderr)
    print("Please install it: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)
import subprocess

def ensure_web_safe_video(video_url_or_path):
    import urllib.request
    from urllib.parse import urlparse
    import tempfile
    
    is_url = urlparse(video_url_or_path).scheme in ('http', 'https')
    local_path = video_url_or_path
    
    if is_url:
        print(f"⬇️ Downloading video: {video_url_or_path}")
        try:
            temp_fd, local_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)
            urllib.request.urlretrieve(video_url_or_path, local_path)
            print(f"✅ Downloaded to temporal path: {local_path}")
        except Exception as e:
            print(f"⚠️ Failed to download video for transcoding: {e}")
            return video_url_or_path
            
    try:
        import imageio_ffmpeg
        ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg_cmd = "ffmpeg"

    try:
        subprocess.run([ffmpeg_cmd, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("⚠️ 'ffmpeg' binary is missing (not in PATH and imageio-ffmpeg not installed). Skipping web-safe video transcoding.")
        return local_path
        
    out_path = local_path.replace(".mp4", "_websafe.mp4")
    if out_path == local_path:
        out_path = local_path + "_websafe.mp4"
        
    print("🔄 Transcoding video to web-safe format (libx264/yuv420p)...")
    cmd = [
        ffmpeg_cmd, "-y", "-i", local_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        out_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"✅ Transcoded successfully: {out_path}")
        return out_path
    except Exception as e:
        print(f"⚠️ FFmpeg transcoding failed: {e}. Falling back to original.")
        return local_path

async def main():
    parser = argparse.ArgumentParser(description="Call RunningHub workflow using ComfyKit securely")
    parser.add_argument("--workflow", required=True, help="RunningHub Workflow ID (e.g. '1983427617984585729') or local JSON wrapper file")
    parser.add_argument("--params-json", required=True, help="JSON string of standard parameters to map (e.g. '{\"prompt\": \"a cat\"}')")
    parser.add_argument("--async-mode", action="store_true", help="Submit the task and return the Task ID immediately without waiting for completion.")

    # intentionally omitting --api-key from args to prevent command line history leakage!
    
    args = parser.parse_args()
    
    # Retrieve API key SECURELY via Environment Variable only
    api_key = os.environ.get("RUNNINGHUB_API_KEY")
    if not api_key:
        print("🔒 Security Error: RunningHub API Key is missing!", file=sys.stderr)
        print("To prevent credential leakage in bash history, passing the API key via command line arguments is disabled.", file=sys.stderr)
        print("Please set the RUNNINGHUB_API_KEY environment variable, or create a .env file in the current directory.", file=sys.stderr)
        sys.exit(1)
        
    try:
        params = json.loads(args.params_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing --params-json: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🚀 Executing workflow: {args.workflow}")
    print(f"📦 Parameters: {json.dumps(params, indent=2, ensure_ascii=False)}")
    print(f"🔐 API Key loaded securely from environment.")
    
    # Initialize ComfyKit with RunningHub execution configuration
    kit = ComfyKit(runninghub_api_key=api_key)
    try:
        executor = kit._get_runninghub_executor()
        
        if args.async_mode:
            print(f"⚡ ASYNC MODE ACTIVATED: Submitting task and returning ID directly.")
            # Map parameters by pulling definitions
            workflow_json = await executor.client.get_workflow_json(args.workflow)
            from comfykit.comfyui.workflow_parser import WorkflowParser
            parser_obj = WorkflowParser()
            metadata = parser_obj.parse_workflow(workflow_json, f"workflow_{args.workflow}")
            
            # This securely auto-uploads any absolute paths before sending payload
            node_info_list = await executor._convert_params_to_node_info_list(metadata.mapping_info, params, executor.client)
            
            # Fire and forget
            task_id = await executor.client.create_task(args.workflow, node_info_list)
            
            print(f"\n✅ [ASYNC SUCCESS] Task submitted to RunningHub!")
            print(f"➡️ Task ID: {task_id}")
            print("Use `python scripts/check_status.py --task-id <ID>` to poll for completion.")
            
            # Optionally persist it to tasks.json in repo root
            tasks_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tasks.json")
            try:
                task_history = {}
                if os.path.exists(tasks_file):
                    with open(tasks_file, 'r') as tf:
                        task_history = json.load(tf)
                task_history[task_id] = {"workflow": args.workflow, "params": params}
                with open(tasks_file, 'w') as tf:
                    json.dump(task_history, tf, ensure_ascii=False, indent=2)
            except Exception:
                pass
                
            sys.exit(0)

        # Synchronous Mode
        result = await kit.execute(args.workflow, params)
        if result.status == "completed":
            print("\n✅ Task completed successfully!")
            
            # Print Outputs
            if hasattr(result, 'images') and result.images:
                print(f"Images ({len(result.images)}):")
                for img in result.images:
                    print(f" - {img}")
                    
            if hasattr(result, 'videos') and result.videos:
                print(f"Videos ({len(result.videos)}):")
                for vid in result.videos:
                    safe_vid = ensure_web_safe_video(vid)
                    print(f" - {safe_vid}")
                    
            if hasattr(result, 'texts') and result.texts:
                print(f"Texts ({len(result.texts)}):")
                for txt in result.texts:
                    print(f" - {txt}")
                    
            if hasattr(result, 'audios') and result.audios:
                print(f"Audios ({len(result.audios)}):")
                for aud in result.audios:
                    print(f" - {aud}")
                    
        else:
            print(f"\n❌ Task failed: {result.msg}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error executing workflow: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await kit.close()

if __name__ == "__main__":
    asyncio.run(main())
