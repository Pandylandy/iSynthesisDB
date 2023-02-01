from pony.orm import db_session
from CGRdb.database import db
from chython import smiles
from CGRdb.database import Substance
from multiprocess import Process, Queue
from tqdm import tqdm
import zipfile

def worker(q):
    db.bind(provider='postgres', user='postgres', host='localhost', password="example", database='test',
        port=5432)
    db.generate_mapping()
    while True:
        data = q.get()
        if data is None:
            break
        for i in data:
            mol, label = i
            mol = smiles(mol)
            mol.canonicalize()
            subs = [(x,None) for x in mol.split()]
            for _ in range(10):
                try:
                    with db_session():
                        Substance(subs)
                        break
                except Exception:
                    continue
    print("finished")

q = Queue(maxsize=30)
num_workers=20
pr = [Process(target=worker,
              args=(q,)) for _ in range(num_workers)]
[p.start() for p in pr]

with zipfile.ZipFile("dataset/Chembl28.smi.zip", 'r') as zip_ref:
    zip_ref.extractall("")
with open("Chembl28.smi",) as f:
    tmp = []
    for n, row in tqdm(enumerate(f)):
        if n > 50000:
            break
        columns = row.rstrip('\n').lstrip().split(" ")
        smi = columns[0]
        idx = None
        if len(columns) > 1:
            if columns[1].startswith("|"):
                smi += columns[1]
                if len(columns) > 2:
                    idx = columns[2]
            else:
                idx = columns[1]
        if not idx:
            idx = n
        tmp.append((smi, idx))
        if len(tmp) == 1000:
            q.put(tmp)
            tmp = []
    else:
        q.put(tmp)
    for i in range(num_workers):
        q.put(None)

with db_session:
    db.bind(provider='postgres', user='postgres', host='localhost', password="example", database='test', port=5432)
    db.generate_mapping()
    db.create_fing_index()
    db.create_sim_index()
