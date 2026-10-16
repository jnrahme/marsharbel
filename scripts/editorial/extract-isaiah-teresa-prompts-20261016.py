from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[2]/'docs/editorial/isaiah-teresa-20261016';j=json.loads((r/'FINAL-PROMPT-PACK.json').read_text());out=r/'prompt-payloads';out.mkdir(exist_ok=True);manifest={}
for k,v in j.items():
 block=v['prompt'];assert block.count('Actual final prompt:\n')==1 and block.count('\n\nReference basis and limit:')==1
 payload=block.split('Actual final prompt:\n',1)[1].split('\n\nReference basis and limit:',1)[0].strip()+'\n'
 assert 'https://' not in payload and 'Accepted page text' not in payload and 'Bindings:' not in payload
 f=out/(k+'.txt');f.write_text(payload)
 manifest[k]={key:val for key,val in v.items() if key!='prompt'}|{'payload_file':'prompt-payloads/'+f.name,'payload_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'extraction_method':'UTF8 Actual final prompt: newline delimiter through before double-newline Reference basis and limit:, strip outer whitespace, append one LF; never send review block or page text','external_image_inputs':[]}
(r/'PROMPT-PAYLOAD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('PAYLOADS',len(manifest),'MD',hashlib.sha256((r/'FINAL-PROMPT-PACK.md').read_bytes()).hexdigest(),'JSON',hashlib.sha256((r/'FINAL-PROMPT-PACK.json').read_bytes()).hexdigest(),'MANIFEST',hashlib.sha256((r/'PROMPT-PAYLOAD-MANIFEST.json').read_bytes()).hexdigest())
