import unittest,tempfile,json,re,ssl,sys,urllib.parse
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from radar import *
from app import app
class RadarTests(unittest.TestCase):
 def test_normalization_and_dedupe(self): self.assertEqual(parse_requirements('Foo_Bar==1.0\nfoo-bar==1.1 #ignored'),[('foo-bar','1.0')])
 def test_rejects_unsafe_requirements(self):
  for s in ['-r secrets.txt','git+https://x','requests>=1','foo @ https://x','x; os_name=="nt"','']:
   with self.assertRaises(RadarError):parse_requirements(s)
 def test_max_packages(self):
  with self.assertRaises(RadarError):parse_requirements('\n'.join('p'+str(i) for i in range(6)))
 def test_query_keeps_pin(self):self.assertIn('1.10.0',queries('pydantic','1.10.0')[0])
 def test_evidence_security_dedupe(self):
  p={'query':'q','retrieved_at':'t','results':[{'link':'javascript:alert(1)'},{'link':'https://docs.pydantic.dev/x','snippet':'migration'},{'link':'https://docs.pydantic.dev/x#copy'}]}
  r=evidence_rows(p,'pydantic','1');self.assertEqual(len(r),1);self.assertEqual(r[0]['status'],'UNVERIFIED: search snippet only')
 def test_cache_no_key_or_metadata(self):
  class R:
   def __enter__(self):return self
   def __exit__(self,*x):pass
   def read(self):return json.dumps({'organic_results':[{'title':'test','link':'https://x.test','snippet':'ok'}],'search_metadata':{'json_endpoint':'SECRET'}}).encode()
  with tempfile.TemporaryDirectory() as d,patch('urllib.request.urlopen',return_value=R()) as call:
   quota={'used':0};p,c=fetch_search('q','DO_NOT_STORE',d,quota);self.assertFalse(c)
   p,c=fetch_search('q','DO_NOT_STORE',d,quota);self.assertTrue(c);self.assertEqual(call.call_count,1)
   text=next(Path(d).glob('*.json')).read_text();self.assertNotIn('DO_NOT_STORE',text);self.assertNotIn('SECRET',text)
 def test_budget(self):
  with tempfile.TemporaryDirectory() as d, self.assertRaises(RadarError):fetch_search('q','x',d,{'used':20})
 def test_error_is_redacted(self):
  with tempfile.TemporaryDirectory() as d,patch('urllib.request.urlopen',side_effect=Exception('SECRET')),self.assertRaises(RadarError) as e:fetch_search('q','SECRET',d,{'used':0})
  self.assertNotIn('SECRET',str(e.exception))
 def test_invalid_api_result(self):
  class R:
   def __enter__(self):return self
   def __exit__(self,*x):pass
   def read(self):return b'{"error":"bad key"}'
  with tempfile.TemporaryDirectory() as d,patch('urllib.request.urlopen',return_value=R()),self.assertRaises(RadarError):fetch_search('q','key',d,{'used':0})
 def test_fixture_and_export(self):
  c=app.test_client();page=c.get('/').text;token=re.search('name="token" value="([^"]+)"',page)[1]
  result=c.post('/',data={'token':token,'requirements':'pydantic==1.10.0','mode':'fixture'})
  self.assertEqual(result.status_code,200);self.assertIn('SYNTHETIC FIXTURE',result.text)
  link=re.search('href="(/export/[^"]+)"',result.text)[1];self.assertIn('SYNTHETIC FIXTURE',c.get(link).text)
 def test_csrf(self):self.assertIn('Invalid form token',app.test_client().post('/',data={'requirements':'x'}).text)
 def test_html_escaped(self):
  c=app.test_client();page=c.get('/').text;token=re.search('name="token" value="([^"]+)"',page)[1]
  result=c.post('/',data={'token':token,'requirements':'<script>alert(1)</script>'}).text
  self.assertNotIn('<script>alert(1)</script>',result)
 def test_query_strings_stay_cache_compatible(self):
  self.assertEqual(queries('pydantic','1.10.0'),['site:docs.pydantic.dev pydantic 1.10.0 migration deprecation','pydantic 1.10.0 security advisory release notes'])
 def test_official_host_outranks_third_party_and_repo(self):
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'Blog','link':'https://blog.example/post','snippet':'pydantic migration notes'},
   {'title':'Issue','link':'https://github.com/pydantic/pydantic/issues/1','snippet':'question'},
   {'title':'Docs','link':'https://docs.pydantic.dev/migration','snippet':'guide'}]}
  rows=finalize_evidence(evidence_rows(payload,'pydantic','1.10.0'))
  self.assertEqual([r['source_category'] for r in rows],['Package documentation','Package repository','Other source'])
  self.assertTrue(all(r['status']=='UNVERIFIED: search snippet only' for r in rows))
  self.assertTrue(all(r['applicability']=='Pin applicability: not established' for r in rows))
 def test_spoofed_hostname_is_not_official(self):
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'Spoof','link':'https://docs.pydantic.dev.evil.test/guide','snippet':'upgrade table'},
   {'title':'Hyphen','link':'https://docs-pydantic.dev/guide','snippet':'upgrade table'},
   {'title':'Lookalike','link':'https://notpydantic.dev/guide','snippet':'upgrade table'},
   {'title':'Real','link':'https://docs.pydantic.dev/guide','snippet':'upgrade table'}]}
  rows=finalize_evidence(evidence_rows(payload,'pydantic','1.10.0'))
  categories={r['url']:r['source_category'] for r in rows}
  self.assertEqual(categories['https://docs.pydantic.dev/guide'],'Package documentation')
  self.assertEqual(categories['https://docs.pydantic.dev.evil.test/guide'],'Other source')
  self.assertEqual(categories['https://docs-pydantic.dev/guide'],'Other source')
  self.assertEqual(categories['https://notpydantic.dev/guide'],'Other source')
  self.assertEqual(rows[0]['url'],'https://docs.pydantic.dev/guide')
 def test_subdomain_of_docs_host_is_documentation(self):
  payload={'query':'q','retrieved_at':'t','results':[{'title':'Nested','link':'https://api.docs.pydantic.dev/guide','snippet':'guide'}]}
  rows=evidence_rows(payload,'pydantic','1')
  self.assertEqual(rows[0]['source_category'],'Package documentation')
 def test_stable_order_within_tier(self):
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'A','link':'https://a.example/pydantic','snippet':'pydantic notes'},
   {'title':'B','link':'https://b.example/pydantic','snippet':'pydantic notes'},
   {'title':'D1','link':'https://docs.pydantic.dev/1','snippet':'one'},
   {'title':'D2','link':'https://docs.pydantic.dev/2','snippet':'two'}]}
  rows=finalize_evidence(evidence_rows(payload,'pydantic','1'))
  self.assertEqual([r['title'] for r in rows],['D1','D2','A','B'])
 def test_unmatched_stays_visible_below(self):
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'Noise','link':'https://example.invalid/noise','snippet':'weekly notes'},
   {'title':'Hit','link':'https://blog.example/pydantic','snippet':'pydantic migration'}]}
  rows=finalize_evidence(evidence_rows(payload,'pydantic','1.10.0'))
  self.assertEqual([r['relevance'] for r in rows],['package-matched lead','unmatched lead'])
  self.assertEqual(rows[1]['url'],'https://example.invalid/noise')
 def test_both_queries_keep_snippets_and_timestamps(self):
  link='https://docs.pydantic.dev/migration'
  first=evidence_rows({'query':'q-one','retrieved_at':'2026-01-01T00:00:00+00:00','results':[{'title':'First title','link':link,'snippet':'alpha snippet'}]},'pydantic','1.10.0',cached=True)
  second=evidence_rows({'query':'q-two','retrieved_at':'2026-02-02T00:00:00+00:00','results':[{'title':'Second title','link':link+'?utm_source=ad','snippet':'beta snippet'}]},'pydantic','1.10.0',cached=False)
  rows=finalize_evidence(first+second)
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]['title'],'First title')
  self.assertEqual(rows[0]['url'],link)
  self.assertEqual([(p['query'],p['snippet'],p['retrieved_at'],p['cached']) for p in rows[0]['provenance']],[('q-one','alpha snippet','2026-01-01T00:00:00+00:00',True),('q-two','beta snippet','2026-02-02T00:00:00+00:00',False)])
 def test_tracking_variants_merge_and_meaningful_queries_do_not(self):
  base='https://docs.pydantic.dev/x'
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'T','link':base+'?utm_source=a&utm_medium=b&version=1&id=9&page=2&q=migration','snippet':'s'},
   {'title':'T','link':base+'?gclid=1&fbclid=2&msclkid=3&page=2&q=migration&id=9&version=1','snippet':'s'},
   {'title':'T','link':base+'?version=1&id=9&page=2&q=migration#frag','snippet':'s'},
   {'title':'T','link':base+'?version=2&id=9&page=2&q=migration','snippet':'s'},
   {'title':'T','link':base+'?version=1&id=8&page=2&q=migration','snippet':'s'},
   {'title':'T','link':base+'?version=1&id=9&page=3&q=migration','snippet':'s'},
   {'title':'T','link':base+'?version=1&id=9&page=2&q=security','snippet':'s'},
   {'title':'T','link':'http://docs.pydantic.dev/x?version=1&id=9&page=2&q=migration','snippet':'s'},
   {'title':'T','link':'https://www.docs.pydantic.dev/x?version=1&id=9&page=2&q=migration','snippet':'s'}]}
  rows=evidence_rows(payload,'pydantic','1')
  self.assertEqual(len(rows),7)
  self.assertEqual(rows[0]['canonical'],base+'?id=9&page=2&q=migration&version=1')
  self.assertEqual(rows[0]['url'],base+'?utm_source=a&utm_medium=b&version=1&id=9&page=2&q=migration')
 def test_repeated_query_params_retained(self):
  payload={'query':'q','retrieved_at':'t','results':[
   {'title':'R','link':'https://example.com/a?id=1&id=2','snippet':'pydantic'},
   {'title':'R','link':'https://example.com/a?id=2&id=1','snippet':'pydantic'},
   {'title':'R','link':'https://example.com/a?id=1','snippet':'pydantic'}]}
  rows=evidence_rows(payload,'pydantic','1')
  self.assertEqual(len(rows),2)
  pairs=urllib.parse.parse_qsl(urllib.parse.urlsplit(rows[0]['canonical']).query, keep_blank_values=True)
  self.assertEqual(pairs,[('id','1'),('id','2')])
 def test_packages_stay_separate(self):
  payload={'query':'q','retrieved_at':'t','results':[{'title':'Same','link':'https://example.com/a','snippet':'shared'}]}
  rows=finalize_evidence(evidence_rows(payload,'pydantic','1')+evidence_rows(payload,'fastapi','1'))
  self.assertEqual(sorted(r['package'] for r in rows),['fastapi','pydantic'])
 def test_pin_in_snippet_does_not_establish_applicability(self):
  payload={'query':'q','retrieved_at':'t','results':[{'title':'Note','link':'https://example.com/n','snippet':'discussed 1.10.0 today'}]}
  row=evidence_rows(payload,'pydantic','1.10.0')[0]
  self.assertEqual(row['relevance'],'needs relevance review')
  self.assertEqual(row['applicability'],'Pin applicability: not established')
 def test_export_includes_every_query(self):
  link='https://example.com/a'
  rows=finalize_evidence(evidence_rows({'query':'query-alpha','retrieved_at':'t1','results':[{'title':'A','link':link,'snippet':'one'}]},'pydantic','1.10.0')+evidence_rows({'query':'query-beta','retrieved_at':'t2','results':[{'title':'A','link':link,'snippet':'two'}]},'pydantic','1.10.0'))
  text=export_markdown(rows)
  self.assertIn('query-alpha',text);self.assertIn('query-beta',text)
  self.assertIn('one',text);self.assertIn('two',text)
  self.assertIn('t1',text);self.assertIn('t2',text)
 def test_fixture_export_lists_both_queries_and_unmatched(self):
  c=app.test_client();page=c.get('/').text;token=re.search('name="token" value="([^"]+)"',page)[1]
  result=c.post('/',data={'token':token,'requirements':'pydantic==1.10.0','mode':'fixture'})
  self.assertIn('SYNTHETIC FIXTURE',result.text);self.assertIn('unmatched leads',result.text)
  self.assertIn('Pin applicability: not established',result.text)
  body=c.get(re.search('href="(/export/[^"]+)"',result.text)[1]).text
  for q in queries('pydantic','1.10.0'): self.assertIn(q,body)
  self.assertIn('SYNTHETIC FIXTURE',body);self.assertIn('Unmatched leads',body)
 def test_legacy_cache_shape_readable(self):
  payload={'query':'legacy','retrieved_at':'2020-01-01T00:00:00+00:00','results':[{'title':'Old','link':'https://example.com/old','snippet':'pydantic','date':'Jan 1'}]}
  row=evidence_rows(payload,'pydantic','1',cached=True)[0]
  self.assertEqual(row['status'],'UNVERIFIED: search snippet only')
  self.assertEqual(row['provenance'][0]['retrieved_at'],'2020-01-01T00:00:00+00:00')
  self.assertTrue(row['provenance'][0]['cached'])
 def test_tls_verification_enabled(self):
  class R:
   def __enter__(self):return self
   def __exit__(self,*x):pass
   def read(self):return json.dumps({'organic_results':[{'title':'t','link':'https://x.test','snippet':'ok'}]}).encode()
  with tempfile.TemporaryDirectory() as d,patch('urllib.request.urlopen',return_value=R()) as call:
   fetch_search('tls-check','k',d,{'used':0})
  ctx=call.call_args.kwargs['context']
  self.assertEqual(ctx.verify_mode,ssl.CERT_REQUIRED)
  self.assertTrue(ctx.check_hostname)
  self.assertGreater(ctx.cert_store_stats().get('x509_ca',0),0)
if __name__=='__main__':unittest.main()
