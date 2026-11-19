"""Build a Google Merchant Center product feed (TSV) from the live shop's JSON-LD."""
import csv, json, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA)).read().decode("utf8")

slugs = sorted(set(re.findall(r'href="/shop/([a-z0-9-]+)"', get("https://asal-sarmadi.com/shop"))) - {"basket", "thanks"})
cols = ["id", "item_group_id", "title", "description", "link", "image_link", "price", "availability",
        "condition", "brand", "identifier_exists", "google_product_category", "product_type", "size"]
rows = []
for s in slugs:
    h = get(f"https://asal-sarmadi.com/shop/{s}")
    prod = next(d for d in (json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)) if d.get("@type") == "Product")
    for o in prod["offers"]:
        v = o["name"]
        size = v.split(" ")[0]
        tag = re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")
        kind = "framed art print" if "framed" in v.lower() else ("signed art print" if "signed" in v.lower() else ("canvas print" if "canvas" in v.lower() else "art print"))
        rows.append({
            "id": f"{s}-{tag}"[:50], "item_group_id": s,
            "title": f"{prod['name']}, {kind}, " + re.sub(r",? (framed|canvas|signed.*)$", "", v, flags=re.I)[:150],
            "description": prod["description"] + " Made to order and shipped from Gelato. By Gothenburg artist Asal Sarmadi.",
            "link": o["url"], "image_link": prod["image"] if isinstance(prod["image"], str) else prod["image"][0],
            "price": f"{o['price']:.2f} {o['priceCurrency']}",
            "availability": "in_stock", "condition": "new", "brand": "Asal Sarmadi",
            "identifier_exists": "no", "google_product_category": "500044",
            "product_type": "Art prints > " + kind, "size": size,
        })
with open("feed.tsv", "w", newline="", encoding="utf8") as f:
    w = csv.DictWriter(f, cols, delimiter="\t"); w.writeheader(); w.writerows(rows)
print(len(slugs), "works,", len(rows), "items")
