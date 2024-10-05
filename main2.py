import streamlit as st
import pandas as pd

# タイトル
st.title("生産計画計算アプリ")

# 入力欄（ユーザーがデータを入力）
st.header("生産情報を入力してください")

# 入力フォーム
products = ['A', 'B', 'C', 'D', 'E', 'F']
data = {}
for product in products:
    data[f'{product}_day_order'] = st.number_input(f'{product} 当日の受注量', min_value=0, max_value=5000, value=100)
    data[f'{product}_4d_order'] = st.number_input(f'{product} 4日間の受注量合計', min_value=0, max_value=5000, value=500)
    data[f'{product}_stock'] = st.number_input(f'{product} 在庫量', min_value=0, max_value=5000, value=100)

# 生産能力（1時間あたりの生産量）
corrected_production_capacity = {
    'A': 1 / 0.0125,  # 80 ケース/時間
    'B': 1 / 0.09375,  # 約10.67 ケース/時間
    'C': 1 / 0.0125,   # 80 ケース/時間
    'D': 1 / 0.025,    # 40 ケース/時間
    'E': 1 / 0.09375,  # 約10.67 ケース/時間
    'F': 1 / 0.004688  # 約213.37 ケース/時間
}

# データフレームを構築
df = pd.DataFrame({
    '商品': products,
    '当日の受注量': [data[f'{product}_day_order'] for product in products],
    '4日間の受注量合計': [data[f'{product}_4d_order'] for product in products],
    '在庫': [data[f'{product}_stock'] for product in products]
})

# 計算: 当日の受注残を計算
df['当日受注残'] = df['当日の受注量'] - df['在庫']

# 生産時間を計算（4日間の受注残を上回らないように制限）
df['生産時間'] = df.apply(lambda row: min(max(0, row['当日受注残'] / corrected_production_capacity[row['商品']]), row['4日間の受注量合計'] / corrected_production_capacity[row['商品']]), axis=1)

# 結果表示
st.header("計算結果")
st.write(df[['商品', '当日の受注量', '在庫', '当日受注残', '生産時間']])

# 1号機と2号機の生産を割り当て
st.header("1号機と2号機での生産計画")

# 受注残が多い順に並べて、1号機と2号機に生産割り当て
df = df.sort_values(by='当日受注残', ascending=False)
st.write(f"1号機で生産: {df.iloc[0]['商品']} （生産時間: {df.iloc[0]['生産時間']} 時間）")
st.write(f"2号機で生産: {df.iloc[1]['商品']} （生産時間: {df.iloc[1]['生産時間']} 時間）")

# 残り時間での追加生産
remaining_hours_1 = 14 - df.iloc[0]['生産時間']
remaining_hours_2 = 14 - df.iloc[1]['生産時間']

# 残りの時間を使って次の生産
remaining_items = df.iloc[2:]  # 3番目以降の商品
remaining_items = remaining_items.sort_values(by='4日間の受注量合計', ascending=False)

# 追加生産ロジック
def calculate_additional_production(row, remaining_hours, first_product_remaining_hours):
    # 4日間の受注残を上回らないように制限
    max_production_time = row['4日間の受注量合計'] / corrected_production_capacity[row['商品']]
    production_time = min(remaining_hours, max_production_time)
    remaining_hours -= production_time
    # もし時間が余った場合は最初に生産した商品を追加
    if remaining_hours > 0:
        production_time += min(remaining_hours, first_product_remaining_hours)
    return production_time

# 1号機の追加生産
first_product_remaining_hours_1 = df.iloc[0]['4日間の受注量合計'] / corrected_production_capacity[df.iloc[0]['商品']] - df.iloc[0]['生産時間']
product_f_time = calculate_additional_production(remaining_items.iloc[0], remaining_hours_1, first_product_remaining_hours_1)

# 2号機の追加生産
first_product_remaining_hours_2 = df.iloc[1]['4日間の受注量合計'] / corrected_production_capacity[df.iloc[1]['商品']] - df.iloc[1]['生産時間']
product_e_time = calculate_additional_production(remaining_items.iloc[1], remaining_hours_2, first_product_remaining_hours_2)

# 結果を表示
st.write(f"1号機で次に生産: {remaining_items.iloc[0]['商品']} （生産時間: {product_f_time} 時間）")
st.write(f"2号機で次に生産: {remaining_items.iloc[1]['商品']} （生産時間: {product_e_time} 時間）")
