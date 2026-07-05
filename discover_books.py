import aiohttp, asyncio, logging, json, os

logging.basicConfig(level=logging.INFO)

BRANCHES = [
    ("كيمياء عضوية", 'subject:"Chemistry, Organic"'),
    ("كيمياء غير عضوية", 'subject:"Chemistry, Inorganic"'),
    ("كيمياء فيزيائية", 'subject:"Chemistry, Physical and theoretical"'),
    ("كيمياء تحليلية", 'subject:"Chemistry, Analytic"'),
    ("كيمياء حيوية", "subject:Biochemistry"),
    ("كيمياء دوائية", 'subject:"Pharmaceutical chemistry"'),
    ("كيمياء بيئية", 'subject:"Environmental chemistry"'),
    ("كيمياء حرارية", 'subject:"Thermochemistry" OR subject:"Chemical thermodynamics"'),
    ("كيمياء النانو", 'subject:Nanochemistry OR subject:Nanotechnology'),
    ("كيمياء عامة", "subject:Chemistry"),
]

async def search_ia(subject_q, max_rows=200):
    results = []
    page = 1
    while len(results) < max_rows:
        url = "https://archive.org/advancedsearch.php"
        params = {
            "q": f"{subject_q} AND mediatype:texts",
            "fl[]": ["identifier", "title", "creator", "downloads", "year"],
            "rows": min(200, max_rows - len(results)),
            "page": page,
            "output": "json",
            "sort[]": "downloads desc",
        }
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=30) as r:
                if r.status != 200:
                    return results
                data = await r.json()
                docs = data.get("response", {}).get("docs", [])
                if not docs:
                    break
                results.extend(docs)
                page += 1
    return results

async def verify_pdf(identifier):
    url = f"https://archive.org/metadata/{identifier}"
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(url, timeout=30) as r:
                if r.status != 200:
                    return None
                meta = await r.json()
                files = meta.get("files", [])
                # Find non-encrypted PDFs under 48MB
                MAX = 48 * 1024 * 1024
                good = []
                for f in files:
                    name = f.get("name", "").lower()
                    if not name.endswith(".pdf"):
                        continue
                    if "encrypted" in name:
                        continue
                    try:
                        sz = int(f.get("size", 0))
                    except:
                        sz = 0
                    if 50000 < sz < MAX:
                        good.append(f["name"])
                if good:
                    return good  # sorted by preference
                # Fallback: any non-encrypted PDF
                any_non_enc = [f["name"] for f in files
                               if f.get("name", "").lower().endswith(".pdf")
                               and "encrypted" not in f.get("name", "").lower()]
                return any_non_enc or None
        except:
            pass
    return None

async def discover_and_save(max_per_branch=100):
    all_books = {}
    stats = {}
    for branch_name, subject_q in BRANCHES:
        logging.info(f"Searching {branch_name}...")
        docs = await search_ia(subject_q, max_rows=500)
        branch_books = []
        for d in docs:
            ident = d.get("identifier", "")
            if not ident:
                continue
            pdfs = await verify_pdf(ident)
            if pdfs:
                branch_books.append({
                    "ia_id": ident,
                    "title": (d.get("title") or "Unknown")[:80],
                    "author": (d.get("creator") or "Unknown")[:50],
                    "year": str(d.get("year") or ""),
                    "size": f"{d.get('downloads', 0)} downloads",
                })
                if len(branch_books) >= max_per_branch:
                    break
        all_books[branch_name] = branch_books
        stats[branch_name] = len(branch_books)
        logging.info(f"{branch_name}: {len(branch_books)} books with PDF")

    # Save to JSON
    json_path = os.path.join(os.path.dirname(__file__), "books_db.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in all_books.values())
    logging.info(f"Saved {total} books to books_db.json")
    return stats

async def main():
    stats = await discover_and_save()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"Total: {sum(v for v in stats.values())}")

if __name__ == "__main__":
    asyncio.run(main())
