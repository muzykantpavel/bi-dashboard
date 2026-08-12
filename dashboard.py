import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="BI-дашборд проекта", layout="wide")
st.title("📊 Дашборд управления проектом BI-аналитики")

# ===================== ДАННЫЕ =====================

# 1. Штатное расписание
df_team = pd.DataFrame({
    "Роль": ["Data Engineer (ETL/DWH)", "BI-разработчик / Аналитик", "Продуктовый аналитик", "Backend/Frontend (трекинг)", "Тимлид / Архитектор"],
    "Загрузка": ["1,0 FTE", "1,0 FTE", "0,5 FTE", "0,5–1,0 FTE", "0,3 FTE"],
    "Ставка_мин": [250000, 180000, 150000, 200000, 300000],
    "Ставка_макс": [350000, 250000, 200000, 300000, 400000],
    "Месяцев": [5, 5, 5, 2.5, 5]
})

df_team["Итого_мин"] = df_team["Ставка_мин"] * df_team["Месяцев"]
df_team["Итого_макс"] = df_team["Ставка_макс"] * df_team["Месяцев"]

# 2. Варианты проекта
df_options = pd.DataFrame({
    "Вариант": ["MVP", "Полный проект"],
    "Состав": ["Executive + Привлечение + Основная воронка", "Все 9 дашбордов"],
    "Срок_мес_мин": [2.0, 5.0],
    "Срок_мес_макс": [2.5, 7.0],
    "Бюджет_мин": [1200000, 3500000],
    "Бюджет_макс": [1800000, 4900000]
})

# 3. Этапы (Гант)
df_stages = pd.DataFrame({
    "Этап": ["Discovery", "Событийная аналитика", "DWH и интеграции", "Дашборды — волна 1", "Дашборды — волна 2", "Дашборды — волна 3", "Валидация и обучение"],
    "Недель_мин": [2, 6, 6, 4, 4, 3, 2],
    "Недель_макс": [3, 10, 8, 6, 6, 5, 3],
    "Зависимости": ["—", "Параллельно с этапом 2", "После этапа 0", "После этапов 1,2", "После этапа 3", "После этапа 4", "После этапа 5"],
    "Цвет": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
})

# 4. Инфраструктура
infra_min = 20000
infra_max = 100000

# ===================== БОКОВАЯ ПАНЕЛЬ =====================
st.sidebar.header("⚙️ Настройки")
option = st.sidebar.radio("Выберите вариант проекта", ["MVP", "Полный проект"])

# Выбор данных по варианту
selected = df_options[df_options["Вариант"] == option].iloc[0]
budget_min = selected["Бюджет_мин"]
budget_max = selected["Бюджет_макс"]
months_min = selected["Срок_мес_мин"]
months_max = selected["Срок_мес_макс"]

# ===================== KPI =====================
st.subheader("📌 Ключевые показатели")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Срок (мес)", f"{months_min} – {months_max}")
col2.metric("Бюджет команды (₽)", f"{budget_min:,} – {budget_max:,}".replace(",", " "))
col3.metric("Инфраструктура (в мес, ₽)", f"{infra_min:,} – {infra_max:,}".replace(",", " "))
col4.metric("Инфраструктура (за проект, ₽)", f"{int(infra_min*months_max):,} – {int(infra_max*months_max):,}".replace(",", " "))

st.divider()

# ===================== ГРАФИК 1: Бюджет по ролям =====================
st.subheader("💰 Бюджет команды по ролям")
fig1 = px.bar(
    df_team,
    x="Роль",
    y=["Итого_мин", "Итого_макс"],
    barmode="group",
    title="Затраты на роли (диапазон)",
    labels={"value": "Рубли", "variable": "Оценка"},
    color_discrete_map={"Итого_мин": "#1f77b4", "Итого_макс": "#ff7f0e"}
)
st.plotly_chart(fig1, use_container_width=True)

# ===================== ГРАФИК 2: Сравнение MVP vs Full =====================
st.subheader("⚖️ Сравнение MVP и Полного проекта")
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df_options["Вариант"],
    y=df_options["Бюджет_мин"],
    name="Бюджет мин",
    marker_color="#1f77b4"
))
fig2.add_trace(go.Bar(
    x=df_options["Вариант"],
    y=df_options["Бюджет_макс"],
    name="Бюджет макс",
    marker_color="#ff7f0e"
))
fig2.update_layout(title="Бюджет команды по вариантам", yaxis_title="Рубли", barmode="group")
st.plotly_chart(fig2, use_container_width=True)

# ===================== ГРАФИК 3: Диаграмма Ганта =====================
st.subheader("🗓️ Дорожная карта (Гант)")

# Преобразуем недели в дни (стартуем с сегодня)
start_base = datetime.today()
df_gantt = df_stages.copy()
df_gantt["Старт"] = [start_base + timedelta(weeks=i*2) for i in range(len(df_gantt))]
df_gantt["Финиш_мин"] = df_gantt["Старт"] + pd.to_timedelta(df_gantt["Недель_мин"], unit="w")
df_gantt["Финиш_макс"] = df_gantt["Старт"] + pd.to_timedelta(df_gantt["Недель_макс"], unit="w")

fig3 = go.Figure()
for i, row in df_gantt.iterrows():
    fig3.add_trace(go.Bar(
        y=[row["Этап"]],
        x=[(row["Финиш_макс"] - row["Старт"]).days],
        base=[row["Старт"]],
        orientation="h",
        name=row["Этап"],
        marker_color=row["Цвет"],
        text=f"{row['Недель_мин']}–{row['Недель_макс']} нед",
        hovertemplate=f"{row['Этап']}<br>{row['Недель_мин']}–{row['Недель_макс']} нед<br>Зависит: {row['Зависимости']}<extra></extra>"
    ))

fig3.update_layout(
    title="Этапы проекта (с зависимостями)",
    xaxis_title="Дата",
    yaxis_title="Этап",
    barmode="stack",
    height=400,
    showlegend=False
)
st.plotly_chart(fig3, use_container_width=True)

# ===================== ГРАФИК 4: Инфраструктура =====================
st.subheader("🖥️ Инфраструктурные расходы")
months_range = list(range(1, int(months_max) + 1))
df_infra = pd.DataFrame({
    "Месяц": months_range,
    "Мин": [infra_min] * len(months_range),
    "Макс": [infra_max] * len(months_range)
})

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_infra["Месяц"], y=df_infra["Мин"],
    mode="lines+markers", name="Мин", line=dict(color="#1f77b4")
))
fig4.add_trace(go.Scatter(
    x=df_infra["Месяц"], y=df_infra["Макс"],
    mode="lines+markers", name="Макс", line=dict(color="#ff7f0e"), fill="tonexty"
))
fig4.update_layout(title="Инфраструктурные затраты по месяцам", xaxis_title="Месяц", yaxis_title="Рубли")
st.plotly_chart(fig4, use_container_width=True)

# ===================== ТАБЛИЦЫ =====================
st.subheader("📋 Детальные данные")
tab1, tab2, tab3, tab4 = st.tabs(["Штатное расписание", "Варианты проекта", "Этапы", "Инфраструктура"])
with tab1:
    st.dataframe(df_team)
with tab2:
    st.dataframe(df_options)
with tab3:
    st.dataframe(df_stages)
with tab4:
    st.dataframe(df_infra)

st.caption("Дашборд создан на основе данных от 12.08.2026")