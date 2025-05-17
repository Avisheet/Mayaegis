import sys
import os
import json
import traceback

# Add the mayaegis directory to the Python path
frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
sys.path.append(frontend)

try:
    from main import run_agents
except ImportError as e:
    print(f"Error importing run_agents from main: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        user_question = sys.argv[1]
        print(f"Running agent with user question: {user_question}", file=sys.stderr)  # Debug statement

        # Call the run_agents function
        result = run_agents(user_question)
        print(json.dumps(result))
    except Exception as e:
        print(f"Error in run_agents.py: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)  # Print the full traceback
        sys.exit(1)