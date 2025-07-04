import itertools
import streamlit as st
import re
from collections import Counter, defaultdict
import datetime
import urllib.parse

# --- מילון עברי מוטמע / חיצוני ---
def load_hebrew_dictionary(filepath="cleaned_hebrew_words.txt"): # שם הקובץ הנקי שלך
    words = set() # נשתמש ב-set לחיפוש מהיר של מילים
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip() # הסר רווחים וקווי שורה
                if word and re.fullmatch(r"[א-ת\s]+", word): # ודא שהמילה לא ריקה ומכילה רק אותיות עבריות ורווחים
                    words.add(word)
    except FileNotFoundError:
        st.error(f"קובץ המילון '{filepath}' לא נמצא. וודא שהוא באותה תיקייה של הקוד.")
        # אם הקובץ לא נמצא, עדיין נחזיר מילון קטן כדי שהאפליקציה לא תקרוס
        return {
            "ישן", "מלא", "עץ", "יפה", "כבד", "כלב", "צחק", "קל", "נסע", "חבר", "רגל", "שחה", "יד",
            "למד", "איטי", "רקד", "מכונית", "חיבק", "שיחק", "חם", "אבן", "כדור", "עצוב", "מלוח", "שתה",
            "בית", "גדול", "הלך", "רחוק", "מהיר", "שולחן", "קרא", "כיסא", "טעים", "חדש", "חכם", "מחשב",
            "חלון", "שמח", "צייר", "חתול", "בישל", "שחט", "כתב", "טייל", "בכה", "שאל", "מים", "אור", "שמש",
            "ספר", "ריק", "מתוק", "גשר", "עין", "קר", "ענה", "רץ", "אור", "חלון", "שולחן", "קטן", "מתוק",
            "חכם", "מלוח", "עצוב", "בכה", "חתול", "צייר", "שחט", "רגל", "רחוק", "מהיר", "יד", "כיסא",
            "קל", "נסע", "חדש", "שולחן", "כתב", "מכונית", "שמש", "מחשב", "כבד", "למד", "שמח", "שיחק",
            "ריק", "עצוב", "טייל", "שתה", "מים", "עין", "חיבק", "חבר", "שחה", "שאל", "יפה", "קרא", "צחק"
        }
    return words

hebrew_dict = load_hebrew_dictionary("cleaned_hebrew_words.txt") # <-- וודא שזה שם הקובץ הנקי שיצרת!
# ניקוי טקסט - רק אותיות עבריות
def clean_text(text):
    return re.sub(r"[^א-ת]", "", text)

# בדיקת תקינות מילה מול מאגר אותיות
def is_valid_word(word, letter_bank):
    return not (Counter(word) - letter_bank)

# יצירת אנגרמות לפי אורך המילים
def generate_categorized_anagrams(sentence):
    letters = clean_text(sentence)
    letter_bank = Counter(letters)
    valid_words = [w for w in hebrew_dict if is_valid_word(w, letter_bank) and len(w) > 1]
    categorized = defaultdict(list)
    for word in valid_words:
        categorized[len(word)].append(word)
    return dict(sorted(categorized.items(), reverse=True))

# שמירת תוצאות לקובץ טקסט
def save_results_to_file(results):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"anagram_results_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for length, words in results.items():
            f.write(f"\n--- מילים באורך {length} ---\n")
            f.write(", ".join(words) + "\n")
    return filename

# יצירת קישורים לשיתוף
def generate_whatsapp_link(text):
    encoded = urllib.parse.quote(text)
    return f"https://api.whatsapp.com/send?text={encoded}"

def generate_facebook_link(text):
    encoded = urllib.parse.quote(text)
    return f"https://www.facebook.com/sharer/sharer.php?u={encoded}"

def generate_email_link(subject, body):
    return f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

# הגדרת ממשק משתמש
st.set_page_config(page_title="יוצר אנגרמות בעברית", layout="wide", page_icon="🧠")

st.markdown("""
    <div style='text-align: center; background-color: #e8f4fc; padding: 25px; border-radius: 15px;'>
        <h1 style='color: #0077b6;'>🎨 יוצר אנגרמות בעברית</h1>
        <p style='font-size:18px;'>הזן מילה או משפט, קבל מאות אנגרמות מחולקות לפי אורך ובעיצוב צבעוני</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
language = col1.selectbox("🌐 שפה להצגה:", ["עברית", "English"])
user_input = col2.text_input("✍️ הכנס מילה או משפט בעברית:", "")
save_results = st.checkbox("📥 שמור את התוצאות כקובץ")

if st.button("🔍 צור אנגרמות"):
    if not user_input.strip():
        st.warning("אנא הכנס טקסט תקני בעברית")
    else:
        categorized_results = generate_categorized_anagrams(user_input)
        total_words = sum(len(words) for words in categorized_results.values())

        if total_words:
            st.success(f"נמצאו {total_words} מילים תקינות על בסיס האותיות שהוזנו!")
            color_palette = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#9D4EDD", "#00A8E8", "#F9844A"]

            for idx, (length, words) in enumerate(categorized_results.items()):
                color = color_palette[idx % len(color_palette)]
                st.markdown(f"<h4 style='color:{color};'>🔹 מילים באורך {length} ({len(words)})</h4>", unsafe_allow_html=True)
                st.markdown(", ".join(sorted(words)))

            if save_results:
                filename = save_results_to_file(categorized_results)
                st.info(f"✅ התוצאות נשמרו לקובץ בשם: {filename}")

            example_text = f"🎉 מצאתי {total_words} אנגרמות מהמילים: '{user_input}'! כנסו לראות בעצמכם: https://hebrew-anagram.streamlit.app"
            whatsapp_link = generate_whatsapp_link(example_text)
            facebook_link = generate_facebook_link("https://hebrew-anagram.streamlit.app")
            email_link = generate_email_link("אנגרמות בעברית", example_text)

            st.markdown(f"[📤 שתף בוואטסאפ]({whatsapp_link})", unsafe_allow_html=True)
            st.markdown(f"[🌐 שתף בפייסבוק]({facebook_link})", unsafe_allow_html=True)
            st.markdown(f"[✉️ שלח במייל]({email_link})", unsafe_allow_html=True)

        else:
            st.error("לא נמצאו מילים תקינות במילון על בסיס האותיות שהוזנו")

st.markdown("""
    <hr style='margin-top:40px;'>
    <div style='text-align: center;'>
        <small style='color:gray;'>מופעל על ידי Python + Streamlit • גרסה מתקדמת וציבורית • כל הזכויות שמורות 🧠</small>
    </div>
""", unsafe_allow_html=True)
