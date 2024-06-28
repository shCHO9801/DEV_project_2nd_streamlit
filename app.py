import streamlit as st
import pandas as pd
import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API를 사용할 범위 설정
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# OAuth 2.0 인증
def authenticate_gdrive():
    creds = None
    # token.json 파일이 있다면 기존 인증 정보를 로드
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 유효한 자격 증명이 없다면 새로 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 자격 증명을 token.json 파일에 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Google Drive에서 파일 다운로드
def download_file_from_gdrive(file_id):
    creds = authenticate_gdrive()
    service = build('drive', 'v3', credentials=creds)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh
# Google Drive에서 파일 목록 가져오기
def list_files_in_folder(folder_id):
    creds = authenticate_gdrive()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(q=f"'{folder_id}' in parents",
                                   pageSize=1000,
                                   fields="files(id, name)").execute()
    items = results.get('files', [])
    return items


# 폴더 ID 설정 (예: '1A2B3C4D5E6F')
folder_id = '1ME74_jO5elNQyHrlIJj3i6xTUvIA0Umo'

# 폴더 내 파일 목록 가져오기
files = list_files_in_folder(folder_id)

# 파일 목록 출력 및 사용자 선택
st.write("### Google Drive 폴더 내 파일 목록")
file_options = {file['name']: file['id'] for file in files}

# 여러 파일 선택을 위한 멀티 셀렉션 박스
selected_files = st.multiselect("파일을 선택하세요 (최대 4개):", list(file_options.keys()))

# 선택된 파일 ID 가져오기
selected_file_ids = [file_options[file_name] for file_name in selected_files]

# 선택된 파일을 다운로드하여 DataFrame으로 로드
dataframes = {}
for i, file_id in enumerate(selected_file_ids):
    downloaded_file = download_file_from_gdrive(file_id)
    df = pd.read_csv(downloaded_file)
    dataframes[f"df_{i+1}"] = df
# # 파일 ID로 Google Drive에서 파일 다운로드
# file_ids = {
#     "daily": "your-daily-file-id",
#     "main": "your-main-file-id",
#     "user_new": "your-user-new-file-id",
#     "user_csv": "your-user-csv-file-id"
# }

# # 파일을 다운로드하여 DataFrame으로 로드
# daily_file = download_file_from_gdrive(file_ids["daily"])
# main_file = download_file_from_gdrive(file_ids["main"])
# user_new_file = download_file_from_gdrive(file_ids["user_new"])
# user_csv_file = download_file_from_gdrive(file_ids["user_csv"])

# daily_df = pd.read_csv(daily_file)
# main_df = pd.read_csv(main_file)
# user_new_df = pd.read_csv(user_new_file)
# user_csv_df = pd.read_csv(user_csv_file)
################################
# # 현재 파일의 디렉토리 경로를 기준으로 상대 경로를 지정
# file_path = os.path.join(os.path.dirname(__file__), 'user_new.csv')
# file_path2 = os.path.join(os.path.dirname(__file__), 'daily.csv')

# # CSV 파일 로드
# user_df = pd.read_csv(file_path)
# daily_df = pd.read_csv(file_path2)

# Streamlit 앱 설정
st.title("AARRR 프레임워크 대시보드")

# 앱 소개
st.write("""
    AARRR 프레임워크 대시보드에 오신 것을 환영합니다. 이 대시보드는 고객 생애 주기의 다양한 단계에서 주요 지표를 분석하는 데 도움을 줍니다.
    왼쪽의 탭을 사용하여 대시보드의 다양한 섹션으로 이동하세요.
    """)

# AARRR 프레임워크 설명 및 네비게이션 안내
st.write("""
    ## 네비게이션
    - **유입(Acquisition)**: 사용자 획득 관련 지표를 확인합니다.
    - **활성화(Activation)**: 사용자 활성화 관련 지표를 확인합니다.
    - **재방문(Retention)**: 사용자 유지 관련 지표를 확인합니다.
    - **수익(Revenue)**: 사용자 수익 관련 지표를 확인합니다.
    """)

# 공통 지표 계산 함수
def calculate_aquisition_metrics(df):
    total_users = df['user_id'].nunique()
    new_users = df[df['first_visit'] >= '2023-01-01']['user_id'].nunique()  # 예시: 2023년 이후 신규 사용자
    return {
        "총 사용자 수": total_users,
        "신규 사용자 수 (2023)": new_users
    }

def calculate_activation_metrics(df):
    active_users = df[df['total_visit_cnt'] > 1]['user_id'].nunique()
    return {
        "활성 사용자 수": active_users
    }

def calculate_retention_metrics(df):
    retention_rate = df['30-Day Retention Rate (%)'].mean()
    return {
        "30일 유지율": retention_rate
    }

def calculate_revenue_metrics(df):
    total_revenue = df['total_spending'].sum()
    avg_revenue_per_user = df['total_spending'].mean()
    return {
        "총 수익": total_revenue,
        "사용자당 평균 수익": avg_revenue_per_user
    }

# 데이터 미리보기
st.write("### 데이터 미리보기")
st.write("#### 사용자 데이터")
st.dataframe(user_df.head())
st.write("#### 일별 데이터")
st.dataframe(daily_df.head())

# 공통 데이터 통계
st.write("### 기본 통계")
st.write("#### 사용자 데이터 통계")
st.write(user_df.describe())
st.write("#### 일별 데이터 통계")
st.write(daily_df.describe())

# 지표 설명을 위한 테이블 생성
# 가장 앞쪽에 추가

user = {
    'KPI': ['first_visit', 'total_session_cnt', 'total_visit_cnt', 'view_count', 
               'cart_count', 'purchase_count', 'last_event_time', 'days_since_first_visit', 
               'total_session_duration', 'avg_session_duration', 'total_spending', 
               'min_spending', 'max_spending', 'most_main_purchase', 'most_sub_purchase', 
               'most_sub_sub_purchase'],
               
    'Description': ['유저 첫 방문일', '유저별 누적 세션 수', '유저별 방문일 수', '유저별 view 이벤트 수', 
                    '유저별 cart 이벤트 수', '유저별 purchase 이벤트 수', '유저가 마지막으로 발생시킨 이벤트의 시간', 
                    '유저 첫 방문일로부터 지난 시간', '유저별 총 체류 시간', '유저별 평균 체류 시간', '유저별 누적 소비액', 
                    '유저별 최소 소비액', '유저별 최대 소비액', '유저별 가장 많이 구입한 주요 카테고리', 
                    '유저별 가장 많이 구입한 하위 카테고리', '유저별 가장 많이 구입한 세부 카테고리']
}

user_ = pd.DataFrame(user, columns=['KPI', 'Description'])

day = {
    'KPI': ['first_visit', 'total_session_cnt', 'total_visit_cnt', 'view_count', 'cart_count', 
               'purchase_count', 'last_event_time', 'days_since_first_visit', 'total_session_duration', 
               'avg_session_duration', 'total_spending', 'min_spending', 'max_spending', 
               'most_main_purchase', 'most_sub_purchase', 'most_sub_sub_purchase', 
               'DAU', 'DAS', 'sessions_per_user', 'unique_view_sessions', 'unique_cart_sessions', 
               'unique_purchase_sessions', 'unique_view_users', 'unique_cart_users', 
               'unique_purchase_users', 'total_purchase_amount', 'purchase_conversion_rate', 
               'ARPU', 'ARPS', 'high_brand_daily', 'AOV'],
               
    'Description': ['일자별 첫 방문일', '일자별 누적 세션 수', '일자별 방문일 수', '일자별 view 이벤트 수', 
                    '일자별 cart 이벤트 수', '일자별 purchase 이벤트 수', '일자별 마지막으로 발생시킨 이벤트의 시간', 
                    '첫 방문일로부터 지난 시간', '일자별 총 체류 시간', '일자별 평균 체류 시간', '일자별 누적 소비액', 
                    '일자별 최소 소비액', '일자별 최대 소비액', '일자별 가장 많이 구입한 주요 카테고리', 
                    '일자별 가장 많이 구입한 하위 카테고리', '일자별 가장 많이 구입한 세부 카테고리', 
                    'Daily Active Users (일일 활성 사용자 수)', 'Daily Active Sessions (일일 활성 세션 수)', 
                    '사용자당 평균 세션 수', '일자별 고유 view 세션 수', '일자별 고유 cart 세션 수', 
                    '일자별 고유 purchase 세션 수', '일자별 고유 view 사용자 수', '일자별 고유 cart 사용자 수', 
                    '일자별 고유 purchase 사용자 수', '일자별  총 구매 금액', '일자별 구매 전환율', 
                    '일자별 사용자당 평균 매출', '일자별 세션당 평균 매출', '일자별 최고 브랜드', '일자별 평균 주문 금액']
}

day_ = pd.DataFrame(day, columns=['KPI', 'Description'])

st.title("비즈니스 지표 요약")
st.write("")

st.write("유저별 비즈니스 지표")
st.dataframe(user_,height=200)

st.write("일자별 비즈니스 지표")
st.dataframe(day_, height=200)
