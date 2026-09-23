from utils.ipfs import fetch_ledger
from utils.merger import merge_ledgers
from utils.data_handler import DataHandler

data = DataHandler()

def handle_rf_sync_frame(frame):
    """
    frame contains:
    - ledger_root
    - ipfs_cid
    - height
    """

    remote_ledger = fetch_ledger(frame["ipfs_cid"])

    local_ledger = data.load_ledger()

    merged = merge_ledgers(local_ledger, remote_ledger)

    if merged:
        data.save_ledger(merged)
        data.rebuild_balances_from_ledger()
