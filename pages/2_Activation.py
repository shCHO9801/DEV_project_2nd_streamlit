import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 로컬 CSV 파일 경로 지정
file_path_daily = os.path.join(os.path.dirname(__file__), '..', 'daily.csv')
# file_path_processed = os.path.join(os.path.dirname(__file__), '..', 'main.csv')

# csv 병합
file_parts = ['main_part1.csv','main_part2.csv','main_part3.csv','main_part4.csv','main_part5.csv','main_part6.csv','main_part7.csv','main_part8.csv','main_part9.csv']
df_list = [pd.read_csv(os.path.join(os.path.dirname(__file__), '..', file) for file in file_parts]
df = pd.concat(df_list, ignore_index=True)

# CSV 파일 로드
daily_df = pd.read_csv(file_path_daily)
daily_df['event_date'] = pd.to_datetime(daily_df['event_date'])

df = pd.read_csv(file_path_processed)

# 지표 시각화 함수
def plot_metric(df, metric):
    fig = px.line(df, x='event_date', y=metric, markers=True, title=f'{metric} over Time')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title=metric,
        xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10)  # 10일 간격 설정
    )
    return fig

def plot_unique_sessions(df):
    fig1 = px.line(df, x='event_date', y='unique_view_sessions', markers=True, title='unique_view_sessions over Time')
    fig2 = px.line(df, x='event_date', y='unique_cart_sessions', markers=True, title='unique_cart_sessions over Time')
    fig3 = px.line(df, x='event_date', y='unique_purchase_sessions', markers=True, title='unique_purchase_sessions over Time')
    
    for fig, color in zip([fig1, fig2, fig3], ['blue', 'green', 'red']):
        fig.update_traces(line=dict(color=color))
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Count',
            xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10)  # 10일 간격 설정
        )
    
    return fig1, fig2, fig3

def plot_unique_users(df):
    fig1 = px.line(df, x='event_date', y='unique_view_users', markers=True, title='unique_view_users over Time')
    fig2 = px.line(df, x='event_date', y='unique_cart_users', markers=True, title='unique_cart_users over Time')
    fig3 = px.line(df, x='event_date', y='unique_purchase_users', markers=True, title='unique_purchase_users over Time')
    
    for fig, color in zip([fig1, fig2, fig3], ['blue', 'green', 'red']):
        fig.update_traces(line=dict(color=color))
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Count',
            xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10)  # 10일 간격 설정
        )
    
    return fig1, fig2, fig3

def plot_event_counts(df):
    fig1 = px.line(df, x='event_date', y='view_count', markers=True, title='view_count over Time')
    fig2 = px.line(df, x='event_date', y='cart_count', markers=True, title='cart_count over Time')
    fig3 = px.line(df, x='event_date', y='purchase_count', markers=True, title='purchase_count over Time')
    
    for fig, color in zip([fig1, fig2, fig3], ['blue', 'green', 'red']):
        fig.update_traces(line=dict(color=color))
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Count',
            xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10)  # 10일 간격 설정
        )
    
    return fig1, fig2, fig3

def plot_unique_users_by_event_type(df):
    event_types = ['view', 'cart', 'purchase']
    user_counts = {event: df[df['event_type'] == event]['user_id'].nunique() for event in event_types}
    
    fig = px.bar(x=list(user_counts.keys()), y=list(user_counts.values()), 
                 labels={'x': 'Event Type', 'y': 'Number of Unique Users'},
                 title='Number of Unique Users by Event Type',
                 color=list(user_counts.keys()))
    return fig

def plot_first_activity_pie_charts(df):
    event_types = ['purchase', 'cart']
    fig = make_subplots(rows=1, cols=len(event_types), subplot_titles=[f'Percentage of Users Who Completed First {event.capitalize()}' for event in event_types], specs=[[{'type':'domain'}, {'type':'domain'}]])
    
    for i, event_type in enumerate(event_types):
        first_activity_users, no_first_activity_users = calculate_first_activity(df, event_type)
        
        labels = [f'First {event_type.capitalize()}', f'No {event_type.capitalize()}']
        sizes = [first_activity_users, no_first_activity_users]
        
        fig.add_trace(go.Pie(labels=labels, values=sizes, name=event_type, marker_colors=['#ff9999', '#66b3ff']), 1, i+1)
    
    fig.update_layout(title_text='Percentage of Users Who Completed First Activity by Event Type')
    return fig

def calculate_first_activity(df, event_type):
    first_activity_df = df[df['event_type'] == event_type].drop_duplicates(subset=['user_id'])
    total_users = df['user_id'].nunique()
    first_activity_users = first_activity_df['user_id'].nunique()
    no_first_activity_users = total_users - first_activity_users
    
    return first_activity_users, no_first_activity_users

def plot_revisit_pie_charts(df):
    event_types = ['purchase', 'view']
    fig = make_subplots(rows=1, cols=len(event_types), subplot_titles=[f'Percentage of Users Who Made Repeated {event.capitalize()}' for event in event_types], specs=[[{'type':'domain'}, {'type':'domain'}]])
    
    for i, event_type in enumerate(event_types):
        repeated_users, first_time_users = calculate_revisit(df, event_type)
        
        labels = [f'Repeated {event_type.capitalize()}', f'First Time {event_type.capitalize()} Only']
        sizes = [repeated_users, first_time_users]
        
        colors = ['#ff9999', '#66b3ff'] if event_type == 'purchase' else ['#99ff99', '#ffcc99']
        
        fig.add_trace(go.Pie(labels=labels, values=sizes, name=event_type, marker_colors=colors), 1, i+1)
    
    fig.update_layout(title_text='Percentage of Users Who Made Repeated Activity by Event Type')
    return fig

def calculate_revisit(df, event_type):
    first_event_df = df[df['event_type'] == event_type].drop_duplicates(subset=['user_id'])
    all_events_df = df[df['event_type'] == event_type]
    
    repeated_events = all_events_df[all_events_df.duplicated(subset=['user_id'], keep=False)]
    first_time_events = first_event_df[~first_event_df['user_id'].isin(repeated_events['user_id'])]
    
    repeated_event_users = repeated_events['user_id'].nunique()
    first_time_event_users = first_time_events['user_id'].nunique()
    
    return repeated_event_users, first_time_event_users

# 페이지 설정
st.title("활성화(Activation) 지표")

# 차트 선택
metrics = [
    "sessions_per_user", "event_count", "unique_sessions", "unique_users", "unique_users_by_event_type", "first_activity_pie_charts", "revisit_pie_charts"
]
metric_selection = st.selectbox("시각화할 지표를 선택하세요", metrics)

# 차트 그리기
if metric_selection == "unique_sessions":
    #st.write("### unique_sessions 차트")
    fig1, fig2, fig3 = plot_unique_sessions(daily_df)
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
elif metric_selection == "unique_users":
    #st.write("### unique_users 차트")
    fig1, fig2, fig3 = plot_unique_users(daily_df)
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
elif metric_selection == "event_count":
    #st.write("### event_count 차트")
    fig1, fig2, fig3 = plot_event_counts(daily_df)
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
elif metric_selection == "unique_users_by_event_type":
   # st.write("### unique_users_by_event_type 차트")
    fig = plot_unique_users_by_event_type(df)
    st.plotly_chart(fig)
elif metric_selection == "first_activity_pie_charts":
    st.write("### First Activity Pie Charts")
    fig = plot_first_activity_pie_charts(df)
    st.plotly_chart(fig)
elif metric_selection == "revisit_pie_charts":
    st.write("### Revisit Pie Charts")
    fig = plot_revisit_pie_charts(df)
    st.plotly_chart(fig)
elif metric_selection:
    st.write(f"### {metric_selection} Charts")
    fig = plot_metric(daily_df, metric_selection)
    st.plotly_chart(fig)
