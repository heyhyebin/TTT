import pandas as pd
import numpy as np
import glob
import os

# 1. 문자열 데이터를 숫자로 변환하는 함수
def clean_value(val):
    if pd.isna(val) or val == '-':
        return 0.0
    if isinstance(val, str):
        if '-' in val:
            try:
                low, high = map(float, val.split('-'))
                return (low + high) / 2
            except:
                return 0.0
        if 'max' in val.lower():
            try:
                return float(val.lower().replace('max.', '').strip())
            except:
                return 0.0
    try:
        return float(val)
    except:
        return 0.0

# 2. 성분 데이터 읽기
alloys = pd.read_excel('alloys1.xlsx')

# 주요 원소 버전
# elements = ['C', 'Mn', 'Si', 'Ni', 'Cr', 'Mo', 'V', 'Cu']

# 전체 원소 버전으로 바꾸고 싶으면 위 줄 대신 아래 사용
elements = [
    'C', 'Fe', 'Mn', 'Si', 'Al', 'Ni', 'Cr', 'Mo', 'Cu',
    'Ti', 'Nb', 'V', 'Co', 'W', 'P', 'S', 'B', 'N', 'Sn',
    'Re', 'O', 'Zr'
]

for col in elements:
    if col in alloys.columns:
        alloys[col] = alloys[col].apply(clean_value)

alloys = alloys.set_index('diagram No')

# 3. 곡선 파일들 읽기
path = './엑셀'
all_files = glob.glob(os.path.join(path, '*.xlsx'))

final_dataset = []

for file in all_files:
    try:
        file_name = os.path.basename(file)
        diagram_no = int(os.path.splitext(file_name)[0])

        if diagram_no not in alloys.index:
            continue

        comp_info = alloys.loc[diagram_no]

        curve_data = pd.read_excel(
            file,
            header=None,
            names=[
                't01_time', 't01_temp',
                't50_time', 't50_temp',
                't99_time', 't99_temp'
            ]
        )

        curve_data = curve_data.dropna(how='all')

        for _, row in curve_data.iterrows():
            curve_map = {
                '0.01T': ('t01_time', 't01_temp'),
                '0.50T': ('t50_time', 't50_temp'),
                '0.99T': ('t99_time', 't99_temp')
            }

            for curve_id, (time_col, temp_col) in curve_map.items():
                if pd.notna(row[time_col]) and pd.notna(row[temp_col]):
                    data_row = {
                        'diagram_no': diagram_no,
                        'time': row[time_col],
                        'temperature': row[temp_col],
                        'curve_id': curve_id
                    }

                    # 원소 정보 자동 추가
                    for elem in elements:
                        data_row[elem] = comp_info.get(elem, 0.0)

                    final_dataset.append(data_row)

    except Exception as e:
        print(f"파일 처리 중 오류 발생 ({file}): {e}")

df_final = pd.DataFrame(final_dataset)

# 숫자형 변환
df_final['time'] = pd.to_numeric(df_final['time'], errors='coerce')
df_final['temperature'] = pd.to_numeric(df_final['temperature'], errors='coerce')

# NaN 제거
df_final = df_final.dropna(subset=['time', 'temperature'])

# 이상치 제거
df_final = df_final[
    (df_final['time'] > 0) &
    (df_final['temperature'] > 200) &
    (df_final['temperature'] < 1300)
]

print(f"총 {len(df_final)}개의 데이터 포인트가 수집되었습니다.")
print(df_final.head())

df_final.to_excel('ttt_total_dataset.xlsx', index=False)
print("통합 데이터 저장 완료: ttt_total_dataset.xlsx")

# nose 추출
df_001 = df_final[df_final['curve_id'] == '0.01T'].copy()
idx = df_001.groupby('diagram_no')['time'].idxmin()
nose_df = df_001.loc[idx].reset_index(drop=True)

nose_df = nose_df.rename(columns={
    'time': 'nose_time',
    'temperature': 'nose_temperature'
})

nose_df.to_excel('ttt_nose_dataset.xlsx', index=False)
print("nose 데이터 저장 완료: ttt_nose_dataset.xlsx")

print("\n=== nose 데이터 예시 ===")
print(nose_df.head())
print(f"총 {len(nose_df)}개 합금의 nose 추출 완료")
