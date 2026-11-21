#!/usr/bin/env python3
"""Build the ESA verification data from the trainees spreadsheet.

Usage:  python3 tools/build_certificates.py trainees.xlsx      (or .csv)

One row per passed course. Columns (English or Arabic headers, any order):
  Name               | الاسم / اسم المتدرب                 (required)
  Course             | الكورس / البرنامج                   (required)
  Verification Code  | كود التحقق / رقم الشهادة            (required)
  GP                 | GP Code / Graduate Passport / كود GP (optional, groups a trainee's courses)
  Date               | التاريخ / تاريخ الاجتياز              (optional)

Writes two files at the site root:
  certificates.json  -> looked up by Verification Code on the home page (#verify)
  passports.json     -> looked up by GP code on /passport/

Every record is encrypted with a key derived from its own code and stored under a
hash of that code, so the published files reveal no names or codes: a record can
only be found and opened by someone who types the exact code.
The GP code is never stored inside a certificate record, so verifying a
certificate does not reveal the trainee's passport code.
Do not commit the spreadsheet itself to the repository.
"""
import sys, json, os, base64, hashlib, unicodedata, re, datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PROGRAMS = ["Data Analysis", "Cybersecurity", "Graphic Design", "Learning & Development",
            "Performance Management System", "Healthcare Facility Management",
            "Digital Marketing", "Networking & IT", "Infection Control"]
ALIASES = {
    "id": ["verification code", "verification", "verify code", "code", "certificate id", "certificate code",
           "certificate no", "certificate number", "cert id", "id", "كود التحقق", "رقم الشهادة", "كود الشهادة", "الكود"],
    "gp": ["gp", "gp code", "gp id", "graduate passport", "graduated passport", "graduate passport code",
           "passport", "passport code", "graduate id", "كود gp", "كود الباسبور", "رقم الخريج", "الباسبور"],
    "course": ["course", "course name", "program", "programme", "الكورس", "اسم الكورس", "البرنامج", "الدورة"],
    "name": ["name", "trainee", "trainee name", "student", "student name", "full name", "الاسم", "اسم المتدرب", "المتدرب"],
    "date": ["date", "issue date", "completion date", "passed date", "pass date", "graduation date",
             "التاريخ", "تاريخ الإصدار", "تاريخ الاجتياز", "تاريخ التخرج"],
}
LOOKUP = {a: k for k, al in ALIASES.items() for a in al}

def norm_code(v):
    v = unicodedata.normalize("NFKC", str(v))
    v = v.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    return re.sub(r"\s+", "", v).upper()

def read_rows(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        ws = openpyxl.load_workbook(path, data_only=True).active
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        import csv
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    # the header is the first row that names at least two known columns
    for hi, r in enumerate(rows[:10]):
        keys = [LOOKUP.get(str(h or "").strip().lower()) for h in r]
        if sum(1 for k in keys if k) >= 2:
            break
    else:
        sys.exit("Could not find the header row (Name / Course / Verification Code / GP).")
    unknown = [str(h) for h, k in zip(rows[hi], keys) if h not in (None, "") and not k]
    for n, r in enumerate(rows[hi + 1:], start=hi + 2):
        rec = {k: r[i] for i, k in enumerate(keys) if k and i < len(r)}
        if any(v not in (None, "") for v in rec.values()):
            yield n, rec
    if unknown:
        print("  (ignored columns: " + ", ".join(unknown) + ")")

def fmt_date(v):
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v or "").strip()
    for f in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d.%m.%Y"):
        try: return datetime.datetime.strptime(s, f).strftime("%Y-%m-%d")
        except ValueError: pass
    return s or None

def seal(salt, kind, code, payload):
    idx = hashlib.sha256(f"esa-{kind}idx|{salt}|{code}".encode()).hexdigest()
    key = hashlib.sha256(f"esa-{kind}key|{salt}|{code}".encode()).digest()
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(payload, ensure_ascii=False).encode(), None)
    return idx, base64.b64encode(iv + ct).decode()

def is_arabic(s): return bool(re.search(r"[؀-ۿ]", s))

def main(src, outdir="."):
    canon = {p.lower(): p for p in PROGRAMS}
    certs, passports, problems = {}, {}, []
    for n, rec in read_rows(src):
        code = norm_code(rec.get("id") or "")
        name = re.sub(r"\s+", " ", str(rec.get("name") or "")).strip()
        name = re.sub(r"^(Dr|Eng|Mr|Mrs|Ms)\.(?=\S)", r"\1. ", name)
        course = re.sub(r"\s+", " ", str(rec.get("course") or "")).strip()
        if not (code and name and course):
            problems.append(f"row {n}: missing name, course or verification code — skipped"); continue
        if code in certs:
            problems.append(f"row {n}: duplicate verification code {code} — skipped"); continue
        course = canon.get(course.lower(), course)
        if course not in PROGRAMS:
            problems.append(f"row {n}: course '{course}' is not one of the site's 9 programs (kept as written)")
        date = fmt_date(rec.get("date"))
        c = {"name": name, "course": course}
        if date: c["date"] = date
        certs[code] = c
        gp = norm_code(rec.get("gp") or "")
        if gp:
            p = passports.setdefault(gp, {"names": [], "certificates": []})
            if name not in p["names"]: p["names"].append(name)
            p["certificates"].append({"id": code, "program": course, "date": date or "", "status": "valid"})
    for gp, p in passports.items():
        if len(p["names"]) > 1:
            problems.append(f"GP {gp}: rows carry different names {p['names']} — the first one is shown")

    salt_c = base64.b64encode(os.urandom(12)).decode()
    recs = dict(seal(salt_c, "", code, c) for code, c in certs.items())
    with open(os.path.join(outdir, "certificates.json"), "w", encoding="utf-8") as f:
        json.dump({"v": 1, "salt": salt_c, "count": len(recs), "records": recs}, f, separators=(",", ":"))

    salt_p = base64.b64encode(os.urandom(12)).decode()
    precs = {}
    for gp, p in passports.items():
        nm = p["names"][0]
        dates = sorted(c["date"] for c in p["certificates"] if c["date"])
        g = {"id": gp, "name_ar": nm if is_arabic(nm) else "", "name_en": "" if is_arabic(nm) else nm,
             "tier": "Graduate", "status": "active", "joined": dates[0] if dates else ""}
        certs_sorted = sorted(p["certificates"], key=lambda c: c["date"] or "9999")
        k, v = seal(salt_p, "gp", gp, {"graduate": g, "certificates": certs_sorted})
        precs[k] = v
    with open(os.path.join(outdir, "passports.json"), "w", encoding="utf-8") as f:
        json.dump({"v": 1, "salt": salt_p, "count": len(precs), "records": precs}, f, separators=(",", ":"))

    print(f"{len(certs)} certificates  ->  certificates.json")
    print(f"{len(passports)} graduate passports  ->  passports.json")
    for p in problems: print("  !", p)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1], *(sys.argv[2:3]))
