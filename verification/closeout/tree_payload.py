"""Prepare bounded Git tree payloads for the authorized repository update."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
if sys.argv[1]=='prepare':
 tracked=subprocess.check_output(['git','diff','--name-only'],cwd=root,text=True).splitlines()
 untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=root,text=True).splitlines()
 paths=sorted(set(tracked+untracked))
 excluded={'verification/closeout/deploys.md','verification/closeout/health-checks.md'}
 paths=[p for p in paths if p not in excluded and not p.startswith('verification/status-2026-10-25/')]
 batches=[]; batch=[]; size=0
 for name in paths:
  text=(root/name).read_text();entry={'path':name,'mode':'100644','type':'blob','content':text}
  n=len(json.dumps(entry).encode())
  if n>100000:raise RuntimeError('Oversized text payload: '+name)
  if batch and size+n>75000:batches.append(batch);batch=[];size=0
  batch.append(entry);size+=n
 if batch:batches.append(batch)
 (root/'verification/closeout/tree-batches.local.json').write_text(json.dumps(batches))
 print(json.dumps({'batches':len(batches),'files':len(paths),'bytes':sum(len((root/p).read_bytes()) for p in paths),'paths':paths}))
else:
 batches=json.loads((root/'verification/closeout/tree-batches.local.json').read_text())
 print(json.dumps(batches[int(sys.argv[1])]))
