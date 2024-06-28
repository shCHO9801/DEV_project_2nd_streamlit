# 프로젝트 설명
- 파이썬 기반 데이터 시각화
- 주제 : Electronic Stores Ecommerce 로그 데이터를 활용한 AARRR 기반 비즈니스 지표 설계 및 대시보드 개발
	- Data : https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store
- 목표
  - Pandas를 활용한 EDA
  - AARRR 프레임워크 기반 비지니스 지표 설계 및 추출
  - 비지니스 지표를 활용한 자료 시각화
  - Streamlit을 활용한 대시보드 제작
    
# Streamlit URL
- https://devproject2ndapp-cmt6w4xb7dafxmygejzwcj.streamlit.app/Acquisition
  
# Role
- 김상준: 활성화, 수익 지표 설계 / 유입 대시보드 제작
- 문규림: 유입, 재방문 지표 설계 / 수익 대시보드 제작
- 조성현: 유입, 수익 지표 설계 / 활성화 대시보드 제작
- 복선혜: 활성화, 재방문 지표 설계 / 재방문 대시보드 제작
  
# 파일 설명
- 01.EDA
	- 각 팀원별 EDA jupyter notebook
- 02.지표설계(일자별)
	- AARRR프레임워크 기반 일자별 지표설계 jupyter notebook
- 03.지표설계(유저별)
	- AARRR 프레임워크 기반 유저별 지표설계 jupyter notebook
- 04.시각화
	- 각 파트별 시각화 결과
- Streamlit
	- main.csv : kaggle Ecommers data set 
	- user.csv : 유저별 지표설계 데이터셋
  - daily.csv : 일자별 지표설계 데이터셋
  - requirements.txt : Streamlit 로드시 import할 라이브러리 버전
  - app.py : streamlit 메인 페이지
  - pages : 하위 페이지 디렉토리
 	- 1_Acqusition.py : Acqusition part page py
	- 2_Avtivation.py : Activation part page py
	- 3_Retention.py : Retention part page py
	- 4_Revenue.py : Revenue part page py
