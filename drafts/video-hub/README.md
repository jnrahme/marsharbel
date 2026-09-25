# Review-gated videos hub draft

The video is NOT published. This folder is not routed by the website. The owner
must review the private MP4 before the source file moves into public /media/.

Private review copy (owner's Drive, not shared):
https://drive.google.com/file/d/1WohjQvh9ExAjtvQc3nCeVrmiQTllaZaI/view?usp=drivesdk&authuser=jnrahme%40gmail.com

The review cut uses all 27 English narration clips from /story (already on the
site), 27 matching illustrated storybook assets already in the repo, and slow zoom/pans.
It is an illustrated story, not documentary footage of Annaya or a clip from
any feature film. Duration 720.865 seconds, 960 x 540, 12,324,513 bytes.

Before publication: confirm rights to reuse the storybook illustrations and
voice clips in an assembled video. Repo presence is not a license.

After visual review and provenance confirmation:
1. Copy the reviewed MP4 to media/video/saint-charbel-illustrated-story.mp4,
   and make a 16:9 poster with accurate illustrated-story labeling.
2. Build /videos with a native video element (controls, preload=metadata,
   poster), explicit illustrated-story caption, link to /story, and separate
   /saint-charbel-movie link that does not imply the 2026 film is ours.
3. Add a correctly timed caption track and a text transcript; do not infer
   exact word timing from chapter durations.
4. Add VideoObject with a real uploadDate, contentUrl, thumbnailUrl,
   duration PT12M1S, and metadata matching the published resource.
5. Add Videos to the shared Story dropdown, sync generated nav, regenerate
   SEO tags and sitemap lastmod, and verify route, media, schema and playback.
6. Test at mobile/desktop, bandwidth and reduced-motion settings. Preserve
   existing storybook and screen-reader flows; no autoplay.

The build script at scripts/video/build-story-video.py reproduces the MP4 from
existing repo audio/images, but remains outside public routing. Do not run it
as part of CI or deployment.

At review time, chapter headings and approximate start timestamps are available
as a separate list in /downloads/saint-charbel-story-chapters.txt (review artifact,
not public captions). A chapter title track is not a substitute for spoken-word
captions. The site source is /story; full transcript export should strip
storybook UI controls and preserve the exact spoken 27 scene texts.
