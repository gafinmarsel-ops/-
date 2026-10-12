import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Маршрут студента", page_icon="🚌", layout="wide")

# Новый визуальный стиль: светлый песочный фон, сливовые акценты и оранжевые детали.
st.markdown("""
<style>
:root { --plum: #6d3b72; --plum-dark: #45254b; --orange: #e58a42; --cream: #fff8ee; }
.stApp { background: #fbf6ef; color: #302a31; }
.block-container { max-width: 1120px; padding-top: 1.8rem; padding-bottom: 3rem; }
.hero { background: linear-gradient(125deg, #45254b 0%, #805087 72%, #b46b61 100%); padding: 1.8rem 2rem; border-radius: 22px; color: #fffaf6; margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(69,37,75,.12); }
.hero h1 { color: #fffaf6; font-size: 2.15rem; margin: 0 0 .45rem 0; }
.hero p { color: #f8eaf4; margin: 0; font-size: 1.02rem; }
div[data-testid="stForm"] { background: #fffdf9; border: 1px solid #eadbd0; padding: 1.25rem 1.35rem; border-radius: 18px; }
.stButton button[kind="primary"], div[data-testid="stFormSubmitButton"] button { background: #6d3b72; border-color: #6d3b72; border-radius: 10px; }
.stButton button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover { background: #45254b; border-color: #45254b; }
[data-testid="stMetric"] { background: #fffdf9; border: 1px solid #eadbd0; padding: 1rem; border-radius: 14px; }
[data-testid="stSidebar"] { background: #f2e7f0; }
hr { border-color: #eadbd0; }
</style>
<div class="hero">
  <h1>🚌 Маршрут студента</h1>
  <p>Опрос о том, как студенты добираются до учёбы и выбирают городской транспорт</p>
</div>
""", unsafe_allow_html=True)

st.write("Цель анкеты — узнать, какие способы передвижения выбирают студенты, сколько времени занимает дорога и что влияет на выбор маршрута. Опрос анонимный и займёт около 2–3 минут. Не указывайте имя или контактные данные.")
st.caption("Учебный проект · Анкета для студентов · Добровольное участие")

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
    st.session_state.responses.append({
        "Возраст": int(age), "Курс": course, "Основной транспорт": transport,
        "Время в пути": duration, "Расходы за день": cost,
        "Удовлетворённость (1–10)": int(satisfaction), "Опоздания": frequency,
        "Проверка маршрута": planning, "Факторы выбора": ", ".join(factors),
        "Что улучшить": improvement.strip(), "Время отправки": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.success("Спасибо! Ваш ответ добавлен в данные текущего сеанса.")
    st.info("Это демонстрационная версия: ответы хранятся в памяти сеанса и могут исчезнуть после перезапуска приложения. Чтобы не потерять результаты, скачайте CSV в блоке аналитики.")

st.divider()
st.subheader("📊 Результаты опроса")
responses = st.session_state.responses
if not responses:
    st.info("Пока нет ответов в этом сеансе. Заполните анкету выше, чтобы сформировать сводку и графики.")
else:
    df = pd.DataFrame(responses)
    c1, c2, c3 = st.columns(3)
    c1.metric("Всего ответов", len(df))
    c2.metric("Средняя удовлетворённость", f"{df['Удовлетворённость (1–10)'].mean():.1f} / 10")
    c3.metric("Самый частый транспорт", df["Основной транспорт"].mode().iat[0])
    st.dataframe(df.drop(columns=["Что улучшить"]), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Скачать ответы в CSV", df.to_csv(index=False).encode("utf-8-sig"), "student_mobility_responses.csv", "text/csv")
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
    st.caption("Сводка строится по ответам, собранным в текущем сеансе. Это учебный опрос, а не репрезентативное исследование.")
