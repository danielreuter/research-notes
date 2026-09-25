"""List failed/errored tests of a pytest JUnit XML (plain or .gz) with the first line of each message.

usage: python3 jfails.py RUN.xml[.gz] [--full]
"""
import gzip
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
full = "--full" in sys.argv
with (gzip.open(path) if path.endswith(".gz") else open(path, "rb")) as f:
    root = ET.parse(f).getroot()
n = 0
for tc in root.iter("testcase"):
    for child in tc:
        if child.tag in ("failure", "error"):
            n += 1
            msg = (child.get("message") or "").replace("\n", " ")
            print(f"{child.tag[:4]} {tc.get('classname')}::{tc.get('name')}  [{msg[:220]}]")
            if full:
                print("    " + (child.text or "")[-3000:].replace("\n", "\n    "))
            break
print("total", n)
