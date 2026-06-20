import json, re
from anthropic import AsyncAnthropic
from resume_data import RESUME

client = AsyncAnthropic()

# ── Shared CSS — identical for both portfolio and tailored output ──
_CSS = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: Arial, sans-serif;
    font-size: 8.5pt;
    color: #000;
    background: #fff;
    padding: 0.15in 0.5in;
    max-width: 8.5in;
    margin: 0 auto;
  }
  h1 { text-align: center; font-size: 15pt; font-weight: bold; margin-bottom: 2px; }
  .contact { text-align: center; font-size: 8pt; margin-bottom: 3px; }
  .contact a { color: #000; text-decoration: none; }
  .section-title {
    font-size: 8.8pt; font-weight: bold; text-transform: uppercase;
    border-bottom: 1px solid #000; padding-bottom: 1px;
    margin-top: 3px; margin-bottom: 2px; letter-spacing: 0.2px;
  }
  .summary { font-size: 8.2pt; line-height: 1.22; margin-bottom: 1px; }
  .entry { margin-bottom: 2px; }
  .entry-header { display: flex; justify-content: space-between; align-items: baseline; }
  .entry-title { font-weight: bold; font-size: 8.5pt; }
  .entry-date { font-size: 8pt; white-space: nowrap; padding-left: 8px; }
  .entry-sub { font-style: italic; font-size: 8pt; margin-bottom: 0px; }
  ul { margin-left: 12px; margin-top: 0px; }
  ul li { font-size: 8pt; margin-bottom: 0px; line-height: 1.17; }
  .skills-line { font-size: 8pt; margin-bottom: 1px; line-height: 1.22; }
  @media print {
    body { padding: 0.15in 0.46in; }
    @page { size: letter; margin: 0; }
  }
"""

SYSTEM_PROMPT = f"""You are an expert ATS resume tailor. You rewrite Zein Rady's resume to match a specific job description.

ZEIN'S PROFILE:
{json.dumps(RESUME, indent=2)}

══════════════════════════════════════════
FIXED RESUME STRUCTURE — NEVER change which entries appear or their order.
Only rewrite the bullet text to weave in JD keywords naturally.
This exact structure keeps the resume exactly 1 page.
══════════════════════════════════════════

EXPERIENCE — always exactly these 3 entries, this order:
1. title: "Treasurer"  |  org: "Vertical Flight Society (VFS) @ UCSD"  |  date: "Oct 2025 – Jun 2026"
   → write EXACTLY 3 bullets
2. title: "Behavioral Health Technician"  |  org: "Nyansa Learning Corporation"  |  date: "Jun 2025 – Sep 2025"
   → write EXACTLY 3 bullets
3. title: "Lead Structural Designer"  |  org: "Freelance Engineering Project"  |  date: "Jun 2025 – Aug 2025"
   → write EXACTLY 4 bullets

PROJECTS — always exactly these 4 entries, this order:
1. title: "Batch Least-Squares Orbit Determination"
   subtitle: "MAE 182 – Spacecraft GNC, UCSD | Apr 2026 – Jun 2026"
   → write EXACTLY 3 bullets
2. title: "Sequential Orbit Determination (Extended Kalman Filter)"
   subtitle: "MAE 182 – Spacecraft GNC, UCSD | Final Exam Project, Jun 2026"
   → write EXACTLY 3 bullets
3. title: "High-Powered Rocket – Proxima (RPL @ UCSD)"
   subtitle: "Lead Design Engineer | Oct 2024 – Jun 2025"
   → write EXACTLY 2 bullets
4. title: "Autonomous Quadcopter – DBVF @ UCSD"
   subtitle: "Embedded Systems Team Member | Nov 2024 – Jun 2025"
   → write EXACTLY 2 bullets

══════════════════════════════════════════
ATS KEYWORD RULES
══════════════════════════════════════════
- Extract 8–12 top keywords from the JD using exact verbatim phrases
- Keyword placement priority: Professional Summary FIRST → bullet points → skills
- Professional Summary: 2–3 sentences naming the exact target role and using 3–5 JD keywords verbatim
- Bullet formula: Action verb + specific tool or method + concrete or quantified result
- NEVER fabricate skills, tools, metrics, or achievements — only what Zein actually did
- Every bullet must be factually grounded in Zein's real experience

══════════════════════════════════════════
COVER LETTER RULES
══════════════════════════════════════════
- Write in a natural, warm, human voice — it must read like a real person wrote it
- Stay professional but conversational — not stiff or robotic
- DO NOT use dashes, hyphens as punctuation, or em dashes anywhere (no -, –, —). Rephrase using commas or rewrite the sentence.
- 3 paragraphs separated by \\n\\n:
  Para 1: Engaging opening that names the exact role and company and shows genuine enthusiasm
  Para 2: 2–3 specific accomplishments from experience or projects directly relevant to this role
  Para 3: Why this company or team specifically excites you, plus a clear and confident call to action

══════════════════════════════════════════

Return ONLY valid JSON, no markdown, no extra text:
{{
  "summary": "2–3 sentence professional summary tailored to this specific role",
  "keywords_matched": ["keyword1", "keyword2"],
  "experience": [
    {{
      "title": "exact title from above",
      "org": "exact org from above",
      "date": "exact date from above",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"]
    }}
  ],
  "projects": [
    {{
      "title": "exact title from above",
      "subtitle": "exact subtitle from above",
      "bullets": ["bullet 1", "bullet 2"]
    }}
  ],
  "cover_letter": "paragraph 1\\n\\nparagraph 2\\n\\nparagraph 3"
}}"""


async def tailor_resume(job_description: str, job_title: str = "", company: str = "") -> dict:
    context = f"Job Title: {job_title}\nCompany: {company}\n\n" if job_title or company else ""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{context}Job Description:\n{job_description}"}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)
    resume_html = build_resume_html(data)
    cover_html = build_cover_letter_html(data, job_title, company)

    return {
        "resume_html": resume_html,
        "cover_letter_html": cover_html,
        "keywords": data.get("keywords_matched", []),
        "cover_letter_text": data.get("cover_letter", ""),
    }


def _bullets_html(bullets: list) -> str:
    return "".join(f"<li>{b}</li>" for b in bullets)


def _edu_html() -> str:
    html = ""
    for edu in RESUME["education"]:
        gpa_str = f"&nbsp;&nbsp; GPA: {edu['gpa']}" if edu.get("gpa") else ""
        html += f"""
        <div class="entry">
          <div class="entry-header">
            <span class="entry-title">{edu['school']}</span>
            <span class="entry-date">{edu.get('date', '')}{gpa_str}</span>
          </div>
          <div class="entry-sub">{edu['degree']}</div>
        </div>"""
    return html


def _html_shell(body_content: str, title: str = "Zein Rady – Resume") -> str:
    r = RESUME
    c = r["contact"]
    contact_line = (
        f"{c['email']} &nbsp;|&nbsp; {c['phone']} &nbsp;|&nbsp; "
        f'<a href="https://{c["linkedin"]}">{c["linkedin"]}</a> &nbsp;|&nbsp; '
        f'<a href="https://{c["github"]}">{c["github"]}</a> &nbsp;|&nbsp; '
        f'{c["website"]}'
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{_CSS}</style>
</head>
<body>
<h1>{r['name']}</h1>
<div class="contact">{contact_line}</div>
{body_content}
</body>
</html>"""


def build_resume_html(data: dict) -> str:
    """Tailored 1-page resume — same CSS/structure as portfolio, AI-rewritten bullets."""
    r = RESUME

    experience_html = ""
    for exp in data["experience"]:
        experience_html += f"""
        <div class="entry">
          <div class="entry-header">
            <span class="entry-title">{exp['title']}</span>
            <span class="entry-date">{exp['date']}</span>
          </div>
          <div class="entry-sub">{exp['org']}</div>
          <ul>{_bullets_html(exp['bullets'])}</ul>
        </div>"""

    projects_html = ""
    for proj in data["projects"]:
        projects_html += f"""
        <div class="entry">
          <div class="entry-header">
            <span class="entry-title">{proj['title']}</span>
          </div>
          <div class="entry-sub">{proj['subtitle']}</div>
          <ul>{_bullets_html(proj['bullets'])}</ul>
        </div>"""

    # Skills always use full RESUME list (same as portfolio) to guarantee 1-page length
    skills_technical = ", ".join(r["skills"]["technical"])
    skills_soft = ", ".join(r["skills"]["soft"])
    summary = data.get("summary", r.get("summary", ""))

    body = f"""
<div class="section-title">Professional Summary</div>
<div class="summary">{summary}</div>

<div class="section-title">Education</div>
{_edu_html()}

<div class="section-title">Experience</div>
{experience_html}

<div class="section-title">Projects</div>
{projects_html}

<div class="section-title">Skills</div>
<div class="skills-line"><strong>Technical:</strong> {skills_technical}</div>
<div class="skills-line"><strong>Soft Skills:</strong> {skills_soft}</div>"""

    return _html_shell(body)


def build_portfolio_resume_html() -> str:
    """1-page base resume for portfolio — fixed entries, no AI tailoring."""
    r = RESUME

    TOP_EXP = {"Treasurer", "Behavioral Health Technician", "Lead Structural Designer"}
    top_exp = [e for e in r["experience"] if e["title"] in TOP_EXP]

    experience_html = ""
    for exp in top_exp:
        experience_html += f"""
        <div class="entry">
          <div class="entry-header">
            <span class="entry-title">{exp['title']}</span>
            <span class="entry-date">{exp['date']}</span>
          </div>
          <div class="entry-sub">{exp['org']}</div>
          <ul>{_bullets_html(exp['bullets'])}</ul>
        </div>"""

    TOP_PROJ = {
        "Batch Least-Squares Orbit Determination",
        "Sequential Orbit Determination (Extended Kalman Filter)",
        "High-Powered Rocket – Proxima (RPL @ UCSD)",
        "Autonomous Quadcopter – DBVF @ UCSD",
    }
    top_proj = [p for p in r["projects"] if p["title"] in TOP_PROJ]

    projects_html = ""
    for proj in top_proj:
        projects_html += f"""
        <div class="entry">
          <div class="entry-header">
            <span class="entry-title">{proj['title']}</span>
          </div>
          <div class="entry-sub">{proj['subtitle']}</div>
          <ul>{_bullets_html(proj['bullets'])}</ul>
        </div>"""

    skills_technical = ", ".join(r["skills"]["technical"])
    skills_soft = ", ".join(r["skills"]["soft"])
    summary = r.get("summary", "")

    body = f"""
<div class="section-title">Professional Summary</div>
<div class="summary">{summary}</div>

<div class="section-title">Education</div>
{_edu_html()}

<div class="section-title">Experience</div>
{experience_html}

<div class="section-title">Projects</div>
{projects_html}

<div class="section-title">Skills</div>
<div class="skills-line"><strong>Technical:</strong> {skills_technical}</div>
<div class="skills-line"><strong>Soft Skills:</strong> {skills_soft}</div>"""

    return _html_shell(body)


def build_cover_letter_html(data: dict, job_title: str, company: str) -> str:
    r = RESUME
    contact = r["contact"]

    # Strip any dashes or em dashes the model may have slipped through
    raw_cl = data.get("cover_letter", "")
    raw_cl = re.sub(r"[–—]", " ", raw_cl)   # em/en dashes → space
    raw_cl = re.sub(r" - ", ", ", raw_cl)    # spaced hyphens → comma
    raw_cl = re.sub(r"  +", " ", raw_cl)

    paragraphs = raw_cl.split("\n\n")
    paras_html = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Zein Rady – Cover Letter</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 11pt;
    color: #000;
    background: #fff;
    padding: 1in 1in;
    max-width: 8.5in;
    margin: 0 auto;
    line-height: 1.55;
  }}
  .header {{ margin-bottom: 28px; }}
  .header h1 {{ font-size: 16pt; font-weight: bold; }}
  .header .contact {{ font-size: 10pt; color: #333; margin-top: 4px; }}
  .date {{ margin-bottom: 22px; }}
  .salutation {{ margin-bottom: 16px; }}
  p {{ margin-bottom: 16px; }}
  .closing {{ margin-top: 28px; }}
  @media print {{
    body {{ padding: 0.75in 1in; }}
    @page {{ size: letter; margin: 0; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>{r['name']}</h1>
  <div class="contact">{contact['email']} &nbsp;&middot;&nbsp; {contact['phone']} &nbsp;&middot;&nbsp; {contact['linkedin']}</div>
</div>
<div class="date">June 2026</div>
<div class="salutation">Dear Hiring Manager{f' at {company}' if company else ''},</div>
{paras_html}
<div class="closing">
  <p>Sincerely,</p>
  <p><strong>{r['name']}</strong></p>
</div>
</body>
</html>"""
