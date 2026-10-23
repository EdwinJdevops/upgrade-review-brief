"""Targeted system-TLS check of final deployed range metadata and inference."""
import argparse,datetime,html,http.cookiejar,json,re,urllib.parse,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--commit',required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
base='https://upgrade-review-brief.onrender.com'
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
with opener.open(base+'/healthz',timeout=30) as r:
 assert r.status==200 and json.load(r)=={'status':'ready'}
with opener.open(base+'/',timeout=30) as r: page=r.read().decode()
match=re.search(r'name="csrf" value="([^"]+)"',page)
assert match and 'Review the version range' in page
request=urllib.request.Request(base+'/review',data=urllib.parse.urlencode({'csrf':html.unescape(match[1]),'mode':'demo_range'}).encode(),method='POST')
with opener.open(request,timeout=90) as response:
 assert response.status==200
 body=response.read().decode()
raw=re.search(r'<textarea id="report-json" hidden>(.*?)</textarea>',body,re.S)
report=json.loads(html.unescape(raw[1]))
assert report['coverage']['sections'][0]['heading']=='Document preamble'
assert report['coverage']['sections'][0]['start_line']==1
assert report['model_calls']==32 and report['passage_count']==16
assert report['coverage']['unscored_query_passage_pairs']==0
assert len(report['reading_tasks'])==2 and report['status']=='REVIEW_REQUIRED'
assert report['generated_actions']==[] and report['live_identity_verified'] is False
out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':base,'expected_commit_verified_separately_by_render':a.commit,'system_tls_validation':True,'health_status':200,'range_status':200,'preamble_start_line':1,'actual_model':report['model'],'model_windows':report['model_calls'],'source_passages':report['passage_count'],'query_count':len(report['reading_tasks']),'unscored_pairs':report['coverage']['unscored_query_passage_pairs'],'processing_seconds':report['processing_seconds'],'status':report['status'],'scope':'Targeted follow-up after a line-number metadata correction; full desktop/mobile checks for the preceding feature revision are retained separately.'}
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
