
import yaml
import sys
import argparse
from graphviz import Digraph


def add_edges(dot, look_up_key, task_name, task):
    on_success_key = look_up_key
    if on_success_key not in task:
        pass
    else:
        dependencies = task[on_success_key]
        for elem in dependencies:
            # If a part of the workflow branches in mistral
            # this will be represented as a list of dict.
            # That is the reason for this somewhat ugly check.
            if type(elem) is dict:
                for key in elem:
                    dot.edge(task_name, key, label=elem[key])
            else:
                dot.edge(task_name, elem)


def add_success_edges(dot, task_name, task):
    add_edges(dot, "on-success", task_name, task)


def add_error_edges(dot, task_name, task):
    add_edges(dot, "on-error", task_name, task)


def main(argv):

    parser = argparse.ArgumentParser(description='Create a dot representation of the give mistral workflow file')
    parser.add_argument('--file', required=True, help='Path to workflow file')
    parser.add_argument('--output', required=True, help='Path to output file')
    parser.add_argument('--format', required=False, help='Format of output file', default="png")

    args = parser.parse_args()

    with open(args.file, "r") as f:
        workflow = yaml.load(f)

    tasks = workflow["workflows"]["main"]["tasks"]

    dot = Digraph(comment='Workflow description', format=args.format)
    for key in tasks:
        task = tasks[key]
        dot.node(key)
        add_success_edges(dot, key, task)
        add_error_edges(dot, key, task)

    dot.render(args.output)


if __name__ == "__main__":
    main(sys.argv[1:])
