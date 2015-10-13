
import os
import requests
import json
import argparse

parser = argparse.ArgumentParser(description="Gets execution ids associated with a trace tag (e.g. a runfolder) and a "
                                             "workflow. It can be used to track executions, e.g: "
                                             "python scripts/trace_runfolder.py --tag 150605_M00485_0183_000000000-ABGT6_testbio14 | xargs -n1 st2 execution get")
parser.add_argument('--tag', required=True)
parser.add_argument('--api_base_url', default="http://localhost:9101/v1")
parser.add_argument('--workflow', default="ngi_uu_workflow")
args = parser.parse_args()

api_base_url = args.api_base_url
workflow_name = args.workflow

# Try to load access token from environment - fall back if not available
try:
    access_token = os.environ['ST2_AUTH_TOKEN']
except KeyError as e:
    print("Could not find ST2_AUTH_TOKEN in environment. Please set it to your st2 authentication token.")

access_headers = {"X-Auth-Token": access_token}

def get_traces_for_tag(tag, headers):
    traces_response = requests.get(
        "{}/{}/?{}={}".format(api_base_url, "traces", "trace_tag", tag),
        headers=headers)
    if not traces_response.ok:
        raise Exception("Response not OK, got: " + traces_response.text)

    return json.loads(traces_response.text)

def get_executions_from_traces(traces, headers):
    executions = []
    for trace in traces:
        trace_id = trace["id"]
        trace_info_response = requests.get(
            "{}/{}/{}".format(api_base_url, "traces", trace_id),
            headers=headers)
        trace_info = json.loads(trace_info_response.text)
        action_executions = map(lambda x: x["object_id"], trace_info["action_executions"])
        executions += action_executions

    return executions

def get_actions_from_executions(executions, headers):
    actions = []
    for execution_id in executions:
        execution_info_response = requests.get(
            "{}/{}/{}".format(api_base_url, "executions", execution_id),
            headers=headers)
        execution_info = json.loads(execution_info_response.text)
        actions.append(execution_info)

    return actions

def filter_actions_by_name(actions, name):
    return [action for action in actions if action["action"]["name"] == name]

# -----------
# Main script
# -----------
traces = get_traces_for_tag(args.tag, access_headers)
executions = get_executions_from_traces(traces, access_headers)
actions = get_actions_from_executions(executions, access_headers)
filtered_actions = filter_actions_by_name(actions, workflow_name)
for a in filtered_actions:
    print a["id"]
