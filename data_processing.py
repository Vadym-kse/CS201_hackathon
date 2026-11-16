import json

def search(title, name, cpv):
    with open("tenders.json", "r") as f:
        tenders = json.load(f)
    return [item for item in tenders if (item.get("cpv") == cpv or cpv == "0") and ((title.lower().strip() in item["title"].lower() or name.lower().strip() in item["name"].lower()) or (title == "0" and name.lower().strip() in item["name"].lower()) or (name == "0" and title.lower().strip() in item["title"].lower()))]