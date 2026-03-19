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

async def main():
    parser = argparse.ArgumentParser(description="Call RunningHub workflow using ComfyKit securely")
    parser.add_argument("--workflow", required=True, help="RunningHub Workflow ID (e.g. '1983427617984585729') or local JSON wrapper file")
    parser.add_argument("--params-json", required=True, help="JSON string of standard parameters to map (e.g. '{\"prompt\": \"a cat\"}')")
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
                    print(f" - {vid}")
                    
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
