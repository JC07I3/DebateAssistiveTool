import streamlit as st 
import pandas as pd
import Data
from Data import add_data, add_contest, delete_data, remove_contest, update_data, get_contests, search_data 
from Data import get_tags, add_tag, remove_tag
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import config
from functools import lru_cache

st.set_page_config(page_title="辯論資料助手", layout="wide")

st.title("辯論助手")

com_sp, side_sp = st.columns(2)

side_options = ["正方", "反方", "中性"]

@st.cache_data()
def get_contest_list():
    return get_contests() + ['...輸入其他']
    
comp_name = st.sidebar.selectbox("盃賽", get_contest_list(), index=0)

def add_option(new_option):
    add_contest(new_option)

if comp_name == "...輸入其他":
    enter_comp_option = st.sidebar.text_input("輸入盃賽")
    if enter_comp_option:
        if enter_comp_option in get_contest_list():
            st.sidebar.warning("盃賽已存在")
        else:
            add_option(enter_comp_option)
            st.cache_data.clear()
            st.rerun()

   
grid_tab, store_tab = st.tabs(["檢視資料", "儲存資料"])

if "last_choose_side" not in st.session_state:
    st.session_state["last_choose_side"] = 0

filter_name = ""
filter_side = ""
filter_tags = []

@lru_cache(maxsize=128)
def get_grid(name=None, tags=None, content=None, side=None, contest=None):
    ret = search_data(name, tags, None, side, contest)
    ret["tags"] = ret["tags"].apply(lambda x: x.split("$"))
    ret["tags"] = ret["tags"].apply(lambda x: [i for i in x if i != ""])
    return ret

if "data_grid" not in st.session_state:
    st.session_state["data_grid"] = get_grid(None, None, None, None, comp_name)

with grid_tab:       
    exp = st.expander("篩選資料")
    with exp:
        data_filter = st.form(key="data_filter", clear_on_submit=False)
        with data_filter:
            filter_name = st.text_input("輸入資料標題")
            filter_side = st.selectbox("選擇持方", ["全部"] + side_options)
            filter_tags = st.multiselect("選擇標籤", get_tags(comp_name))

            filter_submit_button = data_filter.form_submit_button("確認", use_container_width=True)
            if filter_submit_button:
                if filter_side == "全部":
                    filter_side = None
                get_grid.cache_clear()
                st.session_state["data_grid"] = get_grid(name=filter_name, tags='$'.join(filter_tags), side=filter_side, contest=comp_name)
    
    gb = GridOptionsBuilder.from_dataframe(st.session_state["data_grid"])
    gb = config.gen_main_gb(gb)
    g_op = gb.build()
    g_op["paginationPageSizeSelector"] = [10, 20, 50, 100]

    tb = AgGrid(st.session_state["data_grid"], gridOptions=g_op, return_mode="UPDATED", fit_columns_on_grid_load=True, column_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, domLayout="autoHeight", height=465)
    selected = tb["selected_rows"]

    if selected is not None:
        st.write("# 修改資料")
        selected_row = selected 
        new_title = st.text_input(r"$\textbf{\Large 標題}$", value=selected_row.iloc[0]["title"])
        new_side = st.text_input(r"$\textbf{\Large 持方}$", value=selected_row.iloc[0]["side"])
        new_tag = st.multiselect(r"$\textbf{\Large 標籤}$", options=get_tags(comp_name), default=selected_row.iloc[0]["tags"])
        new_content = st.text_area(r"$\textbf{\Large 摘要}$", value=selected_row.iloc[0]["content"], height=200)

        if st.button("確認", use_container_width=True):
            update_data(selected_row.iloc[0]["id"], title=new_title, side=new_side, tags='$'.join(new_tag), content=new_content, contest=comp_name)
            get_grid.cache_clear()
            st.session_state["data_grid"] = get_grid(name=filter_name, tags='$'.join(filter_tags), side=filter_side, contest=comp_name)
        if st.button("刪除", use_container_width=True):
            delete_data(selected_row.iloc[0]["id"])
            get_grid.cache_clear()
            st.session_state["data_grid"] = get_grid(name=filter_name, tags='$'.join(filter_tags), side=filter_side, contest=comp_name)
with store_tab:
    data_form = st.form(key="store_data", clear_on_submit=True)

    with data_form:
        side_chosen = st.selectbox("持方", side_options, index=st.session_state["last_choose_side"])
        
        data_name = data_form.text_input("輸入資料標題")

        data_link = data_form.text_input("輸入資料連結")

        data_tags = data_form.multiselect("標籤", get_tags(comp_name))
       
        data_statement = data_form.text_area("輸入資料摘要", height=200)

        submit_button = data_form.form_submit_button("確認", use_container_width=True)
        
        clear_button = data_form.form_submit_button("清除", use_container_width=True)

        if "success_add_data" not in st.session_state:
            st.session_state["success_add_data"] = 0

        if submit_button:
            if data_name == "" or data_link == "":
                st.warning("請輸入完整資料")
            else:
                add_data(data_name, data_link, '$'.join(data_tags), data_statement, side_chosen, comp_name)
                get_grid.cache_clear()
                st.session_state["data_grid"] = get_grid(filter_name, '$'.join(filter_tags), None, filter_side, comp_name)
                st.session_state["success_add_data"] = 1   
                st.session_state["last_choose_side"] = side_options.index(side_chosen)
                st.rerun()
        if st.session_state["success_add_data"] == 1:
            st.success("資料新增成功")
            st.session_state["success_add_data"] = 0

        
    if "success_add_tag" not in st.session_state:
        st.session_state["success_add_tag"] = 0

    if "success_delete_tag" not in st.session_state:
        st.session_state["success_delete_tag"] = 0

    fake_column = st.sidebar.columns(1, border=True)[0]
    with fake_column:
        new_tag = st.text_input("輸入新標籤")
    if new_tag:
        if "$" in new_tag:
            st.warning("標籤不能包含$符號")
        elif new_tag == "":
            st.warning("標籤不能為空")
        elif new_tag not in get_tags(comp_name):
            add_tag(new_tag, comp_name)
            st.session_state["success_add_tag"] = 1
            st.rerun()
        else:
            st.warning("標籤已存在")
    delet_tag_form = st.sidebar.form(key="delete_tag", clear_on_submit=True)
    with delet_tag_form:
        tag_to_delete = delet_tag_form.multiselect("刪除標籤", get_tags(comp_name))
        delet_tag_form.form_submit_button("確認", use_container_width=True)
        if tag_to_delete:
            for i in tag_to_delete:
                remove_tag(i, comp_name)
            st.session_state["success_delete_tag"] = 1
            st.rerun()

if st.session_state["success_add_tag"] == 1:
    st.sidebar.success("標籤新增成功")
    st.session_state["success_add_tag"] = 0

if st.session_state["success_delete_tag"] == 1:
    st.sidebar.success("標籤刪除成功")
    st.session_state["success_delete_tag"] = 0

