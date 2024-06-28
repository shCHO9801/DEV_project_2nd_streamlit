import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 로컬 CSV 파일 경로 지정
file_path2 = os.path.join(os.path.dirname(__file__), '..', 'daily.csv')

# CSV 파일 로드
daily_df = pd.read_csv(file_path2)
daily_df['event_date'] = pd.to_datetime(daily_df['event_date'])

# DAU와 DAS 시각화 함수
def plot_metric(df, metric):
    fig = px.line(df, x='event_date', y=metric, title=f'{metric} over Time', markers=True)
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title=metric,
        xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10),  # 10일 간격 설정
        title={'x': 0.5},  # 제목을 중앙으로 정렬
        width=1000,  # 너비 설정
        height=500  # 높이 설정
    )
    return fig

def plot_combined_metrics(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['event_date'], y=df['DAU'], mode='lines+markers', name='DAU', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['event_date'], y=df['DAS'], mode='lines+markers', name='DAS', line=dict(color='red')))
    
    fig.update_layout(
        title='DAU와 DAS over Time',
        xaxis_title='Date',
        yaxis_title='Value',
        xaxis=dict(tickformat='%Y-%m-%d', dtick=86400000.0 * 10),  # 10일 간격 설정
        legend=dict(x=0.01, y=0.99),  # 범례 위치 설정
        width=1000,  # 너비 설정
        height=500  # 높이 설정
    )
    return fig

# 페이지 설정
st.title("유입(Acquisition) 지표")

# 차트 선택
metric_selection = st.selectbox("시각화할 지표를 선택하세요", ["DAU", "DAS", "DAU와 DAS"])

# 차트 그리기
if metric_selection == "DAU":
    st.write("### DAU 차트")
    fig = plot_metric(daily_df, "DAU")
    st.plotly_chart(fig)
elif metric_selection == "DAS":
    st.write("### DAS 차트")
    fig = plot_metric(daily_df, "DAS")
    st.plotly_chart(fig)
elif metric_selection == "DAU와 DAS":
    st.write("### DAU와 DAS 차트")
    fig = plot_combined_metrics(daily_df)
    st.plotly_chart(fig)
