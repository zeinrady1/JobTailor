# JobTailor

An AI-powered job application tool that searches across 6 major job boards, then uses Claude to tailor your resume and cover letter to each specific job description — generating ATS-optimized, 1-page PDFs ready to submit.

## What it does

- **Searches 6 job boards in parallel** — USAJobs, Adzuna, LinkedIn, Remotive, Jooble (aggregates Indeed, Glassdoor, ZipRecruiter + 140 more), and Google Jobs
- **Returns thousands of results** sorted by relevance to your search
- **Tailors your resume** — rewrites your bullet points and professional summary to match the job description's exact keywords
- **Writes a cover letter** — human-sounding, professional, tailored to the role and company
- **Generates PDFs** — ATS-optimized 1-page resume + cover letter, ready to submit
- **Works on phone and desktop** — fully responsive mobile UI

## Prerequisites

- Python 3.8 or higher
- [pip](https://pip.pypa.io/en/stable/)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/JobTailor.git
cd JobTailor
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Add your profile data

Open `resume_data.py` and replace the content with your own name, education, experience, projects, and skills. This is the data the AI uses to tailor your resume — the more detail you add, the better the output.

### 5. Configure your API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Then open `.env` and fill in each value:

```
CONTACT_EMAIL=your.email@example.com
CONTACT_PHONE=(000) 000-0000
ANTHROPIC_API_KEY=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
USAJOBS_API_KEY=...
JOOBLE_API_KEY=...
SERPAPI_KEY=...
```

### Getting your API keys

| Key | Where to get it | Free tier |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Pay per use (~$0.03/resume) |
| `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | [developer.adzuna.com](https://developer.adzuna.com) | Free |
| `USAJOBS_API_KEY` | [developer.usajobs.gov](https://developer.usajobs.gov) | Free |
| `JOOBLE_API_KEY` | [jooble.org/api/registered](https://jooble.org/api/registered) | Free |
| `SERPAPI_KEY` | [serpapi.com](https://serpapi.com) | 100 searches/month free |

> The app works with any combination of keys — sources with missing keys are simply skipped. At minimum, add `ANTHROPIC_API_KEY` for AI tailoring and at least one job board key.

### 6. Start the server

```bash
venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

To access from your phone (on the same Wi-Fi), find your local IP:

```bash
ipconfig getifaddr en0   # Mac
ipconfig                 # Windows (look for IPv4)
```

Then open `http://<your-ip>:8000` on your phone.

## Usage

### Searching for jobs
1. Type a job title or keyword in the **Find Jobs** tab
2. Optionally add a location
3. Hit Search — results from all 6 sources appear ranked by relevance

### Tailoring your resume
1. Click any job from the results list
2. Hit **Tailor Resume** — Claude rewrites your bullets and summary to match that job's keywords
3. Download your 1-page resume PDF and cover letter PDF

### Manual job input
Use the **Paste Job** tab to paste a job description directly, or enter a URL for Claude to fetch and parse automatically.

## Project structure

```
JobTailor/
├── main.py          # FastAPI server and API routes
├── jobs.py          # Job board search (all 6 sources)
├── tailor.py        # Claude AI resume/cover letter tailoring + PDF HTML generation
├── pdf_gen.py       # Playwright HTML → PDF conversion
├── resume_data.py   # Your profile data (education, experience, projects, skills)
├── static/
│   └── index.html   # Frontend UI
├── requirements.txt
├── .env.example     # Template for your API keys
└── .env             # Your actual keys (never committed)
```

## Cost estimate

Each resume + cover letter generation uses approximately:
- ~3,000 input tokens + ~1,500 output tokens with Claude Sonnet
- **~$0.03 per application** (3 cents)

With prompt caching enabled automatically by Anthropic, repeated searches cost even less (~2 cents/application).

## Notes

- The `outputs/` folder holds generated PDFs and is not tracked by git
- LinkedIn results may vary as their guest API has rate limits
- SerpAPI free tier allows 100 Google Jobs searches/month (each search uses ~10 calls)
- USAJobs only returns government/federal positions
