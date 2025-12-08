import os, requests

u_if = "https://www.nseindia.com/api/integrated-filing-results"

h = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-integrated-filing"
}

def g_res(sym, iss, ped):
    s = requests.Session()
    s.headers.update(h)
    q = {
        "index": "equities",
        "symbol": sym,
        "issuer": iss,
        "period_ended": ped,
        "type": "Integrated Filing- Financials",
        "page": 1,
        "size": 20
    }
    r = s.get(u_if, params=q, timeout=20)
    r.raise_for_status()
    return r.json(), s

def dl_all(sym, iss, ped, outdir="xbrl_files"):
    j, s = g_res(sym, iss, ped)
    xs = j.get("data", [])
    if not xs:
        print("no rows")
        return
    os.makedirs(outdir, exist_ok=True)
    for r in xs:
        x = r.get("xbrl")
        if not x:
            continue
        z = s.get(x, timeout=30, allow_redirects=True)
        ct = z.headers.get("content-type", "")
        if z.status_code != 200 or "xml" not in ct.lower():
            print("fail", z.status_code, ct, z.text[:200])
            continue
        tag = (r.get("consolidated") or "NA").replace(" ", "_")
        qe = (r.get("qe_Date") or "").replace(" ", "_")
        nm = f"{sym}_{qe}_{tag}.xml"
        pth = os.path.join(outdir, nm)
        with open(pth, "wb") as f:
            f.write(z.content)
        print("saved", pth)

if __name__ == "__main__":
    companies = [
        ("ADANIPORTS", "Adani Ports and Special Economic Zone Limited"),
        ("RELIANCE", "Reliance Industries Limited"),
        ("MARUTI", "Maruti Suzuki India Limited"),
        ("M&M", "Mahindra & Mahindra Limited")
    ]
    
    for sym, iss in companies:
        print(f"\n{'='*60}")
        print(f"Downloading {sym}...")
        print('='*60)
        dl_all(sym, iss, "30-Jun-2025", "xbrl_downloads")
