"""Fetch public benchmark source snapshots; refuse changed source identities."""
import base64
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
dest=ROOT/'sources'
dest.mkdir(exist_ok=True)
for repo,sha,name in [
    ('Kong/charts','893527759a66e5293aded6999f8c6879b634c6d6','kong-guide.md'),
    ('kubernetes/kube-state-metrics','0108cede906f11d049a07b3d095b622ec5a4d957','ksm-readme.md'),
]:
    with urllib.request.urlopen(f'https://api.github.com/repos/{repo}/git/blobs/{sha}',timeout=30) as r:
        data=base64.b64decode(json.load(r)['content'])
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=sha:
        raise RuntimeError('Source Git blob identity mismatch')
    (dest/name).write_bytes(data)
with urllib.request.urlopen('https://api.github.com/repos/external-secrets/external-secrets/issues/4662',timeout=30) as r:
    data=json.load(r)['body'].encode()
if hashlib.sha256(data).hexdigest()!='8079a93898ccdf4b8cf90850794079c6b32c2a5eb6aef70ed10bb1685c968be7':
    raise RuntimeError('The mutable ESO issue body changed; do not silently replace a frozen benchmark source')
(dest/'eso-guide.md').write_bytes(data)
print('Benchmark source identities verified.')
