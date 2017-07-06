import requests
import json
import sys
 
# Usage:
# python runfolder_search.py <search term>

if len(sys.argv) > 1:
    search_term = sys.argv[1]
else:
    print "Missing argument!\nUsage: python search_runfolder.py <search term>"
    sys.exit()

hosts = ["biotank5", "biotank6" ,"biotank7", "biotank8", "biotank9", "biotank10", "biotank11", "biotank12", "biotank13", "biotank14"]

# Print header
print "status\trunfolder_link"

for host in hosts:
    result = requests.get("http://{}:10800/api/1.0/runfolders?state=*".format(host))
    result_json = json.loads(result.text)
    all_runfolders = result_json["runfolders"]
    for runfolder in all_runfolders:
        link = runfolder["link"]
        state = runfolder["state"]
        if search_term in link:
            print "{}\t{}".format(state, link)
