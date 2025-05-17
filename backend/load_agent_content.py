import sys
import os
import json
import traceback

# Add the mayaegis directory to the Python path
frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
sys.path.append(frontend)

try:
    from main import load_agent_content
except ImportError as e:
    print(f"Error importing load_agent_content from main: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        paths = json.loads(sys.argv[1])
        print(f"Loading agent content for paths: {paths}", file=sys.stderr)  # Debug statement

        # Call the load_agent_content function
        result = load_agent_content(paths.get("text"), paths.get("json"))
        print(json.dumps(result))
    except Exception as e:
        print(f"Error in load_agent_content.py: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)  # Print the full traceback
        sys.exit(1)