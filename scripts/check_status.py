#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from comfykit import ComfyKit
except ImportError:
    print("Error: 'comfykit' library is not installed.", file=sys.stderr)
    sys.exit(1)

# Import the ffmpeg transcode helper directly from run_workflow relative module
# To avoid module errors if not run perfectly, we redefine it here safely
def ensure_web_safe_video(video_url_or_path):
    import subprocess
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
    parser = argparse.ArgumentParser(description="Query status of an Asynchronous RunningHub task")
    parser.add_argument("--task-id", required=True, help="The Task ID printed during async invocation")
    args = parser.parse_args()
    
    api_key = os.environ.get("RUNNINGHUB_API_KEY")
    if not api_key:
        print("Error: RUNNINGHUB_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
        
    kit = ComfyKit(runninghub_api_key=api_key)
    try:
        executor = kit._get_runninghub_executor()
        status_data = await executor.client.get_task_status(args.task_id)
        status = status_data.get('status')
        
        print(f"Current Status: {status}")
        
        if status == 'SUCCESS':
            print("\n✅ Task completed successfully!")
            outputs = await executor.client.get_task_outputs(args.task_id)
            
            # Simple extraction reproducing comfykit's Result packaging
            images = outputs.get('images', [])
            videos = outputs.get('videos', [])
            
            if images:
                print(f"Images ({len(images)}):")
                for img in images:
                    print(f" - {img}")
                    
            if videos:
                print(f"Videos ({len(videos)}):")
                for vid in videos:
                    safe_vid = ensure_web_safe_video(vid)
                    print(f" - {safe_vid}")
                    
        elif status == 'FAIL':
            print(f"❌ Task failed: {status_data}", file=sys.stderr)
            sys.exit(1)
        else:
            print("⏳ Task is still running or pending...")
            
    except Exception as e:
        print(f"Error checking status: {e}", file=sys.stderr)
    finally:
        await kit.close()

if __name__ == "__main__":
    asyncio.run(main())
