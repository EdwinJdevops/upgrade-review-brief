import json, os, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'docs/demo'
log=(root/'runner-browser-server.log').open('w')
env=os.environ.copy(); env['RERANKER_CPU_THREADS']='1'
server=subprocess.Popen([sys.executable,'-m','gunicorn','wsgi:app','--bind','127.0.0.1:8766','--workers','1','--threads','2','--timeout','180','--no-control-socket'],cwd=root,env=env,stdout=log,stderr=log)
try:
 for i in range(90):
  if server.poll() is not None: raise RuntimeError('server exited')
  try:
   with urllib.request.urlopen('http://127.0.0.1:8766/healthz',timeout=1) as r:
    if r.status==200: break
  except Exception: time.sleep(1)
 else: raise RuntimeError('server not ready')
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1440,'height':1000},record_video_dir=str(root/'runner-browser-recording'),record_video_size={'width':1440,'height':1000},reduced_motion='reduce')
  page=context.new_page()
  errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
  page.goto('http://127.0.0.1:8766/',wait_until='networkidle')
  page.screenshot(path=str(out/'home-desktop.png'),full_page=True)
  assert page.locator('h1').inner_text()=='Less digging.\nMore context.'
  page.wait_for_timeout(3000)
  with page.expect_navigation(wait_until='networkidle'):
   page.get_by_role('button',name='Run the model review').click()
  assert page.locator('.status').inner_text()=='REVIEW REQUIRED'
  assert page.locator('.passage').count()==5
  assert '/status/ready' in page.locator('table').inner_text()
  page.screenshot(path=str(out/'report-desktop.png'),full_page=True)
  actual_report=json.loads(page.locator('#report-json').input_value())
  assert actual_report['model_calls']==5 and actual_report['passages_omitted']==0
  assert actual_report['model']['runtime']=='server_cpu_float32'
  page.wait_for_timeout(3500)
  page.locator('.report-section').nth(1).scroll_into_view_if_needed()
  page.wait_for_timeout(3500)
  page.locator('.unresolved').scroll_into_view_if_needed()
  page.wait_for_timeout(3500)
  with page.expect_download() as dl:
   page.get_by_role('button',name='Download JSON').click()
  assert json.loads(Path(dl.value.path()).read_text())['status']=='REVIEW_REQUIRED'
  with page.expect_download() as dl:
   page.get_by_role('button',name='Download Markdown').click()
  assert 'REVIEW REQUIRED' in Path(dl.value.path()).read_text()
  page.wait_for_timeout(1500)
  video=page.video
  context.close()
  video.save_as(str(out/'browser-demo.webm'))
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out/'browser-demo.webm'),'-vf','scale=960:-2','-r','12','-c:v','libx264','-preset','fast','-crf','30','-movflags','+faststart',str(out/'browser-demo.mp4')],check=True)
  mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=1,has_touch=True)
  page=mobile.new_page()
  page.goto('http://127.0.0.1:8766/',wait_until='networkidle')
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.screenshot(path=str(out/'home-mobile.png'),full_page=True)
  page.locator('input[name=before]').set_input_files(str(root/'experiment/outputs/kong-old-proxy-only.yaml'))
  page.locator('input[name=after]').set_input_files(str(root/'experiment/outputs/kong-new-proxy-only.yaml'))
  page.locator('input[name=notes]').set_input_files(str(root/'model-evaluation/sources/kong-guide.md'))
  page.get_by_label('Deployment name').fill('upgrade-review-kong')
  page.get_by_label('Namespace',exact=True).fill('review')
  page.get_by_label('Migration section heading').fill('2.26.0')
  page.get_by_label('Documentation source URL').fill('https://github.com/Kong/charts/blob/main/charts/kong/UPGRADE.md#2260')
  with page.expect_navigation(wait_until='networkidle'):
   page.get_by_role('button',name='Prepare review brief').click()
  assert page.locator('.status').inner_text()=='REVIEW REQUIRED'
  uploaded=json.loads(page.locator('#report-json').input_value())
  assert uploaded['input_provenance']=='user_supplied_bytes_not_authenticated'
  assert uploaded['model_calls']>0 and uploaded['passages_omitted']==0
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.screenshot(path=str(out/'report-mobile.png'),full_page=True)
  mobile.close();browser.close()
  evidence={'actual_model':True,'test_double':False,'demo_route_status':200,'upload_route_status':200,'desktop_viewport':[1440,1000],'mobile_viewport':[390,844],'mobile_horizontal_overflow':False,'browser_errors':errors,'json_download_checked':True,'markdown_download_checked':True,'demo_report':actual_report,'upload_model_calls':uploaded['model_calls']}
  assert not errors
  (root/'verification/web-browser-2026-10-23.json').write_text(json.dumps(evidence,indent=2)+'\n')
  print(json.dumps({k:v for k,v in evidence.items() if k!='demo_report'},indent=2))
finally:
 server.terminate()
 try:server.wait(timeout=15)
 except subprocess.TimeoutExpired:server.kill()
 log.close()
