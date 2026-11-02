#!/usr/bin/env python3
"""Build certificates.json for the ESA certificate-verification section.

Usage:  python3 tools/build_certificates.py trainees.xlsx   (or .csv)

Columns (English or Arabic headers, any order):
  ID      | رقم الشهادة / ID   (required)
  Course  | البرنامج           (required, English program name as on the site)
  Name    | الاسم              (optional)
  Date    | تاريخ الإصدار      (optional)

Each record is encrypted with a key derived from its own ID and stored under a
hash of that ID, so the published file does not reveal names or IDs: a record
can only be found and opened by someone who types the exact ID.
Do not commit the source spreadsheet to the repository.
"""
import sys, json, os, base64, hashlib, unicodedata, re, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROGRAMS = ["Data Analysis","Cybersecurity","Graphic Design","Learning & Development",
            "Performance Management System","Healthcare Facility Management",
            "Digital Marketing","Networking & IT","Infection Control"]
ALIASES = {"id":"id","certificate id":"id","رقم الشهادة":"id","الرقم":"id","كود":"id",
           "course":"course","program":"course","البرنامج":"course","الكورس":"course","الدورة":"course",
           "name":"name","trainee":"name","الاسم":"name","اسم المتدرب":"name",
           "date":"date","issue date":"date","تاريخ الإصدار":"date","التاريخ":"date"}

def norm_id(v):
    v = unicodedata.normalize("NFKC", str(v))
    v = v.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    return re.sub(r"\s+", "", v).upper()

def read_rows(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        ws = openpyxl.load_workbook(path, data_only=True).active
        rows = list(ws.iter_rows(values_only=True))
    else:
        import csv
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    head = [ALIASES.get(str(h or "").strip().lower(), str(h or "").strip().lower()) for h in rows[0]]
    for r in rows[1:]:
        rec = {head[i]: r[i] for i in range(min(len(head), len(r)))}
        if any(v not in (None, "") for v in rec.values()):
            yield rec

def fmt_date(v):
    if isinstance(v, (datetime.date, datetime.datetime)): return v.strftime("%Y-%m-%d")
    return str(v).strip() if v not in (None, "") else None

def main(src, out="certificates.json"):
    salt = base64.b64encode(os.urandom(12)).decode()
    records, seen, problems = {}, set(), []
    canon = {p.lower(): p for p in PROGRAMS}
    for n, rec in enumerate(read_rows(src), start=2):
        cid = norm_id(rec.get("id") or "")
        course = str(rec.get("course") or "").strip()
        if not cid or not course:
            problems.append(f"row {n}: missing ID or course"); continue
        if cid in seen:
            problems.append(f"row {n}: duplicate ID {cid}"); continue
        seen.add(cid)
        course = canon.get(course.lower(), course)
        if course not in PROGRAMS:
            problems.append(f"row {n}: program '{course}' is not one of the site's 9 programs (kept as written)")
        payload = {"course": course}
        if rec.get("name"): payload["name"] = str(rec["name"]).strip()
        if fmt_date(rec.get("date")): payload["date"] = fmt_date(rec.get("date"))
        idx = hashlib.sha256(f"esa-idx|{salt}|{cid}".encode()).hexdigest()
        key = hashlib.sha256(f"esa-key|{salt}|{cid}".encode()).digest()
        iv = os.urandom(12)
        ct = AESGCM(key).encrypt(iv, json.dumps(payload, ensure_ascii=False).encode(), None)
        records[idx] = base64.b64encode(iv + ct).decode()
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"v": 1, "salt": salt, "count": len(records), "records": records}, f, separators=(",", ":"))
    print(f"{len(records)} certificates written to {out}")
    for p in problems: print("  !", p)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1], *(sys.argv[2:3]))
