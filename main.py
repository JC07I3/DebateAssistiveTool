import streamlit as st 
import pandas as pd
import time

st.title("辯論助手")

st.sidebar.write("## 儲存資料")

if "data_n" not in st.session_state:
    st.session_state["data_n"] = ""

if "data_l" not in st.session_state:
    st.session_state["data_l"] = ""

def clear_data_input():
    return

def submit():
    if data_name == "" or data_link == "":
        st.sidebar.error("輸入不得為空喔!!!")
        return

data_form = st.sidebar.form(key="store_data", clear_on_submit=True)

with data_form:
    data_name = data_form.text_input("輸入資料名稱", max_chars=50, key="data_n")

    data_link = data_form.text_input("輸入資料連結", key = "data_l")

    confirm_, clear_ = data_form.columns(2)

    with confirm_:
        submit_button = data_form.form_submit_button("確認", on_click=submit, use_container_width=True)

    with clear_:
        clear_button = data_form.form_submit_button("清除", on_click=clear_data_input, use_container_width=True)

tb = pd.DataFrame(
    {
        "盃賽" : ["青聲說"], 
        "持方" : ["中性"]
    }
)

st.write(tb)
