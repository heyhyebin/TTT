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

elements = ['C', 'Mn', 'Si', 'Ni', 'Cr', 'Mo', 'V', 'Cu']
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
        diagram_no = int(os.path.splitext(file_name)[0])  # 예: 7.xlsx -> 7

        if diagram_no not in alloys.index:
            continue

        comp_info = alloys.loc[diagram_no]

        # 헤더를 직접 지정해서 읽기
        curve_data = pd.read_excel(
            file,
            header=None,
            names=[
                't01_time', 't01_temp',
                't50_time', 't50_temp',
                't99_time', 't99_temp'
            ]
        )

        # 빈 행 제거
        curve_data = curve_data.dropna(how='all')

        for _, row in curve_data.iterrows():
            # 0.01T
            if pd.notna(row['t01_time']) and pd.notna(row['t01_temp']):
                final_dataset.append({
                    'diagram_no': diagram_no,
                    'C': comp_info.get('C', 0.0),
                    'Mn': comp_info.get('Mn', 0.0),
                    'Si': comp_info.get('Si', 0.0),
                    'Ni': comp_info.get('Ni', 0.0),
                    'Cr': comp_info.get('Cr', 0.0),
                    'Mo': comp_info.get('Mo', 0.0),
                    'V': comp_info.get('V', 0.0),
                    'Cu': comp_info.get('Cu', 0.0),
                    'time': row['t01_time'],
                    'temperature': row['t01_temp'],
                    'curve_id': '0.01T'
                })

            # 0.50T
            if pd.notna(row['t50_time']) and pd.notna(row['t50_temp']):
                final_dataset.append({
                    'diagram_no': diagram_no,
                    'C': comp_info.get('C', 0.0),
                    'Mn': comp_info.get('Mn', 0.0),
                    'Si': comp_info.get('Si', 0.0),
                    'Ni': comp_info.get('Ni', 0.0),
                    'Cr': comp_info.get('Cr', 0.0),
                    'Mo': comp_info.get('Mo', 0.0),
                    'V': comp_info.get('V', 0.0),
                    'Cu': comp_info.get('Cu', 0.0),
                    'time': row['t50_time'],
                    'temperature': row['t50_temp'],
                    'curve_id': '0.50T'
                })

            # 0.99T
            if pd.notna(row['t99_time']) and pd.notna(row['t99_temp']):
                final_dataset.append({
                    'diagram_no': diagram_no,
                    'C': comp_info.get('C', 0.0),
                    'Mn': comp_info.get('Mn', 0.0),
                    'Si': comp_info.get('Si', 0.0),
                    'Ni': comp_info.get('Ni', 0.0),
                    'Cr': comp_info.get('Cr', 0.0),
                    'Mo': comp_info.get('Mo', 0.0),
                    'V': comp_info.get('V', 0.0),
                    'Cu': comp_info.get('Cu', 0.0),
                    'time': row['t99_time'],
                    'temperature': row['t99_temp'],
                    'curve_id': '0.99T'
                })

    except Exception as e:
        print(f"파일 처리 중 오류 발생 ({file}): {e}")

df_final = pd.DataFrame(final_dataset)

print(f"총 {len(df_final)}개의 데이터 포인트가 수집되었습니다.")
print(df_final.head())

# 4. 통합 데이터 저장
df_final.to_excel('ttt_total_dataset.xlsx', index=False)
print("통합 데이터 저장 완료: ttt_total_dataset.xlsx")

# 5. 0.01T만 선택
df_001 = df_final[df_final['curve_id'] == '0.01T'].copy()

# 6. 각 diagram_no별 최소 time 위치 찾기
idx = df_001.groupby('diagram_no')['time'].idxmin()

# 7. nose 데이터 추출
nose_df = df_001.loc[idx].reset_index(drop=True)

# 8. 컬럼 이름 보기 좋게 변경
nose_df = nose_df.rename(columns={
    'time': 'nose_time',
    'temperature': 'nose_temperature'
})

# 9. nose 데이터 저장
nose_df.to_excel('ttt_nose_dataset.xlsx', index=False)
print("nose 데이터 저장 완료: ttt_nose_dataset.xlsx")

# 10. 확인
print("\n=== nose 데이터 예시 ===")
print(nose_df.head())
print(f"총 {len(nose_df)}개 합금의 nose 추출 완료")
