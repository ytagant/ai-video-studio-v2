# AI Video Studio — Website Deploy Guide

**Kya hai:** Poora AI Video Studio ab ek website hai. Ek Docker container
mein sab kuch: video banane wala backend + website + video player.
Aap sirf site kholenge, category/topic select karenge, aur video wahin
player mein dekh sakenge (saath mein Download MP4 button bhi hai).

**Blogger par NAHI chal sakta** — Blogger sirf static pages dikhata hai,
video render karne wala backend wahan nahi chalta. Neeche 2 asaan raaste hain.

---

## Step 0 — Gemini API key (FREE, 2 minute, sirf ek dafa)

AI script likhne ke liye chahiye. Bina iske bhi kaam chalega (template
writer), lekin AI script behtar hogi.

1. Apne phone par kholein: **https://aistudio.google.com/apikey**
2. Google account se sign in karein
3. **"Create API key"** dabayein → key copy kar lein

Ye key kisi ko na bhejein — sirf neeche deploy steps mein use hogi.

---

## Raasta 1 — Hugging Face Spaces (FREE)

1. **huggingface.co** par free account banayein
2. New **Space** banayein → **Docker** type select karein → **Blank** template
3. Is project ka poora folder (`video-studio`) Space mein upload karein
   (Dockerfile root mein hai — wahi chahiye)
4. Space **Settings → Variables and secrets** mein jayein:
   - **New secret** → naam `GEMINI_API_KEY`, value = upar wali key
5. Space khud build ho kar **Running** ho jayega (5–10 min)
6. Site kholیں — bas!

> Note: Free Space 48 ghante idle rehne par so jata hai, kholne par
> dobara jaag jata hai. Lambi videos par thoda slow ho sakta hai.

## Raasta 2 — VPS (tez tareen, ~Rs 1200/month)

Pakistan mein **Hostinger.pk** Easypaisa/JazzCash leta hai.

1. Hostinger se chhota VPS lein (Ubuntu)
2. SSH karke ye commands chalayein:

```bash
# Docker install
curl -fsSL https://get.docker.com | sh

# project copy karein (apne computer se upload karein ya git se)
cd video-studio
cp backend/.env.example backend/.env
nano backend/.env        # GEMINI_API_KEY= wali line mein key paste karein

# chalao
docker compose up -d --build
```

3. Browser mein `http://AAPKE-VPS-KA-IP:7860` kholein — website taiyaar!

Domain lagana ho to Cloudflare se free mein lag sakta hai.

---

## Website par kya milega

- **8 categories** (Anime, Cartoon, Documentary, Horror, Islamic History,
  Kids, Motivational, Tech/Science) — image walay buttons
- **Video length:** 1m / 2m / 3m / 5m / 10m + slider
- **Language:** Urdu / Hindi / English (voiceover ke saath)
- **Generate** dabayein → 6 agents live progress dikhayenge →
  video **player mein wahin chalegi** + Download MP4 button
- **AI Re-edit box:** "make it scarier" likhein, video dobara ban jayegi

## Keys ka khulasa

| Key | Zaroori? | Muft? | Kahan se |
|-----|----------|-------|----------|
| GEMINI_API_KEY | Behtar script ke liye (warna template) | Haan | aistudio.google.com/apikey |
| PEXELS_API_KEY | Nahi (Wikimedia Commons bina key ke chalta hai) | Haan | pexels.com/api |
| PIXABAY_API_KEY | Nahi | Haan | pixabay.com/api/docs |

**Aapko sirf Gemini key nikalni hai** — baqi sab pehle se laga hua hai.
