# 📸 Visual E-Commerce Price Matcher

Upload a product photo → it reverse-image-searches the web via Google Lens (through SerpApi)
and shows matching retail listings sorted from cheapest to most expensive.

## How it works
1. **Streamlit** gives you the upload UI.
2. **Imgur** temporarily hosts your uploaded image so it has a public URL (Google Lens needs a URL, not a raw file).
3. **SerpApi's Google Lens engine** runs the reverse image search against that URL and returns visual shopping matches.
4. The app parses out price/source/link per match, strips currency symbols, and sorts low → high.

## Setup

### 1. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get your API keys
- **SerpApi**: sign up free at https://serpapi.com, copy your key from the dashboard.
- **Imgur**: register at https://api.imgur.com/oauth2/addclient → choose "Anonymous usage without user authorization" → copy the Client ID.

### 4. Add your keys
Copy `.env.example` to `.env` and fill in your real keys:
```bash
cp .env.example .env
```
```
SERPAPI_KEY=your_actual_key
IMGUR_CLIENT_ID=your_actual_client_id
```
**Never commit `.env` to git** — add it to `.gitignore`.

### 5. Run it
```bash
streamlit run app.py
```
Opens at http://localhost:8501. Upload a clear photo of a recognizable product (shoes, electronics, etc.) and click **Find Best Prices**.

## Notes / things to know before you rely on this
- **SerpApi free tier** is limited (100 searches/month as of writing) — fine for testing, not for production traffic. Check current limits on their pricing page since these change.
- **Imgur anonymous uploads** are rate-limited per IP and images may get auto-deleted after inactivity — it's a *temporary* relay, not real storage. For a production app you'd swap this for S3/Cloudinary/etc.
- The price parser assumes the currency string has digits + a decimal point (e.g. `$29.99`, `₹2,500`). It strips everything else, so something like `"Free"` or `"Contact for price"` is just skipped (handled by the `try/except`).
- I fixed one bug from the original spec: `response.status_with_code` isn't a real `requests` attribute — it's `response.status_code`. The version in `app.py` already has this corrected, so uploads won't silently crash.

## Possible next steps
- Cache results so repeat searches on the same image don't burn API quota.
- Add a currency normalizer (right now `$` and `₹` prices get sorted together as raw numbers, which isn't a fair price comparison across currencies).
- Swap Imgur for a storage bucket you control if you outgrow the free tier.
