import pandas
import streamlit as st
from st_aggrid import GridOptionsBuilder

def gen_main_gb(gb):
    gb.configure_column("id", header_name="", width=0, suppressSizeToFit=True)
    gb.configure_column("title", 
        header_name="標題", 
#        filter="agNumberColumnFilter",  # 过滤器（数字类型）
        sortable=True,      # 是否允许排序
         # 自定义样式
    )
    gb.configure_column("tags",
        header_name="標籤", 
        valueGetter="data.tags.join(', ')",  # 自定义值获取器
    )
    gb.configure_column("side",
        header_name="持方", 
    )
    gb.configure_column("contest", hide=True)
    gb.configure_column("created_at", header_name="上傳時間")
    gb.configure_column("link", hide=True)
    gb.configure_column("content", hide=True)
    gb.configure_default_column(editable=False, resizable=True, filterable=True, cellStyle={'font-size': '20px'} )
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_grid_options(rowHeight=40)
    gb.configure_selection("single", use_checkbox=True)
    return gb