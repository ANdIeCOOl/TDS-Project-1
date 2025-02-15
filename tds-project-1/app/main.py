# /// script
# dependencies = [
#   "fastapi",
#   "requests",
#   "python-dotenv",
#   "uvicorn",
#   "python-dotenv",
#   "beautifulsoup4",
#   "markdown",
#   "requests<3",
#   "duckdb",
#   "numpy",
#   "python-dateutil",
#   "docstring-parser",
#   "httpx",
#   "pydantic",
# ]
# ///
import traceback
import json
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
import os
import logging
from typing import Dict, Callable
from funtion_tasks import (
format_file_with_prettier,
convert_function_to_openai_schema,
query_gpt,
query_gpt_image, 
query_database, 
extract_specific_text_using_llm, 
get_embeddings, 
get_similar_text_using_embeddings, 
extract_text_from_image, 
extract_specific_content_and_create_index, 
process_and_write_logfiles, 
sort_json_by_keys, 
count_occurrences, 
install_and_run_script
)


load_dotenv()
API_KEY = os.getenv("AIPROXY_TOKEN")
URL_CHAT = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
URL_EMBEDDING = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"

app = FastAPI()

RUNNING_IN_CODESPACES = "CODESPACES" in os.environ
RUNNING_IN_DOCKER = os.path.exists("/.dockerenv")
logging.basicConfig(level=logging.INFO)

def ensure_local_path(path: str) -> str:
    """Ensure the path uses './data/...' locally, but '/data/...' in Docker."""
    if ((not RUNNING_IN_CODESPACES) and RUNNING_IN_DOCKER): 
        print("IN HERE",RUNNING_IN_DOCKER) # If absolute Docker path, return as-is :  # If absolute Docker path, return as-is
        return path
    
    else:
        logging.info(f"Inside ensure_local_path with path: {path}")
        return path.lstrip("/")  

function_mappings: Dict[str, Callable] = {
"install_and_run_script": install_and_run_script, 
"format_file_with_prettier": format_file_with_prettier,
"query_database":query_database, 
"extract_specific_text_using_llm":extract_specific_text_using_llm, 
'get_similar_text_using_embeddings':get_similar_text_using_embeddings, 
'extract_text_from_image':extract_text_from_image, 
"extract_specific_content_and_create_index":extract_specific_content_and_create_index, 
"process_and_write_logfiles":process_and_write_logfiles, 
"sort_json_by_keys":sort_json_by_keys, 
"count_occurrences":count_occurrences,

}

def parse_task_description(task_description: str,tools: list):
    response = requests.post(
        URL_CHAT,
        headers={"Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{
                        'role': 'system',
                        'content':"You are intelligent agent that understands and parses tasks. You quickly identify the best tool functions to use to give the desired results"
                            },
                            {
                            "role": "user",
                            "content": task_description
                            }],
                            "tools": tools,
                            "tool_choice":"required",
                }
                     )
    return response.json()["choices"][0]["message"]


def execute_function_call(function_call):
    logging.info(f"Inside execute_function_call with function_call: {function_call}")
    try:
        function_name = function_call["name"]
        function_args = json.loads(function_call["arguments"])
        function_to_call = function_mappings.get(function_name)
        logging.info("PRINTING RESPONSE:::"*3)
        print('Calling function:', function_name)
        print('Arguments:', function_args)
        if function_to_call:
            function_to_call(**function_args)
        else:
            raise ValueError(f"Function {function_name} not found")
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, 
                            detail=f"Error executing function in execute_function_call: {str(e)}",
                            headers={"X-Traceback": error_details}
                            )


@app.post("/run")
async def run_task(task: str = Query(..., description="Plain-English task description")):
    tools = [convert_function_to_openai_schema(func) for func in function_mappings.values()]
    logging.info(len(tools))
    logging.info(f"Inside run_task with task: {task}")
    try:
        function_call_response_message = parse_task_description(task,tools) #returns  message from response
        if function_call_response_message["tool_calls"]:
            for tool in function_call_response_message["tool_calls"]:
                execute_function_call(tool["function"])
        return {"status": "success", "message": "Task executed successfully"}
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, 
                            detail=f"Error executing function in run_task: {str(e)}",
                            headers={"X-Traceback": error_details}
                            )

@app.get("/read",response_class=PlainTextResponse)
async def read_file(path: str = Query(..., description="Path to the file to read")):
    logging.info(f"Inside read_file with path: {path}")
    output_file_path = ensure_local_path(path)
    if not os.path.exists(output_file_path):
        raise HTTPException(status_code=500, detail=f"Error executing function in read_file (GET API")
    with open(output_file_path, "r") as file:
        content = file.read()
    return content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
