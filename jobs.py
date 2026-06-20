import httpx, os, asyncio, re
from urllib.parse import quote

ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = os.environ.get("JOOBLE_API_KEY", "")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")


async def search_jobs(query: str, location: str = "") -> dict:
    tasks = [
        search_usajobs(query, location),
        search_adzuna(query, location) if (ADZUNA_APP_ID and ADZUNA_APP_KEY) else asyncio.sleep(0, result=[]),
        search_linkedin(query, location),
        search_remotive(query),
        search_jooble(query, location) if JOOBLE_API_KEY else asyncio.sleep(0, result=[]),
        search_google(query, location) if SERPAPI_KEY else asyncio.sleep(0, result=[]),
    ]
    groups = await asyncio.gather(*tasks)
    results, seen = [], set()
    for g in groups:
        for job in (g or []):
            key = (job.get("title", "").lower(), job.get("company", "").lower())
            if key not in seen:
                seen.add(key)
                results.append(job)
    return {"jobs": results, "total": len(results)}


# ── USAJobs ────────────────────────────────────────────────────
async def search_usajobs(query: str, location: str = "") -> list:
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": os.environ.get("CONTACT_EMAIL", ""),
        "Authorization-Key": os.environ.get("USAJOBS_API_KEY", ""),
    }
    jobs, page = [], 1
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            while True:
                params = {
                    "Keyword": query,
                    "ResultsPerPage": 500,
                    "Page": page,
                    "SortField": "OpenDate",
                    "SortDirection": "Desc",
                }
                if location:
                    params["LocationName"] = location
                r = await client.get("https://data.usajobs.gov/api/search", params=params, headers=headers)
                r.raise_for_status()
                data = r.json()
                items = data.get("SearchResult", {}).get("SearchResultItems", [])
                for item in items:
                    pos = item.get("MatchedObjectDescriptor", {})
                    jobs.append({
                        "source": "USAJobs",
                        "title": pos.get("PositionTitle", ""),
                        "company": pos.get("OrganizationName", ""),
                        "location": pos.get("PositionLocationDisplay", ""),
                        "url": pos.get("PositionURI", ""),
                        "date": pos.get("PublicationStartDate", "")[:10] if pos.get("PublicationStartDate") else "",
                        "description": pos.get("UserArea", {}).get("Details", {}).get("JobSummary", ""),
                        "salary": _usajobs_salary(pos),
                    })
                total = int(data.get("SearchResult", {}).get("SearchResultCountAll", 0))
                if len(jobs) >= total or len(items) < 500:
                    break
                page += 1
    except Exception:
        pass
    return jobs


def _usajobs_salary(pos: dict) -> str:
    rem = pos.get("PositionRemuneration", [])
    if not rem:
        return ""
    r = rem[0]
    low, high, interval = r.get("MinimumRange", ""), r.get("MaximumRange", ""), r.get("RateIntervalCode", "")
    if low and high:
        return f"${float(low):,.0f} – ${float(high):,.0f} / {interval}"
    return ""


# ── Adzuna ────────────────────────────────────────────────────
async def search_adzuna(query: str, location: str = "") -> list:
    base_params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "results_per_page": 50,
        "sort_by": "relevance",
        "content-type": "application/json",
    }
    if location:
        base_params["where"] = location

    all_items = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            async def fetch_page(p):
                try:
                    r = await client.get(f"https://api.adzuna.com/v1/api/jobs/us/search/{p}", params=base_params)
                    r.raise_for_status()
                    return r.json().get("results", [])
                except Exception:
                    return []
            # Fetch in batches of 3 to avoid rate limiting, up to 100 pages (5000 results)
            for batch_start in range(1, 101, 3):
                batch = await asyncio.gather(*[fetch_page(p) for p in range(batch_start, batch_start + 3)])
                got = 0
                for items in batch:
                    all_items.extend(items)
                    got += len(items)
                if got < 50 * 3:  # ran out of results
                    break
    except Exception:
        pass

    jobs, seen = [], set()
    for item in all_items:
        url = item.get("redirect_url", "")
        if url in seen:
            continue
        seen.add(url)
        jobs.append({
            "source": "Adzuna",
            "title": item.get("title", ""),
            "company": item.get("company", {}).get("display_name", ""),
            "location": item.get("location", {}).get("display_name", ""),
            "url": url,
            "date": item.get("created", "")[:10] if item.get("created") else "",
            "description": item.get("description", ""),
            "salary": _adzuna_salary(item),
        })
    return jobs


def _adzuna_salary(item: dict) -> str:
    low, high = item.get("salary_min"), item.get("salary_max")
    if low and high:
        return f"${float(low):,.0f} – ${float(high):,.0f} / yr"
    return ""


# ── LinkedIn ──────────────────────────────────────────────────
async def search_linkedin(query: str, location: str = "") -> list:
    from bs4 import BeautifulSoup
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    jobs, seen = [], set()
    try:
        async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
            # Fetch in batches of 3 concurrent pages, up to 40 pages (1000 results)
            starts = list(range(0, 1000, 25))
            for batch_start in range(0, len(starts), 3):
                batch = starts[batch_start:batch_start + 3]

                async def fetch_li(start, cl=client):
                    try:
                        r = await cl.get(
                            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
                            params={"keywords": query, "location": location or "United States", "start": start, "count": 25},
                        )
                        return r.text if r.status_code == 200 else ""
                    except Exception:
                        return ""

                pages = await asyncio.gather(*[fetch_li(s) for s in batch])
                got_any = False
                for html in pages:
                    if not html:
                        continue
                    soup = BeautifulSoup(html, "lxml")
                    cards = soup.find_all("div", class_="base-search-card")
                    if not cards:
                        continue
                    got_any = True
                    for card in cards:
                        try:
                            title_el = card.find("h3", class_="base-search-card__title")
                            company_el = card.find("h4", class_="base-search-card__subtitle")
                            location_el = card.find("span", class_="job-search-card__location")
                            link_el = card.find("a", class_="base-card__full-link")
                            url = link_el["href"].split("?")[0] if link_el else ""
                            if url in seen:
                                continue
                            seen.add(url)
                            jobs.append({
                                "source": "LinkedIn",
                                "title": title_el.get_text(strip=True) if title_el else "",
                                "company": company_el.get_text(strip=True) if company_el else "",
                                "location": location_el.get_text(strip=True) if location_el else "",
                                "url": url,
                                "date": "",
                                "description": "",
                                "salary": "",
                            })
                        except Exception:
                            continue
                if not got_any:
                    break  # LinkedIn ran out of results
    except Exception:
        pass
    return jobs


# ── Remotive ──────────────────────────────────────────────────
async def search_remotive(query: str) -> list:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://remotive.com/api/remote-jobs", params={"search": query, "limit": 5000})
            r.raise_for_status()
            data = r.json()
    except Exception:
        return []

    return [{
        "source": "Remotive",
        "title": item.get("title", ""),
        "company": item.get("company_name", ""),
        "location": "Remote",
        "url": item.get("url", ""),
        "date": item.get("publication_date", "")[:10] if item.get("publication_date") else "",
        "description": item.get("description", "")[:500],
        "salary": item.get("salary", ""),
    } for item in data.get("jobs", [])]


# ── Jooble ────────────────────────────────────────────────────
async def search_jooble(query: str, location: str = "") -> list:
    """Aggregates Indeed, Glassdoor, ZipRecruiter, Monster + 140 more."""
    jobs, seen = [], set()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            async def fetch_jooble_page(page):
                try:
                    r = await client.post(
                        f"https://jooble.org/api/{JOOBLE_API_KEY}",
                        json={"keywords": query, "location": location or "United States", "resultonpage": 100, "page": page},
                        headers={"Content-Type": "application/json"},
                    )
                    r.raise_for_status()
                    return r.json().get("jobs", [])
                except Exception:
                    return []

            # Fetch 20 pages concurrently = up to 2000 results
            batches = await asyncio.gather(*[fetch_jooble_page(p) for p in range(1, 21)])
            for batch in batches:
                for item in batch:
                    url = item.get("link", "")
                    if url in seen:
                        continue
                    seen.add(url)
                    jobs.append({
                        "source": "Jooble",
                        "title": item.get("title", ""),
                        "company": item.get("company", ""),
                        "location": item.get("location", ""),
                        "url": url,
                        "date": item.get("updated", "")[:10] if item.get("updated") else "",
                        "description": item.get("snippet", ""),
                        "salary": item.get("salary", ""),
                    })
    except Exception:
        pass
    return jobs


# ── Google Jobs (via SerpAPI) ─────────────────────────────────
async def search_google(query: str, location: str = "") -> list:
    """Search Google Jobs via SerpAPI — pulls from all sources Google indexes."""
    jobs, seen = [], set()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Fetch multiple pages (each page = 10 results, use start param)
            async def fetch_google_page(start):
                try:
                    params = {
                        "engine": "google_jobs",
                        "q": f"{query} jobs" + (f" in {location}" if location else ""),
                        "api_key": SERPAPI_KEY,
                        "hl": "en",
                        "start": start,
                    }
                    if location:
                        params["location"] = location
                    r = await client.get("https://serpapi.com/search", params=params)
                    r.raise_for_status()
                    return r.json().get("jobs_results", [])
                except Exception:
                    return []

            # Fetch 10 pages concurrently (10 results each = up to 100 Google Jobs results)
            pages = await asyncio.gather(*[fetch_google_page(s) for s in range(0, 100, 10)])
            for page_jobs in pages:
                for item in page_jobs:
                    url = (item.get("related_links") or [{}])[0].get("link", "") or item.get("job_id", "")
                    if url in seen:
                        continue
                    seen.add(url)
                    jobs.append({
                        "source": "Google",
                        "title": item.get("title", ""),
                        "company": item.get("company_name", ""),
                        "location": item.get("location", ""),
                        "url": url,
                        "date": item.get("detected_extensions", {}).get("posted_at", ""),
                        "description": item.get("description", ""),
                        "salary": item.get("detected_extensions", {}).get("salary", ""),
                    })
    except Exception:
        pass
    return jobs


# ── URL fetch ─────────────────────────────────────────────────
async def fetch_job_from_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=headers) as client:
            r = await client.get(url)
            r.raise_for_status()
            html = r.text
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()[:8000]
    except Exception as e:
        return f"Could not fetch URL: {e}. Please paste the job description manually."
