import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import data_processing

tenders = data_processing.search()

def create_graph_1(tenders):
    df = pd.DataFrame(tenders)

    if df.empty:
        return None
    
    df["unit_price"] = df["amount"] / df["qty"]
    mean_price = df["unit_price"].mean()
    median_price = df["unit_price"].median()
    