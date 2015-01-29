# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Firefox about:memory log parser.


# "basically: |./about_memory_parser memory_report.json "explicit/"| would give you the explicit value, you could pump that through find and call it good"

import json
import collections
import sys
import operator
import gzip

from pprint import pprint

def path_total(data, path):
    totals = collections.defaultdict(int)
    totals_heap = collections.defaultdict(int)
    totals_heap_allocated = collections.defaultdict(int)
    for report in data["reports"]:
        if report["path"].startswith(path):
            totals[report["process"]] += report["amount"]
            if report["kind"] == 1:
              totals_heap[report["process"]] += report["amount"]
        elif report["path"] == "heap-allocated":
          totals_heap_allocated[report["process"]] = report["amount"]

    if path == "explicit/":
      for k, v in totals_heap.items():
        if k in totals_heap_allocated:
          heap_unclassified = totals_heap_allocated[k] - totals_heap[k]
          totals[k] += heap_unclassified

    return totals


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Need two arguments: a file name and a path prefix to match against."

        exit(-1)
    file_path = sys.argv[1]
    tree_path = sys.argv[2]
    json_data = open(file_path)
    try:
        data = json.load(json_data)
        json_data.close()
    except ValueError, e:
        print "Error:", e
        print "Maybe this is a zip file."
        json_data.close()
        json_data = gzip.open(file_path, 'rb')
        data = json.load(json_data)
        json_data.close()

    totals = path_total(data, tree_path);
    sorted_totals = sorted(totals.iteritems(), key=lambda(k,v): (-v,k))
    for (k, v) in sorted_totals:
        if v:
            print "{0}\t".format(k),
    print ""
    for (k, v) in sorted_totals:
        if v:
            print "{0}\t".format(v),
    print ""
