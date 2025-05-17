import agents
import pentest_tasks
from crewai import Process, Crew
import dynamic_task_generator
import routers
import config_test
import time
import result_logging

#TODO: ADD FUNCTION TO CHECK AND TEST THINGS.

def networkPentTester(question):
    return Crew(
        agents=[
            agents.NetworkPentester,
            agents.ResearcherAgent,
            agents.WriterAgent,
            agents.MakeMarkDownAgent,
        ],
        tasks=[
            dynamic_task_generator.pentest_task(question, agents.NetworkPentester),
            pentest_tasks.cybersecurity_research,
            pentest_tasks.build_cybersecurity_report,
            pentest_tasks.convert_report_to_markdown,
        ],
        process=Process.sequential,
        memory=True,
        cache=True,
        full_output=True,
    )

def WebAppPentTester(question):
    return Crew(
        agents=[
            agents.WebAppPentester,
            agents.ResearcherAgent,
            agents.WriterAgent,
            agents.MakeMarkDownAgent,
        ],
        tasks=[
            dynamic_task_generator.webapp_pentest_task(question, agents.WebAppPentester),
            pentest_tasks.cybersecurity_research,
            pentest_tasks.build_cybersecurity_report,
            pentest_tasks.convert_report_to_markdown,
        ],
        process=Process.sequential,
        memory=True,
        cache=True,
        full_output=True,
    )

def call_vapt_orchestrator(user_question):
    prompt_router = routers.prompt_route(
        config_test.router_model_name,
        config_test.router_config,
        user_question,
    )

    prompt_router = prompt_router.split(", ")
    question = user_question
    crew = None

    if ("Web Application") in prompt_router:
        print("Using Web-App Pentesting crew")
        crew = WebAppPentTester(question)
    elif ("Network") in prompt_router:
        print("Using Network Pentesting crew")
        crew = networkPentTester(question)

    if crew == None:
        raise Exception(f"User request does not aligh with a valid category")

    start_time = time.time()
    result = crew.kickoff()
    runtime = time.time() - start_time

    return {
        "result": result_logging.crewai_result_to_json(result),
        "runtime": {"runtime": runtime, "unit": "seconds"},
    }

