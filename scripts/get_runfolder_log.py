import json
import requests
import argparse



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Get the bcl2fastq log for a runfolder.")
    parser.add_argument('--runfolder', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', default="10900")
    args = parser.parse_args()

    runfolder = args.runfolder
    host = args.host
    port = args.port

    url = "http://{}:{}/api/1.0/logs/{}".format(host, port, runfolder)

    response = requests.get(url)

    json_result = json.loads(response.text)

    log = json_result.get("log")

    print(log)

