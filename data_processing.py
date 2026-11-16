import json
import pandas as pd

def search(title, desc, cpv, for_graph):
    with open("tenders.json", "r", encoding="UTF-8") as f:
        tenders = json.load(f)

    filtered_tenders = [item for item in tenders if (item.get("cpv") == cpv or cpv == "0") and ((title.lower().strip() in item["title"].lower() or desc.lower().strip() in item["desc"].lower()) or (title == "0" and desc.lower().strip() in item["desc"].lower()) or (desc == "0" and title.lower().strip() in item["title"].lower()))]
    pd_searched = pd.DataFrame(filtered_tenders)
    pd_searched["unit_price"] = pd_searched["amount"] / pd_searched["qty"]
    median_price = pd_searched["unit_price"].median()

    if for_graph:
        average_price = pd_searched["unit_price"].mean()
        return pd_searched, average_price, median_price
    else:
        return [item for item in filtered_tenders if item["unit_price"] > median_price]

