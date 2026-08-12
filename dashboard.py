import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ===================== НАСТРОЙКА СТРАНИЦЫ =====================
st.set_page_config(page_title="BI-дашборд VeroTrace", layout="wide", initial_sidebar_state="expanded")

# ===================== АНИМАЦИЯ ПРИ ЗАГРУЗКЕ =====================
with st.spinner("🔄 Загрузка дашборда..."):
    time.sleep(0.5)

# ===================== КАСТОМНЫЙ CSS (профессиональный стиль) =====================
st.markdown("""
<style>
    /* Главный заголовок */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    /* Карточки KPI */
    .kpi-card {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #555;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1f77b4;
    }
    /* Риски */
    .risk-critical {
        background: #ffebee;
        border-left: 6px solid #d32f2f;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 4px 0;
    }
    .risk-high {
        background: #fff3e0;
        border-left: 6px solid #f57c00;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 4px 0;
    }
    .risk-medium {
        background: #fff8e1;
        border-left: 6px solid #fbc02d;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 4px 0;
    }
    .risk-low {
        background: #e8f5e9;
        border-left: 6px solid #388e3c;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 4px 0;
    }
    .risk-badge {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-left: 10px;
    }
    .badge-critical { background: #d32f2f; color: white; }
    .badge-high { background: #f57c00; color: white; }
    .badge-medium { background: #fbc02d; color: #333; }
    .badge-low { background: #388e3c; color: white; }
    /* Прогресс-бар */
    .progress-label {
        font-weight: 600;
        color: #333;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ===================== ЗАГОЛОВОК =====================
st.markdown('<p class="main-title">📊 Оценка DWH/BI для VeroTrace</p>', unsafe_allow_html=True)
st.caption("Интерактивная оценка сроков, бюджета и рисков | Данные на основе ТЗ от 12.08.2026")

# ===================== ДАННЫЕ =====================

# 1. Штатное расписание
df_team = pd.DataFrame({
    "Роль": ["Data Engineer (ETL/DWH)", "BI-разработчик / Аналитик", "Продуктовый аналитик", "Backend/Frontend (трекинг)", "Тимлид / Архитектор"],
    "Загрузка": ["1,0 FTE", "1,0 FTE", "0,5 FTE", "0,5–1,0 FTE", "0,3 FTE"],
    "Ставка_мин": [250000, 180000, 150000, 200000, 300000],
    "Ставка_макс": [350000, 250000, 200000, 300000, 400000],
    "Месяцев": [5, 5, 5, 2.5, 5],
    "Цвет": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
})
df_team["Итого_мин"] = df_team["Ставка_мин"] * df_team["Месяцев"]
df_team["Итого_макс"] = df_team["Ставка_макс"] * df_team["Месяцев"]
df_team["Средний"] = (df_team["Итого_мин"] + df_team["Итого_макс"]) / 2

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

# 4. Матрица рисков
df_risks = pd.DataFrame({
    "ID": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"],
    "Риск": [
        "Задержка трекинга (фронт/бэк)",
        "Стыковка данных из источников",
        "Бизнес меняет метрики",
        "API провайдеров меняются/падают",
        "Уход ключевого разработчика",
        "Недостаток инфраструктуры",
        "Задержка согласования дашбордов",
        "Некорректные данные в источниках",
        "Срыв сроков из-за параллельных задач",
        "Безопасность AML-данных"
    ],
    "Вероятность": [5, 4, 5, 4, 2, 3, 4, 4, 3, 2],
    "Влияние": [5, 5, 4, 4, 5, 4, 3, 3, 3, 5],
    "Уровень": ["Критический", "Критический", "Высокий", "Высокий", "Высокий", "Средний", "Средний", "Средний", "Средний", "Средний"],
    "Мера": [
        "Параллельно с DWH, чёткое ТЗ на события",
        "Проверить ключи связки в Discovery",
        "Зафиксировать метрики в начале",
        "Ретраи + алерты + резервные источники",
        "Документация, код-ревью, cross-training",
        "Начать с Metabase, при росте — масштаб",
        "Демо-сессии после каждой волны",
        "Валидация на ETL + Data Quality Dashboard",
        "Буфер 15–20%, чёткий FTE",
        "Шифрование, RBAC, логирование"
    ]
})
df_risks["Score"] = df_risks["Вероятность"] * df_risks["Влияние"]
df_risks["Цвет"] = df_risks["Уровень"].map({
    "Критический": "#d32f2f",
    "Высокий": "#f57c00",
    "Средний": "#fbc02d",
    "Низкий": "#388e3c"
})
df_risks["CSS_класс"] = df_risks["Уровень"].map({
    "Критический": "risk-critical",
    "Высокий": "risk-high",
    "Средний": "risk-medium",
    "Низкий": "risk-low"
})

# 5. Инфраструктура
infra_min = 20000
infra_max = 100000

# ===================== БОКОВАЯ ПАНЕЛЬ =====================
st.sidebar.markdown("### ⚙️ Настройки")

option = st.sidebar.radio(
    "**Выберите вариант проекта**",
    ["MVP", "Полный проект"],
    index=1,
    help="Переключайте, чтобы увидеть разницу в сроках и бюджете"
)

# Дополнительные настройки
show_risks = st.sidebar.checkbox("📋 Показать матрицу рисков", value=True)
show_animation = st.sidebar.checkbox("✨ Анимация графиков", value=True)
theme_toggle = st.sidebar.toggle("🌙 Тёмная тема", value=False)

# Выбор данных по варианту
selected = df_options[df_options["Вариант"] == option].iloc[0]
budget_min = selected["Бюджет_мин"]
budget_max = selected["Бюджет_макс"]
months_min = selected["Срок_мес_мин"]
months_max = selected["Срок_мес_макс"]

if theme_toggle:
    st.markdown("""
    <style>
        .stApp { background: #1e1e2e; color: #cdd6f4; }
        .kpi-card { background: #313244; color: #cdd6f4; }
        .kpi-label { color: #a6adc8; }
        .kpi-value { color: #89b4fa; }
        .risk-critical { background: #2a1a1a; border-left-color: #d32f2f; }
        .risk-high { background: #2a2015; border-left-color: #f57c00; }
        .risk-medium { background: #2a2515; border-left-color: #fbc02d; }
        .risk-low { background: #152a15; border-left-color: #388e3c; }
        .main-title { background: linear-gradient(90deg, #89b4fa, #f9e2af); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# ===================== ПРОГРЕСС-БАР ПРОЕКТА =====================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Прогресс проекта")
progress_value = min(100, int((months_min / 7) * 100))
st.sidebar.progress(progress_value / 100)
st.sidebar.caption(f"Выполнено ~{progress_value}% от полного проекта")

# ===================== KPI =====================
st.markdown("### 📌 Ключевые показатели")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📅 Срок</div>
        <div class="kpi-value">{months_min}–{months_max} мес</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💰 Бюджет команды</div>
        <div class="kpi-value">{budget_min/1e6:.1f}–{budget_max/1e6:.1f} млн ₽</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🖥️ Инфра (в мес)</div>
        <div class="kpi-value">{infra_min/1000:.0f}–{infra_max/1000:.0f} тыс. ₽</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📊 Дашбордов</div>
        <div class="kpi-value">{3 if option == "MVP" else 9}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">👥 Команда</div>
        <div class="kpi-value">{3 if option == "MVP" else 5}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===================== ГРАФИК 1: Бюджет по ролям =====================
st.markdown("### 💰 Бюджет команды по ролям")

fig1 = px.bar(
    df_team.sort_values("Средний", ascending=False),
    x="Роль",
    y=["Итого_мин", "Итого_макс"],
    barmode="group",
    title="Затраты на роли (диапазон)",
    labels={"value": "Рубли", "variable": "Оценка"},
    color_discrete_map={"Итого_мин": "#1f77b4", "Итого_макс": "#ff7f0e"},
    text_auto=".2s"
)
fig1.update_traces(textposition="outside")
fig1.update_layout(
    height=450,
    hovermode="x",
    yaxis_tickformat=",.0f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    transition_duration=500 if show_animation else 0
)
st.plotly_chart(fig1, use_container_width=True)

# ===================== ГРАФИК 2: Сравнение MVP vs Full =====================
st.markdown("### ⚖️ Сравнение MVP и Полного проекта")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df_options["Вариант"],
    y=df_options["Бюджет_мин"],
    name="Бюджет (мин)",
    marker_color="#1f77b4",
    text=[f"{v/1e6:.1f}M" for v in df_options["Бюджет_мин"]],
    textposition="outside"
))
fig2.add_trace(go.Bar(
    x=df_options["Вариант"],
    y=df_options["Бюджет_макс"],
    name="Бюджет (макс)",
    marker_color="#ff7f0e",
    text=[f"{v/1e6:.1f}M" for v in df_options["Бюджет_макс"]],
    textposition="outside"
))

# Добавим метки сроков
for i, row in df_options.iterrows():
    fig2.add_annotation(
        x=row["Вариант"],
        y=row["Бюджет_макс"] + 300000,
        text=f"⏱ {row['Срок_мес_мин']}–{row['Срок_мес_макс']} мес",
        showarrow=False,
        font=dict(size=12, color="#333")
    )

fig2.update_layout(
    title="Бюджет команды по вариантам проекта",
    yaxis_title="Рубли",
    barmode="group",
    height=400,
    yaxis_tickformat=",.0f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    transition_duration=500 if show_animation else 0
)
st.plotly_chart(fig2, use_container_width=True)

# ===================== ГРАФИК 3: Диаграмма Ганта =====================
st.markdown("### 🗓️ Дорожная карта проекта (Гант)")

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
        textposition="inside",
        hovertemplate=f"<b>{row['Этап']}</b><br>"
                      f"Срок: {row['Недель_мин']}–{row['Недель_макс']} нед<br>"
                      f"Зависит: {row['Зависимости']}<extra></extra>"
    ))

fig3.update_layout(
    title="Этапы проекта с зависимостями",
    xaxis_title="Дата",
    yaxis_title="",
    barmode="stack",
    height=400,
    showlegend=False,
    hovermode="y",
    transition_duration=500 if show_animation else 0
)
st.plotly_chart(fig3, use_container_width=True)

# ===================== ГРАФИК 4: Инфраструктура (ИСПРАВЛЕН) =====================
st.markdown("### 🖥️ Инфраструктурные расходы")

# ВСЕГДА ПОКАЗЫВАЕМ 7 МЕСЯЦЕВ (максимальный срок)
max_months_full = 7
months_range = list(range(1, max_months_full + 1))
df_infra = pd.DataFrame({
    "Месяц": months_range,
    "Мин": [infra_min] * len(months_range),
    "Макс": [infra_max] * len(months_range)
})

# Добавим выделение активного периода
active_months = int(months_max)
df_infra["Активный"] = df_infra["Месяц"] <= active_months

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df_infra["Месяц"], y=df_infra["Мин"],
    mode="lines+markers", 
    name="Мин (₽)",
    line=dict(color="#1f77b4", width=3),
    marker=dict(size=10, color="#1f77b4"),
    fill=None
))
fig4.add_trace(go.Scatter(
    x=df_infra["Месяц"], y=df_infra["Макс"],
    mode="lines+markers", 
    name="Макс (₽)",
    line=dict(color="#ff7f0e", width=3),
    marker=dict(size=10, color="#ff7f0e"),
    fill="tonexty",
    fillcolor="rgba(255, 127, 14, 0.15)"
))

# Добавим вертикальную линию границы проекта
fig4.add_vline(
    x=active_months, 
    line_dash="dash", 
    line_color="green",
    annotation_text=f"🏁 Окончание ({option})",
    annotation_position="top right"
)

# Добавим текстовые метки
for i, row in df_infra.iterrows():
    fig4.add_annotation(
        x=row["Месяц"],
        y=row["Макс"] + 5000,
        text=f"{row['Макс']/1000:.0f}k",
        showarrow=False,
        font=dict(size=10, color="#ff7f0e")
    )

fig4.update_layout(
    title=f"Инфраструктурные затраты по месяцам (проект: {option})",
    xaxis_title="Месяц проекта",
    yaxis_title="Рубли",
    height=400,
    yaxis_tickformat=",.0f",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    transition_duration=500 if show_animation else 0
)
st.plotly_chart(fig4, use_container_width=True)

# ===================== МАТРИЦА РИСКОВ =====================
if show_risks:
    st.markdown("---")
    st.markdown("### 🛡️ Матрица рисков проекта")
    st.caption("Оценка рисков по вероятности и влиянию. Критические риски требуют немедленного внимания.")

    col_risk_left, col_risk_right = st.columns([2, 1])

    with col_risk_left:
        # Топ-3 критических риска
        st.markdown("#### 🔴 Топ-3 критических риска")
        critical_risks = df_risks[df_risks["Уровень"] == "Критический"].head(3)
        for _, row in critical_risks.iterrows():
            st.markdown(f"""
            <div class="{row['CSS_класс']}">
                <b>{row['ID']}</b> — {row['Риск']}
                <span class="risk-badge badge-{row['Уровень'].lower()}">{row['Уровень']}</span>
                <br><span style="font-size:0.85rem; color:#555;">✅ {row['Мера']}</span>
            </div>
            """, unsafe_allow_html=True)

        # Остальные риски в таблице
        with st.expander("📋 Показать все риски (полная матрица)"):
            st.dataframe(
                df_risks[["ID", "Риск", "Вероятность", "Влияние", "Уровень", "Мера"]],
                use_container_width=True,
                hide_index=True
            )

    with col_risk_right:
        # График рисков (пузырьковая диаграмма)
        fig_risk = px.scatter(
            df_risks,
            x="Вероятность",
            y="Влияние",
            size="Score",
            color="Уровень",
            text="ID",
            title="Карта рисков",
            color_discrete_map={
                "Критический": "#d32f2f",
                "Высокий": "#f57c00",
                "Средний": "#fbc02d",
                "Низкий": "#388e3c"
            },
            size_max=40
        )
        fig_risk.update_traces(
            textposition="top center",
            marker=dict(line=dict(width=1, color="white"))
        )
        fig_risk.update_layout(
            height=350,
            xaxis=dict(range=[0.5, 5.5], title="Вероятность"),
            yaxis=dict(range=[0.5, 5.5], title="Влияние"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ===================== ТАБЛИЦЫ С ДАННЫМИ =====================
st.markdown("---")
st.markdown("### 📋 Детальные данные")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Штатное расписание",
    "📊 Варианты проекта",
    "🗓️ Этапы",
    "🖥️ Инфраструктура",
    "🛡️ Риски"
])

with tab1:
    st.dataframe(df_team, use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(df_options, use_container_width=True, hide_index=True)

with tab3:
    st.dataframe(df_stages, use_container_width=True, hide_index=True)

with tab4:
    st.dataframe(df_infra, use_container_width=True, hide_index=True)

with tab5:
    st.dataframe(df_risks[["ID", "Риск", "Вероятность", "Влияние", "Уровень", "Мера"]], use_container_width=True, hide_index=True)

# ===================== ФУТЕР =====================
st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("📅 Оценка создана: 12.08.2026")
with col_f2:
    st.caption("📊 Данные на основе ТЗ VeroTrace")
with col_f3:
    st.caption("🚀 Сделано на Python + Streamlit + Plotly")
