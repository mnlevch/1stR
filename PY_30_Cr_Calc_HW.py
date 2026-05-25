import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Параметры страницы
st.set_page_config(page_title="Кредитный калькулятор", page_icon=":moneybag:", layout="wide")

st.title(":moneybag: Кредитный калькулятор")
st.markdown("Вы можете рассчитать платежи по кредиту, сформировать и скачать график погашения кредита.")

# Боковая панель, условия кредита для расчета
st.sidebar.header("Условия по кредиту")

# Сумма кредита
amount = st.sidebar.number_input(
    "Сумма кредита (руб)",
    min_value=0.00,
    max_value=150_000_000.00,
    value=50_000.00,
    step=50_000.00,
    format="%.2f"
)

# Процентная ставка
rate = st.sidebar.number_input(
    "Процентная ставка (% годовых)",
    min_value=0.00,
    value=15.00,
    step=0.05,
    format="%.2f"
)

# Срок кредита
loan_term = st.sidebar.number_input(
    "Срок кредита (мес)",
    min_value=0,
    value=60,
    step=1
)

# Тип платежа
payment_type = st.sidebar.radio(
    "Тип платежа",
    options=["аннуитетный", "дифференцированный"],
    horizontal=True
)

# Дополнительно (факультативно): считывание даты первого платежа и добавление в таблицу даты каждого из платежей
st.sidebar.subheader("Дополнительно")
enable_dates = st.sidebar.checkbox("Включить даты платежей", value=True)
if enable_dates:
    start_date = st.sidebar.date_input("Введите дату первого платежа", value=datetime.now())
else:
    start_date = None

# Кнопка для запуска расчёта
calculate_btn = st.sidebar.button(label="Рассчитать график", type="primary", use_container_width=True)

# Проверка на ошибки введенных параметров
if calculate_btn:
    errors = []
    if amount <= 0:
        errors.append("Введите сумму кредита (больше 0)")
    if rate <= 0:
        errors.append("Введите ставку по кредиту (больше 0%)")
    if loan_term <= 0:
        errors.append("Введите срок кредита (больше 0 мес).")

    if errors:
        st.error("Неправильный ввод исходных данных:")
        for err in errors:
            st.write(f"- {err}")
        st.stop()

    # Вычисления
    rate_month = rate / 12 / 100
    schedule = []
    balance = amount
    total_payment = 0.00
    total_interest = 0.00

    for month in range(1, loan_term + 1):
        if payment_type == "аннуитетный":
            if rate_month > 0:
                annuity_coef = (rate_month * (1 + rate_month) ** loan_term) / \
                               ((1 + rate_month) ** loan_term - 1)
                payment = amount * annuity_coef
            else:
                payment = amount / loan_term
        else: #дифференцированный
            principal_pay = amount / loan_term
            interest_pay = balance * rate_month
            payment = principal_pay + interest_pay

        interest_pay = balance * rate_month
        principal_pay = payment - interest_pay

        # Последний платеж
        if month == loan_term:
            payment = balance + interest_pay
            principal_pay = balance

        balance_end = balance - principal_pay
        if balance_end < 0:
            balance_end = 0.0

        total_payment += payment
        total_interest += interest_pay

        row = {
            "Месяц": month,
            "Остаток долга": round(balance, 2),
            "Платёж": round(payment, 2),
            "Проценты": round(interest_pay, 2),
            "Основной долг": round(principal_pay, 2),
            "Остаток долга на конец периода": round(balance_end, 2)
        }

        if enable_dates and start_date:
            row["Дата платежа"] = (start_date + relativedelta(months=month - 1)).strftime("%d.%m.%Y")

        schedule.append(row)
        balance = balance_end

    df = pd.DataFrame(schedule)

    # Перенос даты в начало таблицы после № месяца
    if enable_dates and "Дата платежа" in df.columns:
        cols = ["Месяц"] + ["Дата платежа"] + [c for c in df.columns if c != "Дата платежа" and c != "Месяц"]
        df = df[cols]

    # Факультативно использование механизмов условного рендеринга
    if payment_type == "аннуитетный":
        st.info("Обращаем внимание, что платеж является фиксированным, при этом переплата выше, чем при дифференцированном платеже")
    else:
        st.info("Обращаем внимание, что первый платеж является максимальным и уменьшается со временем, при этом переплата меньше, чем при аннуитентном платеже")


    # Вывод графика и итогов
    overpayment = total_payment - amount

    col1, col2, col3 = st.columns(3)
    col1.metric("Ежемесячный / Первый (аннуитет / дифференцированный) платёж", f"{df['Платёж'].iloc[0]:,.2f} ₽")
    col2.metric("Переплата", f"{overpayment:,.2f} ₽")
    col3.metric("Общая сумма выплат", f"{total_payment:,.2f} ₽")

    # Факультативно использование механизмов условного рендеринга (st.expander)
    with st.expander("График платежей", expanded=True):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Платёж": st.column_config.NumberColumn(format="%.2f ₽"),
                "Проценты": st.column_config.NumberColumn(format="%.2f ₽"),
                "Основной долг": st.column_config.NumberColumn(format="%.2f ₽"),
                "Остаток долга": st.column_config.NumberColumn(format="%.2f ₽"),
                "Остаток долга на конец периода": st.column_config.NumberColumn(format="%.2f ₽"),
            }
        )

        # Кнопка для скачивания файла в формате csv
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Скачать график в формате 'CSV'",
            data=csv,
            file_name="payment_sched.csv",
            mime="text/csv"
        )

else:
    st.info("Введите условия кредита для расчета графика и нажмите кнопку «Рассчитать график»")

# Факультативно использование механизмов условного рендеринга (st.rerun())
if st.button("Сформировать новый график"):
    st.rerun()