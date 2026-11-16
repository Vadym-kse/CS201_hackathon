import json
import pandas as pd

def search(title, desc, cpv, for_graph):
    with open("tenders.json", "r", encoding="UTF-8") as f:
        tenders = json.load(f)

    t_clean = title.lower().strip()
    d_clean = desc.lower().strip()

    filtered_tenders = []
    for item in tenders:
        if cpv != "0" and item.get("cpv") != cpv:
            continue

        item_title = item["title"].lower()
        item_desc = item["desc"].lower()

        if title == "0" and desc == "0":
            text_cond = True
        elif title == "0":
            text_cond = d_clean in item_desc
        elif desc == "0":
            text_cond = t_clean in item_title
        else:
            text_cond = (t_clean in item_title) or (d_clean in item_desc)

        if text_cond:
            item["unit_price"] = item["amount"] / item["qty"]
            filtered_tenders.append(item)


    pd_searched = pd.DataFrame(filtered_tenders)
    pd_searched["unit_price"] = pd_searched["amount"] / pd_searched["qty"]
    median_price = pd_searched["unit_price"].median()

    if for_graph:
        average_price = pd_searched["unit_price"].mean()
        return pd_searched, average_price, median_price
    else:
        return pd_searched[pd_searched["unit_price"] > median_price*1.75].to_dict(orient="records")
