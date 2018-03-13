# Micropython-necir
nec ir remote class for Pyboard, ESP(Micropython)

# Usage 
def nec_cb(nec, a, c, r)
    print(a, c, r)				# Address, Command, Repeat

from necir-xxx import NecIr  # replace the -xxx to pyboard or esp
nec = NecIr()
nec.callback(nec_cb)
