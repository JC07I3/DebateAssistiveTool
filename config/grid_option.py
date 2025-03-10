import pandas
import streamlit as st
from st_aggrid import GridOptionsBuilder

def gen_main_gb(gb):
    gb.configure_column("標題", 
        header_name="標題", 
#        filter="agNumberColumnFilter",  # 过滤器（数字类型）
        sortable=True,      # 是否允许排序
#        width=500,          # 列宽度
         # 自定义样式
    )
    gb.configure_default_column(editable=False, resizable=True, filterable=True, cellStyle={'font-size': '20px'} )
    gb.configure_pagination(enabled=True, paginationPageSize=10)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_grid_options(domLayout="autoHeight", rowHeight=40)
    gb.configure_selection("single", use_checkbox=True)
    return gb