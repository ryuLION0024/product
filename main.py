import streamlit as st
import matplotlib.pyplot as plt

# タイトル
st.title("生産量計算アプリ")

# 入力フォーム
st.subheader("目標生産量と前日までのストックをスライダーで指定してください")

# 各ハムの目標生産量と前日のストックをスライダーで指定
Ham_targets = []
Ham_stocks = []
for i in range(1, 6):  # ハム1〜ハム5
    Ham_targets.append(st.slider(f'Ham{i} 目標生産量', min_value=0, max_value=100, step=1))
    Ham_stocks.append(st.slider(f'Ham{i} 前日までのストック', min_value=0, max_value=50, step=1))

# 余剰生産割合
surplus_ratio = st.slider('余剰生産割合 (1.0 = 100%)', min_value=1.0, max_value=1.5, step=0.1)

# ラインの設定
lines = {
    'A': {'capacity': 10},  # ラインA
    'B': {'capacity': 20},  # ラインB
}

# ボタンが押されたときに計算を実行
if st.button('計算を実行'):
    # 余剰生産の上限
    max_ham_production = [Ham_targets[i] * surplus_ratio for i in range(5)]

    # ラインの稼働時間と生産量を初期化
    available_hours_a = 8  # ラインAの残り稼働時間
    available_hours_b = 8  # ラインBの残り稼働時間
    line_production = {'A': {}, 'B': {}}
    line_hours = {'A': {}, 'B': {}}
    
    total_production = {f'Ham{i+1}': 0 for i in range(5)}

    # 各ハムについて計算
    for i in range(5):  # ハム1〜ハム5
        ham_name = f'Ham{i+1}'
        ham_target = Ham_targets[i]

        # ハムの生産（まずラインAで）
        if ham_target > 0 and available_hours_a > 0:
            production_hours_a = min(available_hours_a, ham_target / lines['A']['capacity'])
            production_amount_a = int(production_hours_a * lines['A']['capacity'])
            total_production[ham_name] += production_amount_a
            line_production['A'][ham_name] = production_amount_a
            line_hours['A'][ham_name] = production_hours_a
            available_hours_a -= production_hours_a  # ラインAの残り稼働時間を更新

            # ラインAで目標を達成できなければ、ラインBで補う
            remaining_ham = ham_target - production_amount_a
            if remaining_ham > 0 and available_hours_b > 0:
                production_hours_b = min(available_hours_b, remaining_ham / lines['B']['capacity'])
                production_amount_b = int(production_hours_b * lines['B']['capacity'])
                total_production[ham_name] += production_amount_b
                line_production['B'][ham_name] = production_amount_b
                line_hours['B'][ham_name] = production_hours_b
                available_hours_b -= production_hours_b

    # 結果表示
    st.subheader("生産結果")
    for i in range(5):
        st.write(f'Ham{i+1} 最終生産量: {total_production[f"Ham{i+1}"]} 個')

    # 棒グラフの可視化
    st.subheader("ラインごとの生産時間")
    labels = ['Line A', 'Line B']

    # 各ハムの時間をリスト化
    ham_hours_a = [line_hours['A'].get(f'Ham{i+1}', 0) for i in range(5)]
    ham_hours_b = [line_hours['B'].get(f'Ham{i+1}', 0) for i in range(5)]

    fig, ax = plt.subplots()

    # ハムごとに積み上げ棒グラフを作成
    bottom_a = [0] * 2  # ラインAとラインBの積み上げ開始点
    bottom_b = [0] * 2

    for i in range(5):
        ax.bar(labels, [ham_hours_a[i], ham_hours_b[i]], bottom=bottom_a, label=f'Ham{i+1}')
        bottom_a = [sum(x) for x in zip(bottom_a, [ham_hours_a[i], ham_hours_b[i]])]

    ax.set_ylabel('Hours Produced')
    ax.set_title('Production Hours by Line')
    ax.legend()

    st.pyplot(fig)
