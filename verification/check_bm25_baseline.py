"""Exploratory BM25 baseline added after the frozen model comparison.

This is not a new independent test or a tuned retrieval system. It makes the
stronger non-model comparison explicit instead of claiming token overlap is
all lexical search can do. No parameters are selected using these labels.
"""
import collections,hashlib,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from upgrade_brief import build_brief,read_checked
from review_plan import select_range

def tokens(text): return re.findall(r'[a-z0-9_]+',text.lower())

def main():
 case=json.loads((ROOT/'brief-cases/kong-range.json').read_text())
 contract=json.loads((ROOT/'verification/range-evaluation-contract.json').read_text())
 passages,_=select_range(read_checked(ROOT,case['notes'],200000),case['from_chart'],case['to_chart'])
 queries=build_brief(case,ROOT)['reading_tasks']
 docs=[tokens(p['text']) for p in passages]
 avg=sum(map(len,docs))/len(docs)
 df=collections.Counter(t for doc in docs for t in set(doc))
 result=[]
 for task in queries:
  values=[]
  for p,doc in zip(passages,docs):
   freq=collections.Counter(doc);score=0.0
   for token in set(tokens(task['query'])):
    count=freq[token]
    if not count: continue
    idf=math.log(1+(len(docs)-df[token]+0.5)/(df[token]+0.5))
    score+=idf*count*2.2/(count+1.2*(1-0.75+0.75*len(doc)/avg))
   values.append({'id':p['id'],'score':round(score,6)})
  values.sort(key=lambda x:x['score'],reverse=True)
  expected=contract['expected_prerequisite_passage_by_field'][task['field']]
  result.append({'field':task['field'],'ranking':values,'expected_prerequisite':expected,'hit_at_2':expected in [x['id'] for x in values[:2]]})
 output={'kind':'post_hoc_lexical_baseline_not_independent_evaluation','parameters':{'k1':1.2,'b':0.75,'tokenizer':'lowercase alphanumeric/underscore; no stemming or parameter search'},'frozen_contract_sha256':hashlib.sha256((ROOT/'verification/range-evaluation-contract.json').read_bytes()).hexdigest(),'prerequisites_hit_at_2':sum(x['hit_at_2'] for x in result),'prerequisites_total':len(result),'results':result,'scope':'Same one controlled case and author labels. Added after seeing the frozen comparison; not proof of general model or lexical superiority.'}
 (ROOT/'verification/range-bm25-posthoc.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'hits':output['prerequisites_hit_at_2'],'total':len(result),'top2':{x['field']:[y['id'] for y in x['ranking'][:2]] for x in result}},indent=2))
if __name__=='__main__': main()
