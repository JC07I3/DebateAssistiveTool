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

if comp_name == "...輸入其他":
    enter_comp_option = st.sidebar.text_input("輸入盃賽")
    if enter_comp_option:
        if enter_comp_option in Data.comp_list:
            st.sidebar.warning("盃賽已存在")
        else:
            add_option(enter_comp_option)
            st.rerun()
            
def submit():
    if data_name == "" or data_link == "":
        st.sidebar.error("輸入不得為空喔!!!")
        return

data_form = st.sidebar.form(key="store_data", clear_on_submit=True)

with data_form:
    data_name = data_form.text_input("輸入資料名稱", max_chars=50)

    data_link = data_form.text_input("輸入資料連結")

    data_tags = data_form.multiselect("標籤", Data.tags_list)

    submit_button = data_form.form_submit_button("確認", on_click=submit, use_container_width=True)

    clear_button = data_form.form_submit_button("清除", use_container_width=True)

if "success_add_tag" not in st.session_state:
    st.session_state["success_add_tag"] = 0

new_tag = st.sidebar.text_input("輸入新標籤")
if new_tag:
    if new_tag not in Data.tags_list:
        Data.tags_list.insert(0, str(new_tag))
        st.session_state["success_add_tag"] = 1
        st.rerun()

if st.session_state["success_add_tag"] == 1:
    st.sidebar.success("新增成功")
    st.session_state["success_add_tag"] = 0



tb = pd.DataFrame(
    {
        "盃賽" : ["青聲說"], 
        "持方" : ["中性"]
    }
)

st.write(tb)

st.divider()