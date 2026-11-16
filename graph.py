import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import data_processing

def create_graph_1(title, desc, cpv):
    tenders = data_processing.search(title, desc, cpv)
    df = pd.DataFrame(tenders)

    if df.empty:
        return None
    
    df["unit_price"] = df["amount"] / df["qty"]
    mean_price = df["unit_price"].mean()
    median_price = df["unit_price"].median()

    fig = px.histogram(
        df,
        x="unit_price",
        nbins=20,
        title="Розподіл цін за одиницю товару"
    )

    fig.add_vline(
        x=mean_price,
        line_color="orange",
        line_dash="dash",
        line_width=3
    )

    fig.add_vline(
        x=median_price,
        line_color="red",
        line_width=3
    )

    fig.update_traces(
    marker_color="#6495ED",
    marker_line_color="black",
    marker_line_width=1.2
    )

    fig.update_layout(
        bargap=0.15
    )

    return fig

graph = create_graph_1("Олія", "Олія", "15420000-8")
if graph is not None:
    graph.show()
else:
    pass