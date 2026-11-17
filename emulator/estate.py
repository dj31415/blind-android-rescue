"""Read uiautomator XML on stdin; print title-ish texts and the checked radio row(s)."""
import sys, xml.etree.ElementTree as ET
r = ET.fromstring(sys.stdin.read())
texts = [n.get("text") for n in r.iter("node") if n.get("text")][:4]
rows = []
for n in r.iter("node"):
    kids = list(n.iter("node"))
    if any(k.get("checked") == "true" and "Radio" in (k.get("class") or "") for k in kids):
        t = [k.get("text") for k in kids if k.get("text")]
        if t: rows.append((len(kids), t[0]))
print("texts=%s checked=%s" % (texts, min(rows)[1] if rows else None), end="")
