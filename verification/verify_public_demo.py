"""Check a deployed review app using sanitized committed inputs and real inference."""
import argparse
from datetime import datetime, timezone
import json
import os
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('url')
parser.add_argument('--output',type=Path,help='New evidence path; preserve historical records')
parser.add_argument('--check-range',action='store_true',help='Also exercise the version-range review with actual inference')
parser.add_argument('--allow-proxy-certificate', action='store_true', help='Only for a trusted execution proxy whose CA is absent from Chromium; system TLS health verification remains mandatory.')
args = parser.parse_args()
base = args.url.rstrip('/')
if urlsplit(base).scheme != 'https':
    parser.error('Use the deployed HTTPS URL')
root = Path(__file__).resolve().parents[1]

with sync_playwright() as p:
    proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
    launch = {'headless':True,'args':['--no-sandbox']}
    if proxy_url:
        proxy = urlsplit(proxy_url)
        launch['proxy'] = {'server':proxy.scheme+'://'+proxy.hostname+(':'+str(proxy.port) if proxy.port else '')}
        if proxy.username:
            launch['proxy'].update(username=proxy.username,password=proxy.password or '')
    tls_exception = args.allow_proxy_certificate and bool(proxy_url)
    browser = p.chromium.launch(**launch)
    # The execution proxy's CA is trusted by urllib but not this Chromium profile.
    # Validate health with the system TLS trust first; record the browser exception.
    with urllib.request.urlopen(base + '/healthz', timeout=30) as tls_health:
        assert tls_health.status == 200 and json.loads(tls_health.read()) == {'status':'ready'}
    context = browser.new_context(viewport={'width':1440,'height':1000},ignore_https_errors=tls_exception)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    health = page.request.get(base + '/healthz', timeout=30000)
    assert health.status == 200 and health.json() == {'status':'ready'}
    home = page.goto(base + '/', wait_until='networkidle', timeout=60000)
    assert home.status == 200
    assert 'frame-ancestors' in home.headers['content-security-policy']
    assert home.headers['cache-control'] == 'no-store'
    assert any(c['name']=='session' and c['secure'] and c['httpOnly'] and c['sameSite']=='Strict' for c in context.cookies())
    with page.expect_navigation(wait_until='networkidle', timeout=90000) as review_response:
        page.get_by_role('button', name='Run the model review').click()
    assert review_response.value.status == 200
    demo = json.loads(page.locator('#report-json').input_value())
    assert demo['model_calls'] == 5 and demo['passage_count'] == 5 and demo['passages_omitted'] == 0
    assert demo['status'] == 'REVIEW_REQUIRED' and demo['generated_actions'] == []
    assert demo['model']['name'] == 'BAAI/bge-reranker-base'
    assert demo['source_reference']['commit']=='b39300d09d6d70297dc437015d4a49e484b7b77d'
    assert all('#L' in passage['source_line_url'] for passage in demo['source_passages'])
    assert '/status/ready' in page.locator('table').first.inner_text()
    with page.expect_download() as download:
        page.get_by_role('button', name='Download JSON').click()
    assert json.loads(Path(download.value.path()).read_text())['model_calls'] == 5
    with page.expect_download() as download:
        page.get_by_role('button', name='Download Markdown').click()
    assert 'REVIEW REQUIRED' in Path(download.value.path()).read_text()
    denied = page.request.post(base + '/review', form={'mode':'demo'})
    assert denied.status == 403
    context.close()

    context = browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,ignore_https_errors=tls_exception)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(base + '/',wait_until='networkidle')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    for name, path in [('before','experiment/outputs/kong-old-proxy-only.yaml'),('after','experiment/outputs/kong-new-proxy-only.yaml'),('notes','model-evaluation/sources/kong-guide.md')]:
        page.locator('input[name='+name+']').set_input_files(str(root/path))
    page.get_by_label('Deployment name').fill('upgrade-review-kong')
    page.get_by_label('Namespace',exact=True).fill('review')
    page.get_by_label('Migration section heading').fill('2.26.0')
    page.get_by_label('Documentation source URL').fill('https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260')
    with page.expect_navigation(wait_until='networkidle',timeout=90000) as response:
        page.get_by_role('button',name='Prepare review brief').click()
    assert response.value.status == 200
    upload = json.loads(page.locator('#report-json').input_value())
    assert upload['input_provenance'] == 'user_supplied_bytes_not_authenticated'
    assert upload['model_calls'] == 5 and upload['passages_omitted'] == 0
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    range_summary = None
    if args.check_range:
        page.goto(base+'/',wait_until='networkidle')
        with page.expect_navigation(wait_until='networkidle',timeout=90000) as range_response:
            page.get_by_role('button',name='Review the version range').click()
        assert range_response.value.status == 200
        ranged=json.loads(page.locator('#report-json').input_value())
        assert len(ranged['reading_tasks'])==2 and len(ranged['changes'])==2
        assert ranged['model_calls']==32 and ranged['passage_count']==16
        assert ranged['coverage']['unscored_query_passage_pairs']==0
        assert ranged['status']=='REVIEW_REQUIRED' and ranged['generated_actions']==[]
        assert ranged['input_provenance']=='packaged_demo'
        assert ranged['manifest_inventory']['outside_scope_changed_resources']==3
        assert ranged['manifest_inventory']['metadata_only_modified_resources']==2
        assert ranged['source_reference']['commit']=='b39300d09d6d70297dc437015d4a49e484b7b77d'
        assert not ranged['source_reference']['remote_content_verified_this_review']
        assert page.locator('#manifest-coverage table tbody tr').count()==3
        assert page.locator('#manifest-coverage').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('a[href="#source-L124-L132"]').count()>=1
        with page.expect_download() as range_download:
            page.get_by_role('button',name='Download JSON').click()
        assert len(json.loads(Path(range_download.value.path()).read_text())['coverage']['sections'])>=3
        page.screenshot(path=str(root/'verification/range-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path=str(root/'verification/range-desktop.png'),full_page=True)
        range_summary={key:ranged[key] for key in ('changes','coverage','model_calls','passage_count','reading_tasks','manifest_inventory','processing_seconds')}
    assert not errors
    result = {'checked_at':datetime.now(timezone.utc).isoformat(),'url':base,'actual_model':True,'test_double':False,'system_tls_health_checked':True,'browser_proxy_tls_exception':tls_exception,'health_status':health.status,'demo_status':review_response.value.status,'upload_status':response.value.status,'csrf_without_token_status':denied.status,'secure_session_cookie_checked':True,'json_download_checked':True,'markdown_download_checked':True,'desktop_viewport':[1440,1000],'mobile_viewport':[390,844],'browser_errors':errors,'demo_report':demo,'upload_model_calls':upload['model_calls']}
    if range_summary is not None: result['range_review']=range_summary
    output=args.output or (root/'verification/render-public-browser-2026-10-23.json')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('demo_report','range_review')},indent=2))
    context.close()
    browser.close()
