import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import random
from collections import Counter
import streamlit.components.v1 as components # <-- 【復活】

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

# --- JavaScriptのインジェクション ---
# タップイベントを非表示のチェックボックスクリックに変換するJS
js_code = """
<script>
    function setupDiceClick() {
        const diceContainers = document.querySelectorAll('.dice-tap-area');
        diceContainers.forEach((container, index) => {
            // 既存のリスナーを削除 (二重登録防止)
            container.removeEventListener('click', handleDiceClick);
            
            // 新しいリスナーを登録
            container.addEventListener('click', handleDiceClick);
            
            // サイコロのインデックスをカスタムデータ属性として設定
            container.setAttribute('data-dice-index', index);
        });
    }

    function handleDiceClick(event) {
        event.preventDefault(); // デフォルトの動作を防ぐ
        event.stopPropagation(); // イベントのバブリングを防ぐ

        const parent = event.currentTarget;
        const diceIndex = parent.getAttribute('data-dice-index');
        
        // st.checkbox のラッパーを探索 (IDやkeyに基づいて検索)
        // Streamlitの内部構造に依存するため、最も確実な方法で検索
        const targetElement = document.querySelector('[data-testid="stColumn"]:nth-child(' + (parseInt(diceIndex) + 1) + ') [data-testid="stCheckbox"] input[type="checkbox"]');

        if (targetElement) {
            // プログラムでクリックイベントを発火させる
            targetElement.click();
        }
    }

    // MutationObserver: StreamlitがDOMを更新するたびに再セットアップを試みる
    // これが Streamlit の rerun 後も動作させるための最も重要な対策です
    const observer = new MutationObserver(function(mutations) {
        // diceContainersが存在し、かつDOM変更があった場合に再セットアップ
        if (document.querySelector('.dice-tap-area')) {
            setupDiceClick();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // 初回ロード時
    setupDiceClick();
</script>
"""
# HTMLとしてStreamlitに埋め込む
components.html(js_code, height=0, width=0)

# --- CSS (タップ対応と極小化の再調整) ---
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

/* 【重要】タップ領域のコンテナ */
.dice-tap-area {
    width: 100%;
    aspect-ratio: 1;
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    display: flex; 
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* サイコロの見た目 */
.dice {
    font-size: 2.2rem;
    background: linear-gradient(145deg, #fffde7 0%, #fff9c4 100%);
    border: 3px solid #fbc02d;
    border-radius: 0.75rem;
    padding: 0.75rem 0.25rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    aspect-ratio: 1;
    box-shadow: 0 4px 8px rgba(251, 192, 45, 0.3), inset 0 -2px 4px rgba(251, 192, 45, 0.1);
    transition: all 0.3s ease;
    user-select: none;
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

/* 【重要】チェックボックスを完全に非表示にし、サイコロの見た目と入れ替える */
[data-testid="stCheckbox"] {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}

/* st.checkboxの親要素（stColumn）をFlexコンテナ化し、チェックボックスをサイコロの見た目と重ねる */
[data-testid="stColumn"] {
    display: flex;
    flex-direction: column;
    align-items: stretch;
}

/* Streamlitのボタン全般 */
.stButton > button {
    background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
    color: #ffffff;
    border-radius: 0.75rem;
    padding: 1rem 1.5rem;
    font-weight: 600;
    width: 100%;
    font-size: 1rem;
}

/* 役のスコアリングボタンの調整（前回の極小化CSSを適用） */
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

secret_messages = [
    "🎊 すごい！ヨットマスター！",
    "✨ 運命の一振り！",
    "🌟 サイコロの神が微笑んだ！",
    "🎯 完璧なタイミング！",
    "🔥 伝説の出目！"
]

# --- ゲーム本体 ---
if auth_status:

    # ヘッダー (CSSは省略)
    st.markdown(f"""
    <div class='game-header'>
        <div class='game-title'>🎲 ヨットダイス</div>
        <div class='player-badge'>👤 {name}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- 初期化 ---
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

    def roll_dice():
        for i in range(5):
            if not st.session_state.keep[i]:
                st.session_state.dice[i] = random.randint(1, 6)
                st.session_state.shake[i] = True
            else:
                st.session_state.shake[i] = False
        st.session_state.rolls_left -= 1
        check_easter_eggs()

    def check_easter_eggs():
        # ... (省略: 前のバージョンの関数と同じ)
        pass

    def calculate_score(category, dice):
        # ... (省略: 前のバージョンの関数と同じ)
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

    def fill_score(section, category):
        # ... (省略: 前のバージョンの関数と同じ)
        score = calculate_score(category, st.session_state.dice)
        st.session_state.scores[section][category] = score
        st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
        st.session_state.rolls_left = 2
        st.session_state.keep = [False]*5
        st.session_state.shake = [True]*5
        st.session_state.turn += 1

    def get_total_score():
        # ... (省略: 前のバージョンの関数と同じ)
        upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
        bonus = 35 if upper_total >= 63 else 0
        lower_total = sum(s for s in st.session_state.scores["lower"].values() if s is not None)
        return upper_total + bonus + lower_total

    # --- サイコロ表示（タップでキープ） ---
    st.markdown("<div class='dice-container'>", unsafe_allow_html=True)
    st.markdown("<div class='dice-grid'>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            shake_class = "dice-roll" if st.session_state.shake[i] else ""
            kept_class = "dice-kept" if st.session_state.keep[i] else ""
            label = "✅ KEEP" if st.session_state.keep[i] else "タップでKEEP"
            
            # 1. タップ可能なサイコロの見た目を表示
            # JSがこのdivを検知し、クリックイベントを裏側のチェックボックスに転送します
            st.markdown(f"""
            <div class='dice-tap-area'>
                <div class='dice {shake_class} {kept_class}'>
                    <div>{dice_faces[st.session_state.dice[i]]}</div>
                    <div class='dice-label'>{label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. 非表示のチェックボックスを配置（Streamlitの状態更新用）
            # keyを直接使って値の変更をStreamlitに認識させます
            st.checkbox("", key=f"keep_{i}", value=st.session_state.keep[i], label_visibility="collapsed")
            # 注意: JSがこのチェックボックスを操作するため、Python側の状態操作は不要です

    st.markdown("</div>", unsafe_allow_html=True)
    
    # 振り直しボタン (省略)
    if st.session_state.rolls_left > 0:
        if st.button(f"🎲 振り直す (残り {st.session_state.rolls_left}回)", key="roll", use_container_width=True):
            roll_dice()
            st.rerun()
    else:
        st.markdown("<div class='info-badge'>✋ スコアを選択してください</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # --- スコア表（2カラム） ---
    # ... (省略: スコアリングロジックは前のバージョンと同じ)
    
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
                        button_text = f"{label}\\n{potential}点" 
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
                        button_text = f"{emoji} {label}\\n{potential}点"
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

    # ... (省略: イースターエッグとゲーム終了ロジック)

    # サイドバー
    with st.sidebar:
        # ... (省略: ルールとログアウト)
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
