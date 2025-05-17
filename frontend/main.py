import os
import sys
import re
import uuid
import shlex
import time
import subprocess
import json
import random
from openai import OpenAI
import streamlit as stlit
# import config as config_test


config_file_path = os.path.join(str("/".join(__file__.split("/")[:-2])), "mayaegis")
sys.path.append(config_file_path)
sys.path.append(config_file_path)
import config_test


def replace_local_urls(text):
    # regex to match the URLs with localhost, 127.0.0.1, with optional http(s) and www
    pattern = re.compile(
        r"(https?:\/\/)?(www\.)?(localhost|127\.0\.0\.1)(:[0-9]+)?", re.IGNORECASE
    )

    # replace all matching patterns
    return pattern.sub(r"\1\2host.docker.internal\4", text)


def run_agents(user_question):
    user_question = replace_local_urls(user_question)
    events_dir = config_test.events_dir
    cli_filepath = config_test.cli_filepath

    clid = f"{uuid.uuid4()}_{int(time.time())}"
    cli_id = shlex.quote(f"{clid}")
    user_question = shlex.quote(user_question)

    cmd = f"python3 {cli_filepath} --current_job_id {cli_id} --user_question {user_question} --events_directory {events_dir} &"


    os.system(cmd)

    return {
        "id": clid,
        "paths": {
            "text": os.path.join(events_dir, f"{cli_id}.txt"),
            "json": os.path.join(events_dir, f"{cli_id}.json"),
        },
    }

def agent_running(id):
    command = f"ps aux | grep {id} | grep 'python' | grep -v 'grep'"

    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    output = result.stdout

    pid = None
    try:
        pid = int([item for item in output.split(" ") if item][1])
    except:
        pass

    running = True
    if len(output) == 0:
        running = False

    return {"pid": pid, "status": running}

def load_agent_content(text_path=None, json_path=None):
    output = {"text": None, "json": None}

    if text_path != None and os.path.exists(text_path):
        with open(text_path, "r") as file:
            output["text"] = file.read()

    if json_path != None and os.path.exists(json_path):
        with open(json_path, "r") as f:
            output["json"] = json.load(f)

    return output


def clean_text(text):
    cleaned_text = re.sub(r"^(```markdown|```md|```)\s*", "", text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"```$", "", cleaned_text)
    return cleaned_text.strip()


def remove_color_codes(text):
    # Compile a regular expression pattern to match ANSI escape sequences
    ansi_escape = re.compile(
        r"""
        \x1B  # ESC - Matches the ESC character (hexadecimal 1B), which starts ANSI escape sequences
        (?:   # Non-capturing group starts
            [@-Z\\-_]  # Matches control characters from the C1 character set (except CSI)
        |     # OR (alternation operator)
            \[  # Matches the '[' character which starts a CSI (Control Sequence Introducer) sequence
            [0-?]*  # Matches the parameter bytes of the CSI sequence (optional)
            [ -/]*  # Matches any intermediate bytes (optional)
            [@-~]   # Matches the final byte of the CSI sequence (indicates the control type, like color or style)
        )
    """,
        re.VERBOSE,  # re.VERBOSE allows us to write the regex in a more readable format with comments
    )

    # Substitute (remove) all matching ANSI escape sequences in the input text
    return ansi_escape.sub("", text)  # Replace the escape sequences with an empty string, effectively removing them


def generate_loading_screen(total_boxes=100):
    assets = "⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿"
    
    words_to_insert = ["MAYA", "AEGIS", "M'ayAegis"]
    
    assets = list(assets)
    
    for _ in range(total_boxes):
        # Randomly decide to insert a word from the list
        if random.random() < 0.05:  # 5% chance to insert a word
            word_to_insert = random.choice(words_to_insert)
            position = random.randint(0, len(assets))
            assets.insert(position, word_to_insert)
    
    # Shuffle the list to add randomness
    random.shuffle(assets)
    
    # Return the final string after joining
    return "".join(assets)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


if "submitted" not in stlit.session_state:
    stlit.session_state["submitted"] = False
    stlit.session_state["messages"] = []
    stlit.session_state["website"] = ""
    stlit.session_state["sys_prompt"] = ""
    stlit.session_state["openai_model"] = "gpt-4o-2024-11-20"
    stlit.session_state["run_agent"] = False
    stlit.session_state["agent_running"] = False
    stlit.session_state["init_agent_output"] = {}
    stlit.session_state["agent_done"] = False
    stlit.session_state["stream_max_i"] = -1
    stlit.session_state["agent_words_gened"] = 0
    stlit.session_state["job_failed"] = False
    stlit.session_state["start_time"] = 0


stlit.markdown("<h1 style='text-align: center;'>M'ayAegis</h1>", unsafe_allow_html=True)

stlit.write("\n")
stlit.image(
    image=os.path.join("/".join(os.path.abspath(__file__).split("/")[:-1]), "logo.png")
)

stlit.write("\n")

if stlit.session_state["agent_running"]:
    aid = stlit.session_state["init_agent_output"]["id"]
    astatus = agent_running(aid)
    print("===> astatus: ", astatus)
    if astatus["status"] == True:
        print(f"Agent id {aid} is still running...")
        text_file_path = stlit.session_state["init_agent_output"]["paths"]["text"]
        if os.path.exists(text_file_path):
            with open(text_file_path, "r") as file:
                text_content = file.read()
            ascii_loading_text = generate_loading_screen()
            text_content = (
                ascii_loading_text + "\n\n" + text_content + "\n\n" + ascii_loading_text
            )
            stlit.code(remove_color_codes(text_content))
        time.sleep(1)

        stlit.rerun()
    else:
        print(f"Agent id {aid} is DONE!")
        stlit.session_state["agent_running"] = False
        docs = load_agent_content(
            stlit.session_state["init_agent_output"]["paths"]["text"],
            stlit.session_state["init_agent_output"]["paths"]["json"],
        )

        # print final result
        try:
            runtime = time.time() - stlit.session_state["start_time"]

            # add raw output from agents running (saved stdout outputs)
            reformated_docs_text = (
                f"```\n" + str(docs["text"]).replace("```", '"""') + f"\n```"
            )
            reformated_docs_text = f"""
## Job's ID
                 
{aid}

## Runtime

{runtime} seconds

## Raw Agent(s) Output

{reformated_docs_text}
"""
            stlit.session_state.messages.append(
                {"role": "system", "content": reformated_docs_text}
            )

            final_report = clean_text(docs["json"]["output"]["result"]["final_output"])
            stlit.session_state.messages.append(
                {"role": "system", "content": final_report}
            )
        except Exception as err:
            print("---> ERROR LOADING FINAL REPORT:", err)
            text_file_path = stlit.session_state["init_agent_output"]["paths"]["text"]
            if os.path.exists(text_file_path):
                with open(text_file_path, "r") as file:
                    text_content = file.read()
                if len(text_content) > 0:
                    stlit.session_state.messages.append(
                        {"role": "system", "content": text_content}
                    )
            try:
                error_msg = docs["json"]["error"]
            except:
                error_msg = str(err)

            stlit.session_state.messages.append(
                {
                    "role": "system",
                    "content": f"Job Completely Failed Due To: {error_msg}",
                }
            )

            stlit.session_state.messages.append(
                {"role": "system", "content": f"🚨 Try Again By Refreshing The Page 🚨"}
            )

            stlit.session_state["job_failed"] = True

        stlit.session_state["agent_done"] = True
        stlit.rerun()

# User input form
if not stlit.session_state["submitted"] and not stlit.session_state["run_agent"]:
    with stlit.form("my_form"):
        stlit.session_state["website"] = stlit.text_input(
            "What's Your Target Website/Network Address?", stlit.session_state["website"]
        )
        text = stlit.text_area("What Cybersecurity-Related Task Do You Want To Do?", "")
        submitted = stlit.form_submit_button("Submit")

    # Handle form submission
    if (
        submitted
        and not stlit.session_state["submitted"]
        and not stlit.session_state["run_agent"]
    ):
        if not stlit.session_state["website"]:
            stlit.warning("Please Enter A Valid Website (URL)", icon="⚠️")
        else:
            first_prompt = f"""
### Website to Analyze:

{stlit.session_state["website"]}

### Task Description:

{text}
"""
            stlit.session_state["sys_prompt"] = first_prompt
            stlit.session_state.messages.append(
                {"role": "system", "content": stlit.session_state["sys_prompt"]}
            )
            stlit.session_state["submitted"] = True
            stlit.session_state["run_agent"] = True
            stlit.rerun()

if stlit.session_state["run_agent"] == True:
    stlit.session_state["start_time"] = time.time()
    init_agent_output = run_agents(stlit.session_state["sys_prompt"])
    print(f"Started new agent session: {init_agent_output['id']}")
    stlit.session_state["init_agent_output"] = init_agent_output
    stlit.session_state["run_agent"] = False
    print(stlit.session_state["agent_running"])
    stlit.session_state["agent_running"] = True
    print(stlit.session_state["agent_running"])
    print()
    stlit.rerun()

# Display messages from session state
for message in stlit.session_state["messages"]:
    with stlit.chat_message(message["role"]):
        stlit.markdown(message["content"])

if (
    stlit.session_state["submitted"]
    and stlit.session_state["agent_done"]
    and not stlit.session_state["job_failed"]
):
    # Chat input for interaction
    prompt = stlit.chat_input("Ask about the commands executed")
    if prompt:
        stlit.session_state.messages.append({"role": "user", "content": prompt})
        with stlit.chat_message("user"):
            stlit.markdown(prompt)

        # Call OpenAI's API to generate a response
        with stlit.chat_message("assistant"):
            print('Hola...')
            stream = client.chat.completions.create(
                model=stlit.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in stlit.session_state.messages
                ],
                stream=True,
            )
            response = stlit.write_stream(stream)
            stlit.session_state.messages.append({"role": "assistant", "content": response})