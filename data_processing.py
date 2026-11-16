import json
def search(title, desc, cpv):
    with open("tenders.json", "r") as f:
        tenders = json.load(f)
    return [item for item in tenders if (item.get("cpv") == cpv or cpv == "0") and ((title.lower().strip() in item["title"].lower() or desc.lower().strip() in item["desc"].lower()) or (title == "0" and desc.lower().strip() in item["desc"].lower()) or (desc == "0" and title.lower().strip() in item["title"].lower()))]