import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_tenders(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("tenders", [data])
    
    return data