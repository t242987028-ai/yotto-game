import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import random
from collections import Counter

# ページ設定
# 【変更点1】Viewportを最適化（必須）
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

# --- 明るい緑・白・クリーム色のナチュラルCSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
}

/* --- 【最重要変更点2】強制的な縮小と中央配置 --- */
/* Streamlitのメインブロックをターゲット */
[data-testid="stVerticalBlock"] > div:first-child { 
    /* st.containerでラップされた要素の親を対象とする */
    width: 100%;
    margin: 0 auto;
    padding: 0 1rem; /* 左右の余白は維持 */
}

/* スマホでの縮小処理 */
@media (max-width: 768px) {
    /* 基準となるPCでの幅 (例: 600px) を想定し、現在のビューポート幅との比率でズーム */
    /* これがPC版の「縮尺」を保ちながら全体を縮小する最も有効な方法です */
    
    [data-testid="stVerticalBlock"] > div:first-child { 
        /* zoom: 0.7; など具体的な値を設定すると安定する場合があります */
        /* calc(100vw / 600px) のように計算したいが、CSSで実装が複雑なため、
           以下のように全体を中央に寄せ、サイズを固定して縮小に備えるのが現実的 */
        
        max-width: 600px; 
        margin: 0 auto; 
    }
    
    /* ズームの代替案：コンテンツ全体を包むStreamlitの最上位要素に直接適用 */
    .main {
        padding: 0;
    }

    /* ページのコンテンツ幅がスマホサイズになったら、ズームを適用する */
    .main-container {
        /* スマホで縦長になりすぎるのを防ぎ、PC版のサイズ感を保つ */
        transform-origin: top center;
        /* Viewport Width (vw)を基準に、コンテンツ幅を計算し縮小（近似値） */
        /* 例: 400pxの画面で600pxのコンテンツを表示したい場合、400/600 = 0.666倍 */
        /* 以下は、特定の環境で試す必要があるカスタムな調整です */
        zoom: 0.8; /* 80%に縮小を試みる (最も安定しやすい値) */
        -moz-transform: scale(0.8);
        -moz-transform-origin: top center;
    }
    
    /* フォントサイズのモバイル調整は、このズームアプローチでは削除または緩和します */
    .dice {
        font-size: 3rem; /* PC版のサイズを維持 */
        padding: 1rem 0.5rem;
    }
}


/* ヘッダー */
.game-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
}
/* ... その他のCSSは省略しますが、元のコードのCSSをそのまま使用します ... */
/*
以下に、元のコードから転記したCSSの残りの部分を続けます。
ただし、モバイル調整（@media (max-width: 480px)）で、
特にフォントサイズを縮小している部分は、
上記のズーム処理と競合するため、**削除**または**緩和**することを推奨します。
元のコードのCSSを完全に維持する場合、以下にそのまま続けます。
*/

.game-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2e7d32;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
    text-shadow: 2px 2px 4px rgba(255,255,255,0.5);
}

.player-badge {
    display: inline-block;
    padding: 0.5rem 1.25rem;
    background: #ffffff;
    border: 2px solid #66bb6a;
    border-radius: 1.5rem;
    color: #2e7d32;
    font-size: 0.875rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(46, 125, 50, 0.2);
}

/* サイコロエリア */
.dice-container {
    background: #ffffff;
    border: 3px solid #81c784;
    border-radius: 1.25rem;
    padding: 1.5rem 1rem;
    margin: 1.25rem 0;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.2);
}

.dice-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.dice {
    font-size: 3rem;
    background: linear-gradient(145deg, #fffde7 0%, #fff9c4 100%);
    border: 3px solid #fbc02d;
    border-radius: 0.75rem;
    padding: 1rem 0.5rem;
    display: block;
    width: 100%;
    text-align: center;
    box-shadow: 0 4px 8px rgba(251, 192, 45, 0.3), inset 0 -2px 4px rgba(251, 192, 45, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.dice-kept {
    background: linear-gradient(145deg, #a5d6a7 0%, #81c784 100%);
    border-color: #4caf50;
    box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.3), 0 6px 16px rgba(76, 175, 80, 0.4);
    transform: translateY(-2px) scale(1.05);
}

.dice-roll {
    animation: diceRoll 0.5s ease;
}

@keyframes diceRoll {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-10deg); }
    75% { transform: rotate(10deg); }
}

/* ボタン */
.stButton > button {
    background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
    color: #ffffff;
    border: none;
    border-radius: 0.75rem;
    padding: 1rem 1.5rem;
    font-weight: 600;
    width: 100%;
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.info-badge {
    text-align: center;
    padding: 0.875rem;
    background: #fff3e0;
    border: 2px solid #ffb74d;
    border-radius: 0.625rem;
    color: #e65100;
    font-weight: 600;
    font-size: 0.9375rem;
    margin: 1rem 0;
}

/* スコアカード */
.score-section {
    background: #ffffff;
    border: 3px solid #81c784;
    border-radius: 1.25rem;
    padding: 1.5rem;
    margin: 1.25rem 0;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.15);
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #2e7d32;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 3px solid #a5d6a7;
}

.score-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.875rem 1.25rem;
    margin: 0.5rem 0;
    border-radius: 0.625rem;
    background: #f1f8e9;
    border: 2px solid #c5e1a5;
    font-size: 0.9375rem;
    color: #33691e;
    transition: all 0.2s ease;
}

.score-item:hover {
    background: #dcedc8;
    transform: translateX(4px);
}

.score-filled {
    background: #c8e6c9;
    border: 2px solid #66bb6a;
    color: #1b5e20;
    font-weight: 600;
}

/* 合計スコア */
.total-score-box {
    background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
    text-align: center;
    padding: 2rem 1.5rem;
    border-radius: 1.25rem;
    margin: 1.25rem 0;
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.total-score-number {
    font-size: 3.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0.25rem 0;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}

.total-score-label {
    font-size: 0.875rem;
    color: #e8f5e9;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
}

/* ターン情報 */
.turn-info {
    display: flex;
    justify-content: space-between;
    padding: 0.875rem 1.5rem;
    background: #ffffff;
    border: 2px solid #81c784;
    border-radius: 0.75rem;
    margin: 1rem 0;
    font-size: 0.9375rem;
    font-weight: 600;
    color: #2e7d32;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
}

/* チェックボックス */
.stCheckbox {
    display: flex;
    justify-content: center;
}

.stCheckbox > label {
    font-size: 0.8125rem;
    color: #2e7d32 !important;
    font-weight: 600;
}

/* サイドバー */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
    border-right: 3px solid #81c784;
}

[data-testid="stSidebar"] h3 {
    color: #2e7d32;
    font-weight: 700;
    font-size: 1.25rem;
}

[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] li {
    color: #33691e;
    line-height: 1.7;
}

/* イースターエッグ */
.celebration-text {
    background: linear-gradient(90deg, #66bb6a, #4caf50, #81c784, #a5d6a7, #66bb6a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.375rem;
    font-weight: 700;
    text-align: center;
    padding: 1rem;
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

/* 【元のモバイル調整の削除/緩和推奨】
   今回はズーム処理に頼るため、この部分は不要（または緩和）です */
/* @media (max-width: 480px) { ... } */
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
    # 【変更点3】メインコンテンツを`st.container`でラップし、カスタムCSSのターゲットにする
    with st.container():
        st.markdown("<div class='main-container'>", unsafe_allow_html=True) # CSS用のラッパー

        # ヘッダー
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
            dice = st.session_state.dice
            
            if all(d == 6 for d in dice) and "all_six" not in st.session_state.easter_egg_found:
                st.session_state.easter_egg_found.append("all_six")
                st.balloons()
            
            sorted_dice = sorted(dice)
            if (sorted_dice == [1,2,3,4,5] or sorted_dice == [2,3,4,5,6]) and st.session_state.rolls_left == 2:
                if "first_roll_straight" not in st.session_state.easter_egg_found:
                    st.session_state.easter_egg_found.append("first_roll_straight")
                    st.snow()
            
            if len(set(dice)) == 1 and "yacht_rolled" not in st.session_state.easter_egg_found:
                st.session_state.easter_egg_found.append("yacht_rolled")

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

        def fill_score(section, category):
            score = calculate_score(category, st.session_state.dice)
            st.session_state.scores[section][category] = score
            st.session_state.dice = [random.randint(1, 6) for _ in range(5)]
            st.session_state.rolls_left = 2
            st.session_state.keep = [False]*5
            st.session_state.shake = [True]*5
            st.session_state.turn += 1

        def get_total_score():
            upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
            bonus = 35 if upper_total >= 63 else 0
            lower_total = sum(s for s in st.session_state.scores["lower"].values() if s is not None)
            return upper_total + bonus + lower_total

        # --- サイコロ表示 ---
        st.markdown("<div class='dice-container'>", unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                shake_class = "dice-roll" if st.session_state.shake[i] else ""
                kept_class = "dice-kept" if st.session_state.keep[i] else ""
                st.markdown(f"<div class='dice {shake_class} {kept_class}'>{dice_faces[st.session_state.dice[i]]}</div>", unsafe_allow_html=True)
                keep_label = "🔓 キープ" if not st.session_state.keep[i] else "✅ キープ中"
                st.session_state.keep[i] = st.checkbox(keep_label, key=f"keep_{i}", value=st.session_state.keep[i])
        
        if st.session_state.rolls_left > 0:
            if st.button(f"🎲 振り直す (残り {st.session_state.rolls_left}回)", key="roll", use_container_width=True):
                roll_dice()
                st.rerun()
        else:
            st.markdown("<div class='info-badge'>✋ スコアを選択してください</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # ターン情報
        st.markdown(f"""
        <div class='turn-info'>
            <span>🎯 ターン {st.session_state.turn}/12</span>
            <span>⏳ 残り {12 - st.session_state.turn}回</span>
        </div>
        """, unsafe_allow_html=True)

        # --- スコア表 ---
        # 上段
        st.markdown("<div class='score-section'><div class='section-title'>🔢 数字カテゴリ</div>", unsafe_allow_html=True)
        
        upper_labels = {
            "1": "1️⃣ エース", "2": "2️⃣ デュース", "3": "3️⃣ トレイ",
            "4": "4️⃣ フォー", "5": "5️⃣ ファイブ", "6": "6️⃣ シックス"
        }
        
        for key, label in upper_labels.items():
            if st.session_state.scores["upper"][key] is None:
                potential = calculate_score(key, st.session_state.dice)
                if st.button(f"{label} → {potential}点", key=f"u_{key}", use_container_width=True):
                    fill_score("upper", key)
                    st.rerun()
            else:
                st.markdown(f"<div class='score-item score-filled'><span>{label}</span><span>{st.session_state.scores['upper'][key]}点 ✓</span></div>", unsafe_allow_html=True)
        
        upper_total = sum(s for s in st.session_state.scores["upper"].values() if s is not None)
        bonus_text = "🎁 ボーナス達成 +35点!" if upper_total >= 63 else f"ボーナスまであと{63-upper_total}点"
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
        
        for key, (emoji, label) in lower_labels.items():
            if st.session_state.scores["lower"][key] is None:
                potential = calculate_score(key, st.session_state.dice)
                if st.button(f"{emoji} {label} → {potential}点", key=f"l_{key}", use_container_width=True):
                    fill_score("lower", key)
                    st.rerun()
            else:
                st.markdown(f"<div class='score-item score-filled'><span>{emoji} {label}</span><span>{st.session_state.scores['lower'][key]}点 ✓</span></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # 合計スコア
        total = get_total_score()
        st.markdown(f"""
        <div class='total-score-box'>
            <div class='total-score-label'>Total Score</div>
            <div class='total-score-number'>{total}</div>
        </div>
        """, unsafe_allow_html=True)

        # イースターエッグ表示
        if st.session_state.easter_egg_found:
            if "all_six" in st.session_state.easter_egg_found:
                st.markdown("<div class='celebration-text'>🎉 全部6！完璧なロール！</div>", unsafe_allow_html=True)
            if "first_roll_straight" in st.session_state.easter_egg_found:
                st.success("⚡ 一発ストレート！神業です！")
            if "yacht_rolled" in st.session_state.easter_egg_found:
                st.markdown(f"<div class='celebration-text'>{random.choice(secret_messages)}</div>", unsafe_allow_html=True)

        # ゲーム終了
        all_filled = all(s is not None for s in st.session_state.scores["upper"].values()) and \
                     all(s is not None for s in st.session_state.scores["lower"].values())
        
        if all_filled:
            st.success(f"🎉 ゲーム終了！最終スコア: {total}点")
            if st.button("🔄 新しいゲームを開始", use_container_width=True):
                for key in ["dice", "rolls_left", "keep", "shake", "turn", "scores", "easter_egg_found"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True) # .main-containerの終了

    # サイドバー
    with st.sidebar:
        st.markdown("### 📖 ゲームルール")
        st.markdown("""
        **基本ルール**
        - 各ターン最大3回振れます
        - サイコロを選択してキープ可能
        - 12ターンで全カテゴリを埋める
        
        **ボーナス**
        - 上段63点以上で+35点
        
        **役の得点**
        - ヨット: 50点 (5個同じ)
        - Lストレート: 30点 (1-5 or 2-6)
        - Sストレート: 15点 (4連続)
        - フルハウス: 合計点 (3+2)
        - フォーカード: 合計点 (4個同じ)
        """)
        st.markdown("---")
        authenticator.logout("🚪 ログアウト")

elif auth_status == False:
    st.error("❌ ユーザー名またはパスワードが正しくありません")
elif auth_status == None:
    st.warning("👤 ログインしてゲームを開始してください")
