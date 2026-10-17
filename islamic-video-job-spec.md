# Islamic History Video — Job Spec (ready to launch once the Pexels API key is in)

**Status:** PREPARED 2026-10-17 ~11:30 PKT — waiting only on the user's Pexels API key (requested 10:58 PKT via secure link).
**User's request (10:55 PKT):** Islamic video through the AI Video Studio project, like the anime Urdu video, but with REAL video clips from Pexels + Urdu voiceover.

## Job parameters (feed straight into POST /api/jobs)
- topic: "Islamic Golden Age — jab musalmanon ne duniya ko ilm diya" (Urdu)
- category: "Islamic History"
- language: "Urdu"
- duration: 75
- style: "Documentary"
- voice: "ur-PK-AsadNeural" (same voice as the anime video the user approved)

## Pre-written Urdu narration (6 scenes, ~70s @125wpm — reviewed, respectful tone)

**Scene 1 (0–10s)** — Pexels: `mosque aerial`
آج سے تقریباً بارہ سو سال پہلے، جب دنیا کا بڑا حصہ اندھیرے میں ڈوبا تھا، بغداد میں علم کا ایک ایسا چراغ جلا، جس کی روشنی آج بھی ہماری زندگیوں کو منور کر رہی ہے۔

**Scene 2 (10–22s)** — Pexels: `ancient library manuscripts`
یہ تھا اسلام کا سنہری دور۔ بغداد کے بیت الحکمت میں دنیا بھر کے عالم جمع تھے، یونانی، فارسی اور ہندی کتابوں کا عربی میں ترجمہ ہو رہا تھا، اور علم کی نئی بنیادیں رکھی جا رہی تھیں۔

**Scene 3 (22–34s)** — Pexels: `herbal medicine apothecary`
ابنِ سینا نے طب کی وہ کتاب لکھی، القانون، جو یورپ کی یونیورسٹیوں میں چھ سو سال تک پڑھائی گئی۔

**Scene 4 (34–46s)** — Pexels: `astronomy stars night`
الخوارزمی نے الجبرا کی بنیاد رکھی — آج آپ کے فون کا ہر حساب اسی کے نام پر الگوردم کہلاتا ہے۔

**Scene 5 (46–58s)** — Pexels: `surgery medical history` (fallback: `laboratory vintage`)
ابنِ الہیثم نے روشنی کے اصول دریافت کیے، اور الزہراوی نے سرجری کے وہ اوزار بنائے جو آج بھی استعمال ہوتے ہیں۔

**Scene 6 (58–70s)** — Pexels: `kaaba makkah`
یہ ورثہ ہمیں یاد دلاتا ہے کہ علم ہی اصل طاقت ہے۔ ویڈیو پسند آئی تو شیئر ضرور کیجیے۔

## Verified ready (checked 2026-10-17 ~11:30 PKT)
- Footage agent (`backend/agents.py` `_pexels_connector_clip`) fetches via `custom.pexels/bin/pexels_fetch.py` using the stored connector credential — key never lands in files. Falls back to `PEXELS_API_KEY` env var.
- Network path OPEN: `api.pexels.com/videos/search` returns HTTP 401 without a key (expected) — connectivity proven; the ONLY blocker is the key itself.
- Urdu TTS voice `ur-PK-AsadNeural` and the "Islamic History" category tone are already wired in `agents.py`.
- Renderer outputs WhatsApp-friendly MP4 by default (faststart, yuv420p, AAC 44.1k stereo) — the fix from this morning.

## Notes for posting
- Pexels license: clips are free for commercial use, no attribution required — copyright-safe by design (fits the user's no-rip rules).
- When posting: AI-generated label ON (standing rule for every posted video).
- Posting account undecided — leave that choice with the user.
