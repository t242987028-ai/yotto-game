import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import random
from collections import Counter
# import streamlit.components.v1 as components # <-- 削除

# ページ設定
st.set_page_config(page_title="🎲 ヨットダイス", page_icon="🎲", layout="centered")

# --- パスワードハッシュ化関数 ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# --- ログイン設定 ---
names = ["T", "N"]
usernames = ["Takahito", "Nanako"]
passwords = ["0628", "0408"]
hashed_passwords = [hash_password(p) for p in passwords]

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
        usernames[1]: {"name": names[1], "password": hashed_passwords[1]}
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="yacht_game",
    key="abcdef",
    cookie_expiry_days=30
)

try:
    authenticator.login()
except Exception as e:
    pass

name = st.session_state.get("name")
auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# --- CSS (チェックボックスをサイコロの見た目にする) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
}

/* サイコロエリア */
.dice-container {
    background: #ffffff;
    border: 3px solid #81c784;
    border-radius: 1.25rem;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.2);
}

.dice-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    max-width: 100%;
}

/* --- サイコロの見た目 --- */
.dice {
    font-size: 2.2rem;
    background: linear-gradient(145deg, #fffde7 0%, #fff9c4 100%);
    border: 3px solid #fbc02d;
    border-radius: 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    aspect-ratio: 1;
    box-shadow: 0 4px 8px rgba(251, 192, 45, 0.3), inset 0 -2px 4px rgba(251, 192, 45, 0.1);
    transition: all 0.3s ease;
    user-select: none;
    padding: 0.5rem 0.25rem;
}

.dice-kept {
    background: linear-gradient(145deg, #a5d6a7 0%, #81c784 100%);
    border-color: #4caf50;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3), 0 6px 16px rgba(76, 175, 80, 0.4);
    transform: scale(1.05);
}

.dice-label {
    font-size: 0.65rem;
    margin-top: 0.25rem;
    font-weight: 700;
    color: #2e7d32;
    line-height: 1;
}

.dice-kept .dice-label {
    color: #1b5e20;
}

/* --- 【最重要】チェックボックスのスタイルを上書き --- */

/* stColumn内のstCheckboxコンテナ */
[data-testid="stColumn"] [data-testid="stCheckbox"] {
    position: relative;
    padding: 0 !important;
    margin: 0 !important;
}

/* チェックボックスのチェックマークと枠を非表示 */
[data-testid="stCheckbox"] input[type="checkbox"] {
    position: absolute;
    opacity: 0; /* 完全に見えなくする */
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    z-index: 100; /* 最前面に配置してタップを確実に受け付ける */
    cursor: pointer;
}

/* チェックボックスのラベル（サイコロの見た目）を配置 */
[data-testid="stCheckbox"] label {
    display: block;
    width: 100%;
    margin: 0 !important;
    padding: 0 !important;
    position: relative; /* サイコロの見た目の基準 */
    z-index: 10; /* チェックボックスより奥に配置 */
}

/* StreamlitがCheckboxのラベルとして挿入するdiv（これがサイコロの見た目になる） */
[data-testid="stCheckbox"] label > div:nth-of-type(2) { 
    padding: 0 !important;
    margin: 0 !important;
}

/* --- 役のスコアリングボタンの調整（前回の極小化CSSを維持） --- */
.stColumn .stButton:nth-child(1) > button { 
    padding: 0.4rem 0.5rem !important; 
    font-size: 0.75rem !important;      
    line-height: 1.2 !important;       
    height: 50px !important;           
    text-align: left;
    white-space: pre-wrap;             
}


/* レスポンシブ */
@media (max-width: 480px) {
    .dice {
        font-size: 1.8rem;
        padding: 0.3rem 0.1rem;
    }
    .dice-label {
        font-size: 0.55rem;
    }
    .stColumn .stButton:nth-child(1) > button {
        font-size: 0.65rem !important;
        padding: 0.3rem 0.2rem !important;
        height: 40px !important;
    }
}
</style>
""", unsafe_allow_html=True)

dice_faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

# --- ゲーム本体 (ロジックは前回と同じ) ---
if auth_status:
    # ヘッダー (省略)
    st.markdown(f"""
    <div class='game-header'>
        <div class='game-title'>🎲 ヨットダイス</div>
        <div class='player-badge'>👤 {name}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- 初期化 (省略) ---
    if "dice" not in st.session_state:
        st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
        st.session_state.rolls_left = 2
        st.session_state.keep = [False]*5
        st.session_state.shake = [False]*5
        st.session_state.turn = 1
        st.session_state.easter_egg_found = []
        
        st.session_state.scores = {
            "upper": {"1": None, "2": None, "3": None, "4": None, "5": None, "6": None},
            "lower": {
                "choice": None, "four_of_kind": None, "full_house": None,
                "small_straight": None, "large_straight": None, "yacht": None
            }
        }

    # ロジック関数 (省略)
    def roll_dice():
        for i in range(5):
            if not st.session_state.keep[i]:
                st.session_state.dice[i] = random.randint(1, 6)
                st.session_state.shake[i] = True
            else:
                st.session_state.shake[i] = False
        st.session_state.rolls_left -= 1
        # check_easter_eggs()

    # スコア計算などは省略

    def fill_score(section, category):
        score = calculate_score(category, st.session_state.dice)
        st.session_state.scores[section][category] = score
        st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
        st.session_state.rolls_left = 2
        st.session_state.keep = [False]*5
        st.session_state.shake = [True]*5
        st.session_state.turn += 1

    def calculate_score(category, dice):
        counts = Counter(dice)
        sorted_dice = sorted(dice)
        
        if category in ["1", "2", "3", "4", "5", "6"]:
            return dice.count(int(category)) * int(category)
        if category == "choice":
            return sum(dice)
        if category == "four_of_kind":
            return sum(dice) if (4 in counts.values() or 5 in counts.values()) else 0
        if category == "full_house":
            return sum(dice) if sorted(counts.values()) == [2, 3] else 0
        if category == "small_straight":
            unique_dice = sorted(list(set(dice)))
            for straight in [[1,2,3,4], [2,3,4,5], [3,4,5,6]]:
                if all(s in unique_dice for s in straight):
                    return 15
            return 0
        if category == "large_straight":
            return 30 if sorted_dice in [[1,2,3,4,5], [2,3,4,5,6]] else 0
        if category == "yacht":
            return 50 if 5 in counts.values() else 0
        return 0
    
    def get_total_score():
        upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
        bonus = 35 if upper_total >= 63 else 0
        lower_total = sum(s for s in st.session_state.scores["lower"].values() if s is not None)
        return upper_total + bonus + lower_total


    # --- サイコロ表示（チェックボックスをサイコロの見た目にする） ---
    st.markdown("<div class='dice-container'>", unsafe_allow_html=True)
    st.markdown("<div class='dice-grid'>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        # チェックボックスが変更されたときの処理
        def handle_keep_change(index):
            # チェックボックスの値（True/False）をセッションステートに反映
            st.session_state.keep[index] = st.session_state[f"keep_{index}"]

        with col:
            shake_class = "dice-roll" if st.session_state.shake[i] else ""
            kept_class = "dice-kept" if st.session_state.keep[i] else ""
            label_text = "✅ KEEP" if st.session_state.keep[i] else "タップでKEEP"
            
            # チェックボックスのラベルとしてサイコロの見た目を渡す
            dice_html = f"""
            <div class='dice {shake_class} {kept_class}'>
                <div>{dice_faces[st.session_state.dice[i]]}</div>
                <div class='dice-label'>{label_text}</div>
            </div>
            """
            
            # st.checkboxを使用して、サイコロの見た目とタップロジックを両立させる
            st.checkbox(
                dice_html, 
                key=f"keep_{i}", 
                value=st.session_state.keep[i], 
                on_change=handle_keep_change, 
                args=(i,),
                label_visibility="visible"
            )

    st.markdown("</div>", unsafe_allow_html=True)
    
    # 振り直しボタン 
    if st.session_state.rolls_left > 0:
        if st.button(f"🎲 振り直す (残り {st.session_state.rolls_left}回)", key="roll", use_container_width=True):
            roll_dice()
            st.rerun()
    else:
        st.markdown("<div class='info-badge'>✋ スコアを選択してください</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # --- スコア表（2カラム） ---
    # 上段
    st.markdown("<div class='score-section'><div class='section-title'>🔢 数字カテゴリ</div>", unsafe_allow_html=True)
    
    upper_labels = {
        "1": "1️⃣ エース", "2": "2️⃣ デュース", "3": "3️⃣ トレイ",
        "4": "4️⃣ フォー", "5": "5️⃣ ファイブ", "6": "6️⃣ シックス"
    }
    
    upper_keys = list(upper_labels.keys())
    for row in range(3):
        cols = st.columns(2)
        for col_idx in range(2):
            idx = row * 2 + col_idx
            if idx < len(upper_keys):
                key = upper_keys[idx]
                label = upper_labels[key]
                with cols[col_idx]:
                    if st.session_state.scores["upper"][key] is None:
                        potential = calculate_score(key, st.session_state.dice)
                        button_text = f"{label}\n{potential}点" 
                        if st.button(button_text, key=f"u_{key}", use_container_width=True):
                            fill_score("upper", key)
                            st.rerun()
                    else:
                        st.markdown(f"<div class='score-item score-filled'><span>{label}</span><span>{st.session_state.scores['upper'][key]}点</span></div>", unsafe_allow_html=True)
    
    upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
    bonus_text = "🎁 +35点!" if upper_total >= 63 else f"あと{63-upper_total}点"
    st.markdown(f"<div class='score-item'><span><strong>小計</strong></span><span><strong>{upper_total}点</strong> ({bonus_text})</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 下段
    st.markdown("<div class='score-section'><div class='section-title'>🎯 役カテゴリ</div>", unsafe_allow_html=True)
    
    lower_labels = {
        "choice": ("🎲", "チョイス"),
        "four_of_kind": ("4️⃣", "フォーカード"),
        "full_house": ("🏠", "フルハウス"),
        "small_straight": ("➡️", "Sストレート"),
        "large_straight": ("⏩", "Lストレート"),
        "yacht": ("⛵", "ヨット")
    }
    
    lower_keys = list(lower_labels.keys())
    for row in range(3):
        cols = st.columns(2)
        for col_idx in range(2):
            idx = row * 2 + col_idx
            if idx < len(lower_keys):
                key = lower_keys[idx]
                emoji, label = lower_labels[key]
                with cols[col_idx]:
                    if st.session_state.scores["lower"][key] is None:
                        potential = calculate_score(key, st.session_state.dice)
                        button_text = f"{emoji} {label}\n{potential}点"
                        if st.button(button_text, key=f"l_{key}", use_container_width=True):
                            fill_score("lower", key)
                            st.rerun()
                    else:
                        st.markdown(f"<div class='score-item score-filled'><span>{emoji} {label}</span><span>{st.session_state.scores['lower'][key]}点</span></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 合計スコア
    total = get_total_score()
    st.markdown(f"""
    <div class='total-score-box'>
        <div class='total-score-label'>Total Score</div>
        <div class='total-score-number'>{total}</div>
    </div>
    """, unsafe_allow_html=True)

    # ... (サイドバーとログインロジックは省略)

    # サイドバー
    with st.sidebar:
        st.markdown("### 📖 ゲームルール")
        st.markdown("""
        **基本ルール**
        - 各ターン最大3回振れます
        - **サイコロの画像をタップしてキープ/アンキープ**
        - 12ターンで全カテゴリを埋める
        
        **ボーナス**
        - 上段63点以上で+35点
        """)
        st.markdown("---")
        authenticator.logout("🚪 ログアウト")

elif auth_status == False:
    st.error("❌ ユーザー名またはパスワードが正しくありません")
elif auth_status == None:
    st.warning("👤 ログインしてゲームを開始してください")
