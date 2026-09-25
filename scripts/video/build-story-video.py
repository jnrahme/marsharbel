#!/usr/bin/env python3
"""Assemble the site's existing 27 story illustrations and narration clips.

This creates a private review render, not a publication. Rights to reuse
the existing assets in a compiled video must be confirmed before release.
Source files and captions
are read from the site's /story sequence; no external footage is fetched.
"""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/downloads/saint-charbel-story-review.mp4')
WORK=Path('/tmp/charbel-video-build');WORK.mkdir(exist_ok=True)
s=ROOT.joinpath('storybook.js').read_text().split('    en: [',1)[1].split('    ar: [',1)[0]
titles=re.findall(r"\btitle: '([^']+)'",s)
illustrations=re.findall(r"illustration: '(\./media/storybook/images/[^']+)'",s)
assert len(titles)==len(illustrations)==27,(len(titles),len(illustrations))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
segments=[]
for i,(title,image) in enumerate(zip(titles,illustrations),1):
    audio=ROOT/f'media/storybook/en/page-{i:02}.mp3'
    img=ROOT/image[2:]
    assert audio.exists() and img.exists()
    duration=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(audio)]))['format']['duration'])
    textfile=WORK/f'title-{i:02}.txt';textfile.write_text(title+'\n')
    seg=WORK/f'scene-{i:02}.mp4'
    if not seg.exists() or '--rebuild' in sys.argv:
        filter_=f"[0:v]scale=1000:563:force_original_aspect_ratio=increase,crop=1000:563,zoompan=z='min(zoom+0.00035,1.12)':d=1:s=960x540:fps=12,format=yuv420p,fade=t=in:st=0:d=0.35,fade=t=out:st={max(0,duration-.4):.2f}:d=0.4,drawtext=fontfile={font}:textfile={textfile}:fontsize=23:fontcolor=white:x=35:y=h-78:box=1:boxcolor=black@0.58:boxborderw=12:enable='lt(t,5)'[v]"
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-loop','1','-framerate','12','-i',str(img),'-i',str(audio),'-filter_complex',filter_,'-map','[v]','-map','1:a','-t',f'{duration:.3f}','-c:v','libx264','-preset','veryfast','-crf','27','-r','12','-c:a','aac','-b:a','72k','-movflags','+faststart',str(seg),'-y']
        subprocess.run(cmd,check=True)
    segments.append(seg)
    print(f'chapter {i:02}/27: {duration:.1f}s {title}',flush=True)
manifest=WORK/'manifest.txt'
manifest.write_text(''.join("file '"+str(p)+"'\n" for p in segments))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart',str(OUT),'-y'],check=True)
print(f'Review video: {OUT}',flush=True)
