import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import os

# 로컬 CSV 파일 경로 지정
file_path_daily = os.path.join(os.path.dirname(__file__), '..', 'daily.csv')
file_path_user = os.path.join(os.path.dirname(__file__), '..', 'user_new.csv')


# CSV 파일 로드
day_df = pd.read_csv(file_path_daily)
user_df = pd.read_csv(file_path_user)

# 날짜 변환
day_df['event_date'] = pd.to_datetime(day_df['event_date'])
user_df['last_event_time'] = pd.to_datetime(user_df['last_event_time'], errors='coerce')
user_df['first_visit'] = pd.to_datetime(user_df['first_visit'], errors='coerce')

# fig 1, 2
def create_retention_figure(dates, retention_data, title, yaxis_title):
    fig = go.Figure()
    colors = ['rgba(55, 83, 109, 0.6)', 'rgba(26, 118, 255, 0.6)', 'rgba(50, 171, 96, 0.6)', 'rgba(255, 140, 0, 0.6)']
    names = ['1-Day', '3-Day', '7-Day', '30-Day']

    for data, color, name in zip(retention_data, colors, names):
        fig.add_trace(go.Scatter(
            x=dates, y=data, mode='lines', name=name,
            line=dict(color=color)
        ))

    tickvals = pd.date_range(start=dates.min(), end=dates.max(), freq='1W')
    ticktext = [date.strftime('%Y-%m-%d') for date in tickvals]

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=yaxis_title,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=45
        ),
        legend=dict(
            orientation='h',
            x=0.5,
            y=1.15,
            xanchor='center'
        ),
        template='plotly_white'
    )
    return fig

dates = day_df['event_date']
retention_data = [day_df['1-Day Retention Rate (%)'], day_df['3-Day Retention Rate (%)'], day_df['7-Day Retention Rate (%)'], day_df['30-Day Retention Rate (%)']]
purchase_retention_data = [day_df['1-Day Purchase Retention Rate (%)'], day_df['3-Day Purchase Retention Rate (%)'], day_df['7-Day Purchase Retention Rate (%)'], day_df['30-Day Purchase Retention Rate (%)']]

fig1 = create_retention_figure(dates, retention_data, 'Retention Rates Over Time', 'Retention Rate (%)')
fig2 = create_retention_figure(dates, purchase_retention_data, 'Purchase Retention Rates Over Time', 'Purchase Retention Rate (%)')

# fig 3, 4
def create_retention_diff_figure(df, diff_columns, title, yaxis_title):
    fig = go.Figure()
    colors = ['rgba(255, 204, 0, 0.6)', 'rgba(34, 139, 34, 0.6)', 'rgba(26, 118, 255, 0.6)']
    new_colors = ['rgba(34, 139, 34, 0.6)', 'rgba(26, 118, 255, 0.6)', 'rgba(255, 204, 0, 0.6)']
    names = ['7d to 30d Diff', '1d to 3d Diff', '3d to 7d Diff']
    new_names = ['1d to 3d Diff', '3d to 7d Diff', '7d to 30d Diff']
    legendgroups = ['1', '2', '3']
    new_legendgroups = ['2', '3', '1']

    for col, color, name, group in zip(diff_columns, colors, names, legendgroups):
        fig.add_trace(go.Bar(
            x=df['event_date'],
            y=df[col],
            name=name,
            marker_color=color,
            legendgroup=group,
            showlegend=False
        ))

    # 각 그룹에 대한 레전드 순서 변경
    for name, color, group in zip(new_names, new_colors, new_legendgroups):
        fig.add_trace(go.Bar(
            x=[None],
            y=[None],
            name=name,
            marker_color=color,
            legendgroup=group,
            # showlegend=True
        ))

    tickvals = pd.date_range(start=df['event_date'].min(), end=df['event_date'].max(), freq='W')
    ticktext = tickvals.strftime('%Y-%m-%d')

    fig.update_layout(
        title=title,
        xaxis_tickfont_size=14,
        yaxis=dict(
            title=yaxis_title,
            titlefont_size=16,
            tickfont_size=14,
        ),
        xaxis=dict(
            title='Event Date',
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=45
        ),
        legend=dict(
            orientation='h',
            x=0,
            y=1.1,
            tracegroupgap=0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='overlay',
        bargap=0.15,
        bargroupgap=0.1
    )
    return fig

retention_diff_df = pd.DataFrame({
    'event_date': day_df['event_date'],
    '1d_to_3d_diff': day_df['3-Day Retention Rate (%)'] - day_df['1-Day Retention Rate (%)'],
    '3d_to_7d_diff': day_df['7-Day Retention Rate (%)'] - day_df['3-Day Retention Rate (%)'],
    '7d_to_30d_diff': day_df['30-Day Retention Rate (%)'] - day_df['7-Day Retention Rate (%)']
})

purchase_retention_diff_df = pd.DataFrame({
    'event_date': day_df['event_date'],
    '1d_to_3d_diff': day_df['3-Day Purchase Retention Rate (%)'] - day_df['1-Day Purchase Retention Rate (%)'],
    '3d_to_7d_diff': day_df['7-Day Purchase Retention Rate (%)'] - day_df['3-Day Purchase Retention Rate (%)'],
    '7d_to_30d_diff': day_df['30-Day Purchase Retention Rate (%)'] - day_df['7-Day Purchase Retention Rate (%)']
})

fig3 = create_retention_diff_figure(retention_diff_df, ['7d_to_30d_diff', '1d_to_3d_diff', '3d_to_7d_diff'], 'Retention Rate Differences Over Time', 'Retention Rate Difference (%)')
fig4 = create_retention_diff_figure(purchase_retention_diff_df, ['7d_to_30d_diff', '1d_to_3d_diff', '3d_to_7d_diff'], 'Purchase Retention Rate Differences Over Time', 'Purchase Retention Rate Difference (%)')

# fig 5
# NaN 값 제거 및 계산
filtered_data = user_df.dropna(subset=['last_event_time'])
max_event_time = filtered_data['last_event_time'].max()
filtered_data['days_since_last_event'] = (max_event_time - filtered_data['last_event_time']).dt.days
filtered_data['days_since_first_visit'] = user_df['days_since_first_visit']
filtered_data = filtered_data[filtered_data['days_since_last_event'] != float('inf')]

# 가입자 수 계산
user_counts = filtered_data.groupby('days_since_first_visit')['user_id'].nunique().reset_index()
user_counts.rename(columns={'user_id': 'total_users'}, inplace=True)

# 이탈한 사용자 수 계산
churn_counts = filtered_data.groupby(['days_since_first_visit', 'days_since_last_event'])['user_id'].nunique().reset_index()
churn_counts.rename(columns={'user_id': 'churned_users'}, inplace=True)

# Churn rate 계산
churn_rate_data = pd.merge(churn_counts, user_counts, on='days_since_first_visit')
churn_rate_data['churn_rate'] = churn_rate_data['churned_users'] / churn_rate_data['total_users'] * 100

first_day_mask = churn_rate_data['days_since_first_visit'] == churn_rate_data['days_since_last_event']
chart_data = churn_rate_data[first_day_mask]
chart_data = chart_data.iloc[1:,:]

# 히트맵 시각화
fig_blues = px.line(chart_data, x='days_since_first_visit', y='churn_rate',
                    title='가입 기간별 가입 당일 이탈률(Churn Rate)',
                    labels={'days_since_first_visit': '가입 기간(일)', 'days_since_last_event': '미방문 기간(일)', 'churn_rate': 'Churn Rate(%)'})

# 라인의 색상 설정
fig_blues.update_traces(line=dict(color='rgba(55, 83, 109, 0.6)'))

# 추가 설명 추가
fig_blues.add_annotation(
    xref='paper', yref='paper', x=0.0, y=-0.31,
    showarrow=False, text='* 데이터에 가입일 및 탈퇴일은 명시되어 있지 않았으나, user_id별 첫 user_session 발생일을 가입일이라 가정<br>'
                            '* 마지막 방문 이후 재방문이 일어나지 않은 경우, 이탈로 간주',
    font=dict(size=12),
    align='left',
    xanchor='left'
)

# 페이지 설정
st.title("리텐션(Retention) 지표")

# 차트 선택
metrics = [
    "Visit_Retention", "Visit_Purchase_Retention"
]
metric_selection = st.selectbox("시각화할 지표를 선택하세요", metrics)

# 차트 그리기
if metric_selection == "Visit_Retention":
    # st.write("### Retention Rates 차트")
    st.plotly_chart(fig1)
    # st.write("### Retention Rates Difference 차트")
    st.plotly_chart(fig3)
    # st.write("### Retention Rate Trend Over Time 차트")
    st.plotly_chart(fig_blues)
elif metric_selection == "Visit_Purchase_Retention":
    # st.write("### Purchase Retention Rates 차트")
    st.plotly_chart(fig2)
    # st.write("### Purchase Retention Rates Difference 차트")
    st.plotly_chart(fig4)
