import requests
import json
import sys
import yaml

# Usage:
# python runfolder_search.py <search term>

if len(sys.argv) > 1:
    search_term = sys.argv[1]
else:
    print "Missing argument!\nUsage: python search_runfolder.py <search term>"
    sys.exit()

# Load config
with open("/opt/stackstorm/packs/arteria-packs/config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# Get hosts from config
hosts = cfg['runfolder_svc_urls']

# Print header
print "status\trunfolder_link"

for host in hosts:
    result = requests.get("{}/api/1.0/runfolders?state=*".format(host))
    result_json = json.loads(result.text)
    all_runfolders = result_json["runfolders"]
    for runfolder in all_runfolders:
        link = runfolder["link"]
        state = runfolder["state"]
        if search_term in link:
            print "{}\t{}".format(state, link)
