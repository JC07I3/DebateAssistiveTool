import streamlit as st 
import pandas as pd
import Data
from Data import add_data, add_contest, delete_data, remove_contest, update_data, get_contests, search_data 
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import config

st.set_page_config(page_title="辯論資料助手", layout="wide")

st.title("辯論助手")

st.sidebar.write("## 儲存資料")

com_sp, side_sp = st.columns(2)

side_options = ["正方", "反方", "中性"]

@st.cache_data()
def get_contest_list():
    return get_contests() + ["蘇州杯"] + ['...輸入其他']

comp_name = st.selectbox("盃賽", get_contest_list(), index=0)

def add_option(new_option):
    add_contest(new_option)

if comp_name == "...輸入其他":
    enter_comp_option = st.text_input("輸入盃賽")
    if enter_comp_option:
        if enter_comp_option in get_contest_list():
            st.sidebar.warning("盃賽已存在")
        else:
            add_option(enter_comp_option)
            st.cache_data.clear()

side_chosen = st.selectbox("持方", side_options, index=0)
           
data_form = st.sidebar.form(key="store_data", clear_on_submit=True)

@st.cache_data
def get_grid(name, side, tags):
    return search_data(name, tags, side=side, contest=comp_name)

if "data_grid" not in st.session_state:
    st.session_state["data_grid"] = get_grid(None, None, None)

with data_form:
    data_name = data_form.text_input("輸入資料標題")

    data_link = data_form.text_input("輸入資料連結")

    data_tags = data_form.multiselect("標籤", Data.tags_list)

    data_statement = data_form.text_area("輸入資料摘要", height=200)

    submit_button = data_form.form_submit_button("確認", use_container_width=True)
    
    clear_button = data_form.form_submit_button("清除", use_container_width=True)


    if submit_button:
        if data_name == "" or data_link == "":
            st.warning("請輸入完整資料")
        else:
            add_data(data_name, data_link, '$'.join(data_tags), data_statement, side_chosen, comp_name)
            st.cache_data.clear()
            st.session_state["data_grid"] = get_grid(None, None, None)
            st.success("新增成功")

    
if "success_add_tag" not in st.session_state:
    st.session_state["success_add_tag"] = 0

new_tag = st.sidebar.text_input("輸入新標籤")
if new_tag:
    if new_tag not in Data.tags_list:
        Data.tags_list.insert(0, str(new_tag))
        st.session_state["success_add_tag"] = 1
        st.rerun()

if st.session_state["success_add_tag"] == 1:
    st.sidebar.success("標籤新增成功")
    st.session_state["success_add_tag"] = 0

filter_name = ""
filter_side = ""
filter_tags = []

with st.expander("篩選資料"):
    data_filter = st.form(key="data_filter", clear_on_submit=False)
    with data_filter:
        col1, col2 = data_filter.columns(2)
        with col1:
            filter_name = st.text_input("輸入資料標題")
        with col2:
            filter_side = st.selectbox("選擇持方", side_options)
        filter_tags = st.multiselect("選擇標籤", Data.tags_list)

        filter_submit_button = data_filter.form_submit_button("確認", use_container_width=True)
        if filter_submit_button:
            st.session_state["data_grid"] = get_grid(filter_name, filter_side, filter_tags)
            st.cache_data.clear()
        
gb = GridOptionsBuilder.from_dataframe(st.session_state["data_grid"])
gb = config.gen_main_gb(gb)
g_op = gb.build()
g_op["paginationPageSizeSelector"] = [10, 20, 50, 100]

tb = AgGrid(st.session_state["data_grid"], gridOptions=g_op, fit_columns_on_grid_load=True, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, domLayout='autoHeight' )
selected = tb["selected_rows"]


if selected is not None:
    st.write("# 修改資料")
    selected_row = selected 
    st.write(selected_row)
    st.write(selected_row.iloc[0]["id"])
    new_title = st.text_input(r"$\textbf{\Large 標題}$", value=selected_row.iloc[0]["title"])
    new_side = st.text_input(r"$\textbf{\Large 持方}$", value=selected_row.iloc[0]["side"])
    new_tag = st.text_input(r"$\textbf{\Large 標籤}$", value=selected_row.iloc[0]["tags"])

    if st.button("確認", use_container_width=True):
        update_data(selected_row.iloc[0]["id"], new_title, new_side, new_tag)
        st.cache_data.clear()
        st.session_state["data_grid"] = get_grid(None, None, None)
        st.rerun()
    if st.button("刪除", use_container_width=True):
        print("delete", selected_row.iloc[0]["id"])
        delete_data(selected_row.iloc[0]["id"])
        print("delete comp")
        st.cache_data.clear()
        st.session_state["data_grid"] = get_grid(None, None, None)
        st.rerun()
