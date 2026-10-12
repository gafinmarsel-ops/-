import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from supabase import create_client

st.set_page_config(page_title="Маршрут студента", page_icon="🚌", layout="wide")

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"].rstrip("/"), st.secrets["SUPABASE_KEY"])

try:
    supabase = get_supabase()
    db_ready, db_error = True, None
except Exception as exc:
    supabase, db_ready, db_error = None, False, str(exc)

st.markdown("""
<style>
.stApp { background: #fbf6ef; color: #302a31; }
.block-container { max-width: 1120px; padding-top: 1.8rem; padding-bottom: 3rem; }
.hero { background: linear-gradient(125deg,#45254b 0%,#805087 72%,#b46b61 100%); padding:1.8rem 2rem; border-radius:22px; color:#fffaf6; margin-bottom:1.2rem; }
.hero h1 { color:#fffaf6; font-size:2.15rem; margin:0 0 .45rem 0; }
.hero p { color:#f8eaf4; margin:0; font-size:1.02rem; }
div[data-testid="stForm"] { background:#fffdf9; border:1px solid #eadbd0; padding:1.25rem 1.35rem; border-radius:18px; }
.stButton button[kind="primary"], div[data-testid="stFormSubmitButton"] button { background:#6d3b72; border-color:#6d3b72; border-radius:10px; }
[data-testid="stMetric"] { background:#fffdf9; border:1px solid #eadbd0; padding:1rem; border-radius:14px; }
</style>
<div class="hero"><h1>🚌 Маршрут студента</h1>
<p>Опрос о том, как студенты добираются до учёбы и выбирают городской транспорт</p></div>
""", unsafe_allow_html=True)

st.write("Цель анкеты — узнать, какие способы передвижения выбирают студенты, сколько времени занимает дорога и что влияет на выбор маршрута. Опрос анонимный и займёт около 2–3 минут. Не указывайте имя или контактные данные.")
st.caption("Учебный проект · Анкета для студентов · Добровольное участие")
if db_ready:
    st.success("База данных подключена. Ответы сохраняются после отправки.")
else:
    st.warning("База данных пока не подключена. Проверьте Secrets и настройки приложения.")
    with st.expander("Техническая информация"):
        st.code(db_error or "Подключение не выполнено")

if "responses" not in st.session_state:
    st.session_state.responses = []

with st.form("mobility_survey"):
    st.subheader("О вашей дороге до учёбы")
    left, right = st.columns(2)
    with left:
        age = st.number_input("Ваш возраст", min_value=14, max_value=80, value=19, step=1)
        course = st.selectbox("На каком вы курсе?", ["1 курс", "2 курс", "3 курс", "4 курс", "5 курс и выше", "Не учусь сейчас"])
        transport = st.radio("Как чаще всего добираетесь до места учёбы?", ["Автобус / троллейбус / трамвай", "Метро", "Пешком", "Личный автомобиль", "Такси / каршеринг", "Велосипед / самокат", "Другой способ"])
        duration = st.selectbox("Сколько обычно занимает дорога в одну сторону?", ["До 15 минут", "15–30 минут", "31–45 минут", "46–60 минут", "Больше часа"])
    with right:
        cost = st.selectbox("Сколько примерно тратите на дорогу за учебный день?", ["Ничего", "До 100 ₽", "101–200 ₽", "201–350 ₽", "Больше 350 ₽", "Затрудняюсь ответить"])
        satisfaction = st.slider("Насколько вы довольны своим способом передвижения?", 1, 10, 7, help="1 — совсем не доволен(на), 10 — полностью доволен(на)")
        frequency = st.selectbox("Как часто опаздываете из-за дороги?", ["Никогда или почти никогда", "Несколько раз в семестр", "1–3 раза в месяц", "Примерно раз в неделю", "Несколько раз в неделю"])
        planning = st.radio("Проверяете ли маршрут или расписание заранее?", ["Всегда", "Часто", "Иногда", "Редко", "Никогда"])
    factors = st.multiselect("Что сильнее всего влияет на выбор транспорта?", ["Стоимость", "Скорость", "Комфорт", "Наличие маршрута рядом с домом", "Расписание", "Погода", "Количество пересадок", "Экологичность", "Безопасность", "Другое"])
    improvement = st.text_area("Что улучшило бы вашу дорогу до учёбы? (необязательно)", max_chars=500)
    submitted = st.form_submit_button("Отправить ответы", type="primary", use_container_width=True)

if submitted:
    answer = {
        "Возраст": int(age), "Курс": course, "Основной транспорт": transport,
        "Время в пути": duration, "Расходы за день": cost,
        "Удовлетворённость (1–10)": int(satisfaction), "Опоздания": frequency,
        "Проверка маршрута": planning, "Факторы выбора": factors,
        "Что улучшить": improvement.strip(), "Время отправки": datetime.now(timezone.utc).isoformat()
    }
    if not db_ready:
        st.error("Ответ не сохранён: база данных не подключена.")
    else:
        try:
            supabase.table("survey_responses").insert({"answers": answer}).execute()
            st.session_state.responses.append(answer)
            st.success("Спасибо! Ваш ответ сохранён в базе данных.")
        except Exception as exc:
            st.error("Не удалось сохранить ответ. Проверьте подключение и права таблицы.")
            with st.expander("Техническая информация"):
                st.code(str(exc))

st.divider()
st.subheader("📊 Результаты опроса в этом сеансе")
st.caption("Для защиты анонимности графики показывают ответы только текущего сеанса. Отправленные анкеты сохраняются в базе данных.")
responses = st.session_state.responses
if not responses:
    st.info("Пока нет ответов в этом сеансе. Заполните анкету выше, чтобы увидеть сводку и графики.")
else:
    df = pd.DataFrame(responses)
    c1, c2, c3 = st.columns(3)
    c1.metric("Ответов в этом сеансе", len(df))
    c2.metric("Средняя удовлетворённость", f"{df['Удовлетворённость (1–10)'].mean():.1f} / 10")
    c3.metric("Самый частый транспорт", df["Основной транспорт"].mode().iat[0])
    st.dataframe(df.drop(columns=["Что улучшить", "Факторы выбора"]), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Скачать ответы этого сеанса в CSV", df.drop(columns=["Что улучшить"]).to_csv(index=False).encode("utf-8-sig"), "student_mobility_responses.csv", "text/csv")
    a, b = st.columns(2)
    with a:
        counts = df["Основной транспорт"].value_counts().rename_axis("Способ передвижения").reset_index(name="Количество")
        fig = px.bar(counts, x="Способ передвижения", y="Количество", title="Каким транспортом пользуются чаще", color_discrete_sequence=["#6d3b72"])
        fig.update_layout(plot_bgcolor="#fffdf9", paper_bgcolor="#fffdf9", font_color="#302a31")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        order = ["До 15 минут", "15–30 минут", "31–45 минут", "46–60 минут", "Больше часа"]
        counts = df["Время в пути"].value_counts().reindex(order, fill_value=0).rename_axis("Время в пути").reset_index(name="Количество")
        fig = px.bar(counts, x="Время в пути", y="Количество", title="Продолжительность дороги", color_discrete_sequence=["#e58a42"])
        fig.update_layout(plot_bgcolor="#fffdf9", paper_bgcolor="#fffdf9", font_color="#302a31")
        st.plotly_chart(fig, use_container_width=True)

st.caption("Учебный опрос. Не вводите имя, телефон, адрес или другие личные данные.")
