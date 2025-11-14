import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import random
from collections import Counter

# ページ設定
st.set_page_config(
    page_title="🎲 ヨットダイス",
    page_icon="🎲",
    layout="centered",
)

# -------------------------------
# パスワードハッシュ化
# -------------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

names = ["T", "N"]
usernames = ["Takahito", "Nanako"]
passwords = ["0628", "0408"]
hashed_passwords = [hash_password(p) for p in passwords]

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
        usernames[1]: {"name": names[1], "password": hashed_passwords[1]},
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="yacht_game",
    key="abcdef",
    cookie_expiry_days=30,
)

try:
    authenticator.login()
except Exception:
    pass

name = st.session_state.get("name")
auth_status = st.session_state.get("authentication_status")

# --------------------------------
# スマホ対応 CSS
# --------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* 全体背景 */
.stApp {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
    padding-bottom: 2rem;
}

/* ヘッダー */
.game-header {
    text-align: center;
    padding: 1.5rem 0.5rem;
}
.game-title {
    font-size: 2.3rem;
    font-weight: 700;
    color: #2e7d32;
}
.player-badge {
    background: #ffffff;
    padding: 0.4rem 1rem;
    border-radius: 1rem;
    border: 2px solid #66bb6a;
    font-size: 0.9rem;
}

/* ダイスコンテナ */
.dice-container {
    background: #ffffff;
    border: 3px solid #81c784;
    border-radius: 1.25rem;
    padding: 1rem;
    margin-top: 1rem;
}

/* ダイス（スマホで押しやすいサイズに変更） */
.dice {
    font-size: 2.8rem;
    background: #fffde7;
    border: 3px solid #fbc02d;
    border-radius: 0.75rem;
    padding: 0.7rem 0.3rem;
    width: 100%;
    text-align: center;
}
.dice-kept {
    background: #a5d6a7 !important;
    border-color: #4caf50 !important;
}

/* スマホでダイスの幅調整 */
@media (max-width: 480px) {
    .dice {
        font-size: 2.3rem;
        padding: 0.6rem 0.2rem;
    }
}

/* ボタン（スマホで押しやすい大きさ） */
.stButton > button {
    background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
    color: white;
    border: none;
    border-radius: 0.75rem;
    padding: 1rem;
    font-size: 1rem;
    width: 100%;
}

/* スマホは得点横幅を調整 */
.score-item {
    font-size: 0.95rem;
    padding: 0.8rem;
}

/* 合計スコア（スマホ縮小） */
.total-score-number {
    font-size: 2.6rem;
}

/* スマホでの余白改善 */
@media (max-width: 480px) {
    .total-score-number {
        font-size: 2.1rem;
    }
    .game-title {
        font-size: 1.9rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------
# ゲームロジック
# --------------------------------
dice_faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
secret_messages = [
    "🎊 すごい！ヨットマスター！",
    "✨ 運命の一振り！",
    "🌟 サイコロの神が微笑んだ！",
    "🎯 完璧なタイミング！",
    "🔥 伝説の出目！",
]

if auth_status:

    # ヘッダー
    st.markdown(
        f"""
        <div class='game-header'>
            <div class='game-title'>🎲 ヨットダイス</div>
            <div class='player-badge'>👤 {name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 初期化
    if "dice" not in st.session_state:
        st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
        st.session_state.rolls_left = 2
        st.session_state.keep = [False] * 5
        st.session_state.turn = 1
        st.session_state.easter_egg_found = []
        st.session_state.scores = {
            "upper": {"1": None, "2": None, "3": None, "4": None, "5": None, "6": None},
            "lower": {
                "choice": None,
                "four_of_kind": None,
                "full_house": None,
                "small_straight": None,
                "large_straight": None,
                "yacht": None,
            },
        }

    # --------------------------------
    # ダイス処理
    # --------------------------------
    def roll_dice():
        for i in range(5):
            if not st.session_state.keep[i]:
                st.session_state.dice[i] = random.randint(1, 6)
        st.session_state.rolls_left -= 1

    def calculate_score(category, dice):
        counts = Counter(dice)
        sorted_dice = sorted(dice)

        if category in ["1", "2", "3", "4", "5", "6"]:
            return dice.count(int(category)) * int(category)

        if category == "choice":
            return sum(dice)

        if category == "four_of_kind":
            return sum(dice) if max(counts.values()) >= 4 else 0

        if category == "full_house":
            return sum(dice) if sorted(counts.values()) == [2, 3] else 0

        if category == "small_straight":
            straights = [{1,2,3,4},{2,3,4,5},{3,4,5,6}]
            return 15 if any(s.issubset(dice) for s in straights) else 0

        if category == "large_straight":
            return 30 if sorted_dice in ([1,2,3,4,5],[2,3,4,5,6]) else 0

        if category == "yacht":
            return 50 if max(counts.values()) == 5 else 0

        return 0

    def fill_score(section, category):
        st.session_state.scores[section][category] = calculate_score(
            category, st.session_state.dice
        )
        st.session_state.turn += 1
        st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
        st.session_state.rolls_left = 2
        st.session_state.keep = [False] * 5

    # ---------------------
    # ダイス表示
    # ---------------------
    st.markdown("<div class='dice-container'>", unsafe_allow_html=True)
    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"<div class='dice {'dice-kept' if st.session_state.keep[i] else ''}'>{dice_faces[st.session_state.dice[i]]}</div>",
                unsafe_allow_html=True,
            )
            st.session_state.keep[i] = st.checkbox(
                "キープ", value=st.session_state.keep[i], key=f"keep{i}"
            )

    if st.session_state.rolls_left > 0:
        if st.button(f"🎲 振り直す（残り {st.session_state.rolls_left} ）"):
            roll_dice()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # スコアカード
    # -------------------------
    st.subheader("🔢 数字カテゴリ")

    for num in ["1", "2", "3", "4", "5", "6"]:
        if st.session_state.scores["upper"][num] is None:
            potential = calculate_score(num, st.session_state.dice)
            if st.button(f"{num} → {potential}点", key=f"U{num}"):
                fill_score("upper", num)
                st.rerun()
        else:
            st.write(f"{num}: {st.session_state.scores['upper'][num]}点 ✓")

    st.subheader("🎯 役カテゴリ")

    labels = {
        "choice": "チョイス",
        "four_of_kind": "フォーカード",
        "full_house": "フルハウス",
        "small_straight": "Sストレート",
        "large_straight": "Lストレート",
        "yacht": "ヨット",
    }

    for key, label in labels.items():
        if st.session_state.scores["lower"][key] is None:
            potential = calculate_score(key, st.session_state.dice)
            if st.button(f"{label} → {potential}点", key=f"L{key}"):
                fill_score("lower", key)
                st.rerun()
        else:
            st.write(f"{label}: {st.session_state.scores['lower'][key]}点 ✓")

    # -------------------------
    # 合計スコア
    # -------------------------
    upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
    bonus = 35 if upper_total >= 63 else 0
    lower_total = sum(s for s in st.session_state.scores["lower"].values() if s is not None)

    total_score = upper_total + bonus + lower_total

    st.markdown(
        f"""
        <div class='total-score-box'>
        <div class='total-score-number'>{total_score}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # ゲーム終了
    # -------------------------
    all_filled = all(v is not None for v in st.session_state.scores["upper"].values()) and all(
        v is not None for v in st.session_state.scores["lower"].values()
    )

    if all_filled:
        st.success(f"🎉 ゲーム終了！最終スコア: {total_score}点")
        if st.button("🔄 新しいゲームを開始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # -------------------------
    # サイドバー
    # -------------------------
    with st.sidebar:
        st.markdown("### 📖 ルール")
        st.write(
            """
- 1ターンで最大3回のロール
- ダイスをキープして狙った役を作る
- 上段63点以上で+35点
- 全12カテゴリを埋めると終了
"""
        )
        authenticator.logout("🚪 ログアウト")

elif auth_status is False:
    st.error("❌ ログイン失敗")
else:
    st.warning("👤 ログインしてください")
