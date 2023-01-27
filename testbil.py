from qiwip2py import QiwiP2P
from datetime import timedelta
from Config import QIWI_TOKEN

qiwi_p2p = QiwiP2P(secret_key=QIWI_TOKEN)

qiwi_p2p.reject_bill('64241')

bill = qiwi_p2p.get_bill('64241')

print(bill.status_value)
