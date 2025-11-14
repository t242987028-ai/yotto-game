import streamlit as st
import random

st.set_page_config(page_title="スマホ対応ヤッツィ", layout="centered")

# ----------------------------
# 初期化
# ----------------------------
if "dice" not in st.session_state:
    st.session_state.dice = [1, 2, 3, 4, 5]

if "locked" not in st.session_state:
    st.session_state.locked = [False] * 5

if "rolls_left" not in st.session_state:
    st.session_state.rolls_left = 3

if "score" not in st.session_state:
    st.session_state.score = {}

# ----------------------------
# CSS: スマホ対応
# ----------------------------
st.markdown("""
<style>
/* サイコロのスタイル */
.dice {
    display: inline-block;
    margin: 5px;
    padding: 20px 15px;
    font-size: 3rem;
    border: 2px solid #555;
    border-radius: 10px;
    text-align: center;
    cursor: pointer;
    user-select: none;
    background-color: #f0f0f0;
    transition: all 0.2s;
}
.dice.locked {
    background-color: #aaa;
    color: #fff;
}

/* ボタン大きめ */
.stButton > button {
    padding: 1.25rem 1.5rem;
    font-size: 1.25rem;
}

/* スマホ向け縦並び */
@media (max-width: 480px) {
    .dice {
        font-size: 4rem;
        padding: 25px 20px;
        margin: 10px auto;
        width: 60px;
    }
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# サイコロ操作
# ----------------------------
st.header("🎲 スマホ対応ヤッツィ")

cols = st.columns(5)
for i, col in enumerate(cols):
    dice_html = f'<div class="dice {"locked" if st.session_state.locked[i] else ""}" id="dice{i}">{st.session_state.dice[i]}</div>'
    col.markdown(dice_html, unsafe_allow_html=True)
    # サイコロクリックはセッションで代用
    if col.button(f"🔒 {i+1}" if not st.session_state.locked[i] else f"🔓 {i+1}"):
        st.session_state.locked[i] = not st.session_state.locked[i]

# ----------------------------
# サイコロを振る
# ----------------------------
def roll_dice():
    for i in range(5):
        if not st.session_state.locked[i]:
            st.session_state.dice[i] = random.randint(1, 6)
    st.session_state.rolls_left -= 1

if st.button(f"🎲 振る ({st.session_state.rolls_left}回残り)"):
    if st.session_state.rolls_left > 0:
        roll_dice()
    else:
        st.warning("もう振れません！スコアを選んでください。")

# ----------------------------
# スコアカード
# ----------------------------
st.subheader("📊 スコアカード")

def score_upper(n):
    return st.session_state.dice.count(n) * n

def score_three_kind():
    for i in range(1,7):
        if st.session_state.dice.count(i) >= 3:
            return sum(st.session_state.dice)
    return 0

def score_four_kind():
    for i in range(1,7):
        if st.session_state.dice.count(i) >= 4:
            return sum(st.session_state.dice)
    return 0

def score_full_house():
    counts = [st.session_state.dice.count(i) for i in range(1,7)]
    if 3 in counts and 2 in counts:
        return 25
    return 0

def score_small_straight():
    straights = [{1,2,3,4},{2,3,4,5},{3,4,5,6}]
    dice_set = set(st.session_state.dice)
    for s in straights:
        if s.issubset(dice_set):
            return 30
    return 0

def score_large_straight():
    straights = [{1,2,3,4,5},{2,3,4,5,6}]
    dice_set = set(st.session_state.dice)
    for s in straights:
        if s == dice_set:
            return 40
    return 0

def score_yahtzee():
    if len(set(st.session_state.dice)) == 1:
        return 50
    return 0

def score_chance():
    return sum(st.session_state.dice)

# 上段
with st.expander("🔢 数字カテゴリ"):
    for i in range(1,7):
        key = f"{i}"
        if key not in st.session_state.score:
            if st.button(f"{i} の得点 ({score_upper(i)}点)"):
                st.session_state.score[key] = score_upper(i)
                st.session_state.rolls_left = 3
                st.session_state.locked = [False]*5

# 下段
with st.expander("🎯 役カテゴリ"):
    categories = {
        "Three of a kind": score_three_kind,
        "Four of a kind": score_four_kind,
        "Full House": score_full_house,
        "Small Straight": score_small_straight,
        "Large Straight": score_large_straight,
        "Yahtzee": score_yahtzee,
        "Chance": score_chance
    }
    for key, func in categories.items():
        if key not in st.session_state.score:
            if st.button(f"{key} ({func()}点)"):
                st.session_state.score[key] = func()
                st.session_state.rolls_left = 3
                st.session_state.locked = [False]*5

# ----------------------------
# 合計表示
# ----------------------------
st.subheader("🏆 得点")
total = sum(st.session_state.score.values())
for k,v in st.session_state.score.items():
    st.write(f"{k}: {v}")
st.write(f"**合計: {total}点**")

