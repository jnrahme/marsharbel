from kokoro_onnx import Kokoro
import soundfile as sf,pathlib,json,hashlib
p=pathlib.Path('/downloads/daily-rosary-tuesday');d=p/'new-takes';d.mkdir(exist_ok=True);k=Kokoro('/downloads/rosary-recovered/onnx/kokoro-v1.0.int8.onnx','/downloads/rosary-recovered/onnx/voices-v1.0.bin');out=[]
for name,s in json.load(open(p/'new-recording-plan.json')).items():
 f=d/(name+'.wav')
 if not f.exists():
  a,sr=k.create(s,voice='am_michael',speed=.94,lang='en-us');sf.write(f,a,sr)
 a,sr=sf.read(f);out.append({'key':name,'text':s,'spoken_text_sha256':hashlib.sha256(s.encode()).hexdigest(),'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'duration':len(a)/sr,'sample_rate':sr,'voice':'am_michael','speed':.94});print(name,len(a)/sr,flush=True)
 (p/'new-takes-manifest.json').write_text(json.dumps(out,indent=2))
