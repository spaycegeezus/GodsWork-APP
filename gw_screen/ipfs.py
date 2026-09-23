import subprocess
import json

def fetch_ledger(cid):
    result = subprocess.check_output(["ipfs", "cat", cid])
    return json.loads(result)

def publish_ledger(path):
    cid = subprocess.check_output(["ipfs", "add", "-q", path])
    return cid.decode().strip()
