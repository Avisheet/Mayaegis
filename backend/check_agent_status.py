import sys
import os
import json
import traceback

# Add the mayaegis directory to the Python path
frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
sys.path.append(frontend)

try:
    from main import agent_running
except ImportError as e:
    print(f"Error importing agent_running from main: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        agent_id = sys.argv[1]
        print(f"Checking agent status for ID: {agent_id}", file=sys.stderr)  # Debug statement

        # Call the agent_running function
        result = agent_running(agent_id)
        print(json.dumps(result))
    except Exception as e:
        print(f"Error in check_agent_status.py: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)  # Print the full traceback
        sys.exit(1)