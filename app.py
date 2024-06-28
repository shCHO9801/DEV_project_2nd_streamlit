import streamlit as st
import pandas as pd
import os
import io
import json
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

# Google Drive API를 사용할 범위 설정
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 환경 변수에서 OAuth 클라이언트 정보 가져오기
oauth_secrets = st.secrets["oauth"]
client_id = oauth_secrets["client_id"]
client_secret = oauth_secrets["client_secret"]
redirect_uri = oauth_secrets["redirect_uri"]

# 사용자 인증을 처리하는 함수
def authenticate_gdrive():
    if "credentials" not in st.session_state:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = redirect_uri

        auth_url, _ = flow.authorization_url(prompt="consent")

        st.write(f"로그인을 위해 [여기]({auth_url})를 클릭하세요.")

        auth_code = st.text_input("인증 코드 입력:")

        if auth_code:
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            st.session_state.credentials = credentials
            st.experimental_rerun()

    credentials = st.session_state.credentials
    return credentials

# Google Drive에서 파일 목록 가져오기
def list_files_in_folder(folder_id):
    creds = authenticate_gdrive()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(q=f"'{folder_id}' in parents",
                                   pageSize=1000,
                                   fields="files(id, name)").execute()
    items = results.get('files', [])
    return items

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

# 데이터 미리보기
for i, df in dataframes.items():
    st.write(f"### 데이터 미리보기 {i}")
    st.dataframe(df.head())

# 데이터 통계
for i, df in dataframes.items():
    st.write(f"### 기본 통계 {i}")
    st.write(df.describe())
