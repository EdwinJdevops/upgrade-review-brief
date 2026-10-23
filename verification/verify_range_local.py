"""Real-model desktop/mobile range-review checks on a loopback app server."""
from datetime import datetime, timezone
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
log=(ROOT/'runner-range-server.log').open('w')
env=dict(os.environ,RERANKER_CPU_THREADS='1')
server=subprocess.Popen([sys.executable,'-m','gunicorn','wsgi:app','--bind','127.0.0.1:8768','--workers','1','--threads','2','--timeout','180','--no-control-socket'],cwd=ROOT,env=env,stdout=log,stderr=log)
try:
    for attempt in range(45):
        if server.poll() is not None: raise RuntimeError('Local app stopped')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8768/healthz',timeout=1) as response:
                if response.status==200: break
        except Exception: time.sleep(0.5)
    else: raise RuntimeError('Local model did not become ready')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000})
        page=context.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8768/',wait_until='networkidle')
        page.screenshot(path=str(ROOT/'verification/range-home-desktop.png'),full_page=True)
        with page.expect_navigation(wait_until='networkidle',timeout=90000):
            page.get_by_role('button',name='Review the version range').click()
        report=json.loads(page.locator('#report-json').input_value())
        assert report['model_calls']==32 and report['passage_count']==16
        assert report['coverage']['unscored_query_passage_pairs']==0
        assert len(report['reading_tasks'])==2 and report['status']=='REVIEW_REQUIRED'
        assert report['model']['name']=='BAAI/bge-reranker-base'
        assert page.locator('[id^="source-L"]').count()==16
        assert page.locator('a[href="#source-L124-L132"]').count()>0
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        for button,expected in [('Download JSON','version_range'),('Download Markdown','Source selection ledger')]:
            with page.expect_download() as download:
                page.get_by_role('button',name=button).click()
            assert expected in Path(download.value.path()).read_text()
        page.screenshot(path=str(ROOT/'verification/range-desktop.png'),full_page=True)
        context.close()
        mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        page=mobile.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8768/',wait_until='networkidle')
        for name,path in [('before','experiment/outputs/kong-range-before.yaml'),('after','experiment/outputs/kong-range-after.yaml'),('notes','model-evaluation/sources/kong-guide.md')]:
            page.locator('input[name='+name+']').set_input_files(str(ROOT/path))
        page.get_by_label('Deployment name').fill('upgrade-review-kong')
        page.get_by_label('Namespace',exact=True).fill('review')
        page.get_by_label('Documentation source URL').fill('https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md')
        assert page.locator('input[name=section]').input_value()==''
        with page.expect_navigation(wait_until='networkidle',timeout=90000):
            page.get_by_role('button',name='Prepare review brief').click()
        uploaded=json.loads(page.locator('#report-json').input_value())
        assert uploaded['coverage']['mode']=='version_range' and uploaded['model_calls']==32
        assert uploaded['input_provenance']=='user_supplied_bytes_not_authenticated'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(ROOT/'verification/range-mobile.png'),full_page=True)
        assert not errors
        result={'checked_at':datetime.now(timezone.utc).isoformat(),'local_only':True,'actual_model':True,'test_double':False,
                'desktop':[1440,1000],'mobile':[390,844],'model_windows_per_review':32,'passages_per_review':16,
                'per_change_queries':2,'unscored_pairs':0,'automatic_upload_selection':True,
                'json_download':True,'markdown_download':True,'no_horizontal_overflow':True,'page_errors':errors,
                'request_processing_seconds':report['processing_seconds'],'status':report['status']}
        (ROOT/'verification/range-local-browser-2026-10-23.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        mobile.close();browser.close()
finally:
    server.terminate()
    try: server.wait(timeout=10)
    except subprocess.TimeoutExpired: server.kill();server.wait()
    log.close()
