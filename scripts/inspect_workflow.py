#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from comfykit import ComfyKit
    from comfykit.comfyui.workflow_parser import WorkflowParser
except ImportError:
    print("Error: 'comfykit' library is not installed.", file=sys.stderr)
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="Inspect RunningHub workflow parameters")
    parser.add_argument("--workflow", required=True, help="RunningHub Workflow ID")
    args = parser.parse_args()
    
    api_key = os.environ.get("RUNNINGHUB_API_KEY")
    if not api_key:
        print("Error: RUNNINGHUB_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
        
    kit = ComfyKit(runninghub_api_key=api_key)
    try:
        executor = kit._get_runninghub_executor()
        workflow_json = await executor.client.get_workflow_json(args.workflow)
        
        parser_obj = WorkflowParser()
        # Parse it
        metadata = parser_obj.parse_workflow(workflow_json, f"workflow_{args.workflow}")
        
        if not metadata or not metadata.mapping_info or not metadata.mapping_info.param_mappings:
            print(f"No exposed primitive parameters found for workflow {args.workflow}.")
            print("Note: RunningHub workflows generally require parameters to be explicitly 'converted to input' in ComfyUI or follow specific naming conventions.")
            return

        print(f"=== Workflow Inspection: {args.workflow} ===")
        print(f"Found {len(metadata.mapping_info.param_mappings)} mappable parameter(s):")
        print("-" * 50)
        
        # Determine if there's any image/video nodes dynamically
        # MEDIA_UPLOAD_NODE_TYPES imported conditionally from base executor if available
        try:
            from comfykit.comfyui.base_executor import MEDIA_UPLOAD_NODE_TYPES
        except ImportError:
            MEDIA_UPLOAD_NODE_TYPES = []
            
        for mapping in metadata.mapping_info.param_mappings:
            param_name = mapping.param_name
            node_type = mapping.node_class_type
            
            # ComfyKit base upload logic triggers if need_upload flag is True 
            # OR if node_type is in the legacy MEDIA_UPLOAD_NODE_TYPES list.
            need_upload = mapping.need_upload or (node_type in MEDIA_UPLOAD_NODE_TYPES)
            
            upload_req = "📁 [REQUIRES ABSOLUTE FILE PATH]" if need_upload else ""
            print(f" - Parameter Name : '{param_name}' {upload_req}")
            print(f"   Node Type      : {node_type}")
            print(f"   Target Field   : {mapping.input_field}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error inspecting workflow: {e}", file=sys.stderr)
    finally:
        await kit.close()

if __name__ == "__main__":
    asyncio.run(main())
