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

# graph = create_graph_1("Олія", "Олія", "15420000-8")
# if graph is not None:
#     graph.show()
# else:
#     pass

def create_graph_2(title, desc, cpv):
    tenders = data_processing.search(title, desc, cpv)
    df = pd.DataFrame(tenders)

    if df.empty:
        return None

    df["unit_price"] = df["amount"] / df["qty"]

    median_price = df["unit_price"].median()

    df["deviation"] = (
    (df["unit_price"] - median_price) / median_price * 100
    ).clip(lower=0)

    if median_price <= 0:
        return None

    def classify(deviation):
        if deviation <= 10:
            return "Нормальна ціна"
        elif deviation <= 30:
            return "Помірне відхилення"
        else:
            return "Аномальне відхилення"
    df["category"] = df["deviation"].apply(classify)

    categories = [
        "Нормальна ціна",
        "Помірне відхилення",
        "Аномальне відхилення"
    ]

    counts = (
        df["category"].value_counts().reindex(categories, fill_value=0)
    )

    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.35,
            sort=False,
            marker=dict(
                colors=[
                    "#22A06B",
                    "#F5A623",
                    "#DC2626"
                ]
            ),
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>"
                "Кількість тендерів: %{value}<br>"
                "Частка: %{percent}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Розподіл тендерів за завищенням цін",
        template="plotly_white",
        height=550
    )

    return fig

# graph_2 = create_graph_2("Олія", "Олія", "15420000-8")

# if graph_2 is not None:
#     graph_2.show()

