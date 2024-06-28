import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import os

# 로컬 CSV 파일 경로 지정
file_path_main = os.path.join(os.path.dirname(__file__), '..', 'main.csv')
file_path_daily = os.path.join(os.path.dirname(__file__), '..', 'daily.csv')
file_path_user = os.path.join(os.path.dirname(__file__), '..', 'user.csv')

# CSV 파일 로드
df = pd.read_csv(file_path_main)
day_df = pd.read_csv(file_path_daily)
day_df['event_date'] = pd.to_datetime(day_df['event_date'], errors='coerce')
user_df = pd.read_csv(file_path_user)

day_revenue = day_df[['event_date', 'total_purchase_amount', 'purchase_conversion_rate', 'ARPU', 'ARPS', 'high_brand_daily', 'AOV']]
user_revenue = user_df[['user_id', 'total_spending', 'most_main_purchase', 'most_sub_purchase', 'most_sub_sub_purchase']]
user_pro = user_df[(user_df['most_main_purchase'] != 0) & (user_df['most_sub_purchase'] != 0) & (user_df['most_sub_sub_purchase'] != 0)]

# 페이지 제목
st.title("수익(Revenue) 지표")
st.write("날짜 별 수익 지표")

# 데이터 프레임 요약
st.dataframe(day_revenue.describe())

# 구매 및 구매 전환율(fig1)
fig1 = px.line(day_revenue, x='event_date', y=['total_purchase_amount', 'purchase_conversion_rate'],
               title='Total Purchase Amount and Purchase Conversion Rate Over Time')
st.plotly_chart(fig1)

# 전날 대비 구매 전환율(fig5)
day_df['event_date'] = pd.to_datetime(day_df['event_date'])
daily_conversion_rate_diff_new = day_df['purchase_conversion_rate'].diff().fillna(0)

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=day_df['event_date'].astype(str),
    y=daily_conversion_rate_diff_new,
    marker_color=['red' if x > 0 else 'blue' for x in daily_conversion_rate_diff_new],
))
fig5.update_layout(
    title='Daily Change in Purchase Conversion Rate (Difference)',
    xaxis_title='Day',
    yaxis_title='Difference in Purchase Conversion Rate',
    xaxis_tickangle=-90,
    template='plotly_white'
)
st.plotly_chart(fig5)

# ARPU, ARPS(fig2)
fig2 = px.line(day_revenue, x='event_date', y=['ARPU', 'ARPS'],
               title='ARPU, ARPS Over Time')
st.plotly_chart(fig2)

# AOV(fig4)
fig4 = px.line(day_revenue, x='event_date', y='AOV',
               title='AOV Over Time')
st.plotly_chart(fig4)

# 유저 별 수익 지표
st.title("유저 별 수익 지표")
st.dataframe(user_revenue, height=200)

# 구매 액수 분포(fig6)
bins = [0, 25, 50, 75, 100, float('inf')]
labels = ['0-25 USD', '25-50 USD', '50-75 USD', '75-100 USD', 'Above 100 USD']
price_range_data = pd.cut(df['price'], bins=bins, labels=labels).reset_index()
price_range_counts = price_range_data['price'].value_counts().sort_index()

fig6 = px.bar(
    x=price_range_counts.index,
    y=price_range_counts.values,
    labels={'x': 'Price Range', 'y': 'Count'},
    title='Price Distribution'
)
st.plotly_chart(fig6)

# 카테고리 별 주문 여부(fig3)
user_pro = user_df[user_df['most_main_purchase'] != '0']

def create_pie_chart(df, column, title):
    df_counts = df[column].value_counts().reset_index()
    df_counts.columns = [column, 'count']
    df_counts['label'] = df_counts.apply(lambda row: row[column] if row.name < 3 else '', axis=1)
    fig = px.pie(df_counts, names=column, values='count', title=title)
    fig.update_traces(textposition='inside', textinfo='label+percent', insidetextorientation='radial', customdata=df_counts['label'])
    return fig

fig3 = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
                     subplot_titles=['Main', 'Sub', 'Sub-Sub'])

fig3.add_trace(create_pie_chart(user_pro, 'most_main_purchase', 'Main Category Purchase Count').data[0], 1, 1)
fig3.add_trace(create_pie_chart(user_pro, 'most_sub_purchase', 'Sub Category Purchase Count').data[0], 1, 2)
fig3.add_trace(create_pie_chart(user_pro, 'most_sub_sub_purchase', 'Sub-Sub Category Purchase Count').data[0], 1, 3)

fig3.update_layout(title_text="Category Purchase Counts")
st.plotly_chart(fig3)
