import streamlit as st 
import pandas as pd
import Data
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import config

st.set_page_config(page_title="辯論資料助手", layout="wide")

st.title("辯論助手")

st.sidebar.write("## 儲存資料")

com_sp, side_sp = st.columns(2)

side_options = ["正方", "反方", "中性"]

comp_name = st.selectbox("盃賽", Data.comp_list, index=0)


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

side_chosen = st.selectbox("持方", side_options, index=0)
           
def submit():
    if data_name == "" or data_link == "":
        st.sidebar.error("輸入不得為空喔!!!")
        return

data_form = st.sidebar.form(key="store_data", clear_on_submit=True)

with data_form:
    data_name = data_form.text_input("輸入資料標題", max_chars=50)

    data_link = data_form.text_input("輸入資料連結")

    data_tags = data_form.multiselect("標籤", Data.tags_list)

    data_statement = data_form.text_area("輸入資料摘要", height=200)

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



filter_name = ""
filter_side = ""
filter_tags = []

def filter_submit():
    return

with st.expander("篩選資料"):
    data_filter = st.form(key="data_filter", clear_on_submit=False)
    with data_filter:
        col1, col2 = data_filter.columns(2)
        with col1:
            filter_name = st.text_input("輸入資料標題")
        with col2:
            filter_side = st.selectbox("選擇持方", side_options)
        filter_tags = st.multiselect("選擇標籤", Data.tags_list)

        c1, c2 = data_filter.columns(2)
        with c1:
            filter_submit_button = data_filter.form_submit_button("確認", on_click=filter_submit, use_container_width=True)
        with c2:
            filter_clear_button = data_filter.form_submit_button("清除", use_container_width=True)

gb = GridOptionsBuilder.from_dataframe(Data.test_database)
gb = config.gen_main_gb(gb)
g_op = gb.build()
g_op["paginationPageSizeSelector"] = [10, 20, 50, 100]

tb = AgGrid(Data.test_database, gridOptions=g_op, fit_columns_on_grid_load=True, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, domLayout='autoHeight' )
selected = tb["selected_rows"]

if selected is not None:
    st.write("# 修改資料")
    new_title = st.text_input(r"$\textbf{\Large 標題}$", value = str(selected.iloc[0, 0]))
    new_side = st.text_input(r"$\textbf{\Large 持方}$", value = str(selected.iloc[0, 1]))
    new_tag = st.text_input(r"$\textbf{\Large 標籤}$", value = str(selected.iloc[0, 2]))

    if st.button("確認", use_container_width=True):
    #    selected_index = tb.index[tb["標題"] == selected_row["標題"]].tolist()[0] 
    #    tb.loc[selected_index, "標題"] = new_title
    #    tb.loc[selected_index, "持方"] = new_position
    #    tb.loc[selected_index, "標籤"] = new_tag

        st.rerun()
