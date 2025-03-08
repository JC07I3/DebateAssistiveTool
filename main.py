import streamlit as st 
import pandas as pd
import time
import Data

st.title("辯論助手")

st.sidebar.write("## 儲存資料")

com_sp, side_sp = st.sidebar.columns(2)

side_options = ["全部", "正方", "反方", "中性"]

comp_name = st.sidebar.selectbox("盃賽", Data.comp_list, index=0)

side_chosen = st.sidebar.selectbox("持方", side_options, index=0)

def add_option(new_option):
    Data.comp_list.insert(0, str(new_option))

if comp_name == "輸入其他盃賽":
    enter_comp_option = st.sidebar.text_input("輸入盃賽")
    if enter_comp_option:
        if enter_comp_option in Data.comp_list:
            st.sidebar.warning("盃賽已存在")
        else:
            add_option(enter_comp_option)
            st.rerun()
            
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

st.divider()