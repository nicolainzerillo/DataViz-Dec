import base64
import streamlit as st
from typing import List, Tuple
import pandas as pd

# Inspiration
# https://medium.com/@cameronjosephjones/building-a-kpi-dashboard-in-streamlit-using-python-c88ac63903f5

def set_page_config():
    st.set_page_config(
        page_title="Top Switch Games Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv('best_selling_switch_games.csv')
    data['release_date']= pd.to_datetime(data['release_date'])
    data['as_of']= pd.to_datetime(data['as_of'])
    return data

def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data


@st.cache_data
def calculate_kpis(data: pd.DataFrame) -> List[float]:
    total_sales = data['copies_sold'].sum()
    sales_in_m = f"{total_sales / 1000000:.2f}M"

    total_games = data['title'].nunique()

    unique_developers = data['developer'].nunique()

    average_sales_per_developer = f"{total_sales / unique_developers / 1000:.2f}K"
    
    return [sales_in_m, total_games, unique_developers, average_sales_per_developer]

def display_kpi_metrics(kpis: List[float], kpi_names: List[str]):
    st.header("KPI Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)


def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    st.sidebar.header("Filters")

    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['release_date'].min().date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", data['as_of'].max().date()))

    selected_genres = st.sidebar.multiselect("Select Genre", data['genre'].unique())

    selected_developer = st.sidebar.multiselect("Select Developer", data['developer'].unique())

    selected_publisher = st.sidebar.multiselect("Select Publisher", data['publisher'].unique())

    return selected_genres, selected_developer, selected_publisher

def display_charts(data: pd.DataFrame):

    st.subheader("Top 10 Games 🕹️")
    top_games = data.groupby('title')['copies_sold'].sum().reset_index().sort_values('copies_sold',
                                                                                              ascending=False).head(10)
    top_game = top_games.head(1)['title'].iloc[0]

    top_game_sales = top_games.head(1)['copies_sold'].iloc[0] / data['copies_sold'].sum()

    st.write(f':green[{top_game} makes up {top_game_sales: .0%} of total sales]')

    st.bar_chart(top_games, x='title', y='copies_sold', color=["#ff4554"])
    # colors = "#03c3e3", "#ff4554"

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Sales by Developer 🏆")
        total_developer_sales = data.groupby('developer')['copies_sold'].sum().reset_index()
        st.dataframe(total_developer_sales, hide_index=True, use_container_width=True)

    with col2: 
        st.subheader("Total Sales by Publisher 🎉")
        total_publisher_sales = data.groupby('publisher')['copies_sold'].sum().reset_index()
        st.dataframe(total_publisher_sales, hide_index=True, use_container_width=True)

def main():
    set_page_config()

    data = load_data()

    st.title("🎮 Top Switch Games Dashboard")

    selected_genres, selected_developer, selected_publisher = display_sidebar(data)

    filtered_data = data.copy()
    filtered_data = filter_data(filtered_data, 'genre', selected_genres)
    filtered_data = filter_data(filtered_data, 'developer', selected_developer)
    filtered_data = filter_data(filtered_data, 'publisher', selected_publisher)

    kpis = calculate_kpis(filtered_data)
    kpi_names = ["Total Sales", "Total Games", "Unique Developers", "Average Sales Per Developer"]
    display_kpi_metrics(kpis, kpi_names)

    st.markdown("##")
    display_charts(filtered_data)


if __name__ == '__main__':
    main()
