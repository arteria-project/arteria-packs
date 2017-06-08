
import os
import requests
import json
import argparse
from datetime import datetime

def get_traces_for_tag(tag, headers):
    traces_response = requests.get(
        "{}/{}/?{}={}".format(api_base_url, "traces", "trace_tag", tag),
        headers=headers)
    if not traces_response.ok:
        raise Exception("Response not OK, got: " + traces_response.text)

    return json.loads(traces_response.text)

def get_executions_from_traces(traces, headers):
    for trace in traces:
        trace_id = trace["id"]
        trace_info_response = requests.get(
            "{}/{}/{}".format(api_base_url, "traces", trace_id),
            headers=headers)
        trace_info = json.loads(trace_info_response.text)
        action_executions = map(lambda x: x["object_id"], trace_info["action_executions"])
        for execution in action_executions:
            yield execution

def get_actions_from_executions(executions, headers):
    for execution_id in executions:
        execution_info_response = requests.get(
            "{}/{}/{}".format(api_base_url, "executions", execution_id),
            headers=headers)
        execution_info = json.loads(execution_info_response.text)
        yield execution_info

def filter_actions_by_name(actions, name):
    return (action for action in actions if action["action"]["name"] == name)

def sort_actions_by_timestamp(actions):
    def get_start_time(action):
        #Select start_time, e.g. 2017-05-29T15:03:03.818222Z for each action. Remove everything after ".".
        start_time = datetime.strptime(action['start_timestamp'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        return start_time
    #Compare elements in actions on key value start_timestamp.
    sort_actions = sorted(actions, key=get_start_time)
    return sort_actions

if __name__ == "__main__":

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

    traces = get_traces_for_tag(args.tag, access_headers)
    executions = get_executions_from_traces(traces, access_headers)
    #print list(executions)
    actions = get_actions_from_executions(executions, access_headers)
    filtered_actions = filter_actions_by_name(actions, workflow_name)
    sorted_actions = sort_actions_by_timestamp(filtered_actions)
    for a in sorted_actions:
        print a["id"]
