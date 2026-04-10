import streamlit as st 
import pandas as pd
import plotly.express as px
from Data import add_data, add_contest, delete_data, remove_contest, update_data, get_contests, search_data 
from Data import get_tags, add_tag, remove_tag
from Data.operation import get_debate_history, add_note, get_notes, update_note, delete_note, add_script, get_scripts, update_script, delete_script
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from Data.auth import create_user, verify_user_login
from Data.contest_manage import share_contest
import config
from config.constants import SIDE_OPTIONS, SIDE_ALL, OTHER_CONTEST

st.set_page_config(page_title="辯論資料助手", layout="wide")

st.title("辯論助手")

# ----- 帳號登入系統 -----
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
    st.session_state.current_username = None

if st.session_state.current_user_id is None:
    login_tab, signup_tab = st.tabs(["登入", "註冊新帳號"])
    with login_tab:
        l_user = st.text_input("帳號", key="login_u")
        l_pass = st.text_input("密碼", type="password", key="login_p")
        if st.button("登入", use_container_width=True):
            user = verify_user_login(l_user, l_pass)
            if user:
                st.session_state.current_user_id = user["id"]
                st.session_state.current_username = user["username"]
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
    with signup_tab:
        s_user = st.text_input("設定帳號", key="sig_u")
        s_pass = st.text_input("設定密碼", type="password", key="sig_p")
        if st.button("註冊", use_container_width=True):
            if s_user and s_pass:
                if create_user(s_user, s_pass):
                    st.success("註冊成功！請切換至「登入」頁籤進行登入。")
                else:
                    st.error("該帳號名稱已存在")
            else:
                st.warning("請填寫帳號與密碼")
    st.stop()  # 阻擋未登入查看下方內容

# ----- 狀態管理初始化 -----
if "needs_refresh" not in st.session_state:
    st.session_state.needs_refresh = True
if "data_grid" not in st.session_state:
    st.session_state.data_grid = pd.DataFrame()
if "last_choose_side" not in st.session_state:
    st.session_state.last_choose_side = 0

if "filter_keyword" not in st.session_state:
    st.session_state.filter_keyword = ""
if "filter_side" not in st.session_state:
    st.session_state.filter_side = SIDE_ALL
if "filter_tags" not in st.session_state:
    st.session_state.filter_tags = []

# ----- 定義資料拉取函式 -----
def load_data(comp_name):
    f_keyword = st.session_state.filter_keyword if st.session_state.filter_keyword else None
    f_side = None if st.session_state.filter_side == SIDE_ALL else st.session_state.filter_side
    f_tags = st.session_state.filter_tags if st.session_state.filter_tags else None
    
    ret = search_data(keyword=f_keyword, title=None, tags=f_tags, content=None, side=f_side, contest=comp_name)
    
    if not ret.empty and "tags" in ret.columns:
        ret["tags"] = ret["tags"].apply(lambda x: x.split("$") if isinstance(x, str) else [])
        ret["tags"] = ret["tags"].apply(lambda x: [i for i in x if i != ""])
    
    st.session_state.data_grid = ret
    st.session_state.needs_refresh = False

# ----- 側邊欄：使用者與盃賽管理 -----
st.sidebar.markdown(f"**目前身份：{st.session_state.current_username}**")
if st.sidebar.button("登出", use_container_width=True):
    st.session_state.current_user_id = None
    st.session_state.current_username = None
    st.rerun()

st.sidebar.divider()

my_contests = get_contests(st.session_state.current_user_id)
if not my_contests:
    comp_name = st.sidebar.selectbox("資料庫 (盃賽)", ["目前無盃賽"], disabled=True, key="current_comp_ui")
else:
    comp_name = st.sidebar.selectbox("資料庫 (盃賽)", my_contests, index=0, key="current_comp_ui")

if "current_comp" not in st.session_state or st.session_state.current_comp != comp_name:
    st.session_state.current_comp = comp_name
    st.session_state.needs_refresh = True

if st.session_state.needs_refresh and comp_name and comp_name != "目前無盃賽":
    load_data(comp_name)

st.sidebar.write("")
with st.sidebar.expander("盃賽管理與設定", expanded=False):
    st.markdown("##### 新增盃賽")
    enter_comp_option = st.text_input("輸入盃賽名稱", label_visibility="collapsed")
    if st.button("建立盃賽", use_container_width=True):
        if enter_comp_option:
            if enter_comp_option in my_contests:
                st.warning("盃賽已存在")
            else:
                add_contest(enter_comp_option, st.session_state.current_user_id)
                st.session_state.needs_refresh = True
                st.rerun()
        else:
            st.warning("請輸入盃賽名稱")
            
    st.divider()
    st.markdown("##### 協作權限")
    if comp_name and comp_name != "目前無盃賽":
        target_uname = st.text_input("分享此盃賽給使用者 (輸入帳號)", help="目標使用者登入後也能檢視並編輯本盃賽內容")
        if st.button("加入協作者", use_container_width=True):
            if target_uname:
                success, msg = share_contest(comp_name, target_uname)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("請輸入帳號")
    else:
        st.info("請先建立並選取盃賽")

# ----- 主頁面：檢視、儲存與數據分析 -----
note_tab, script_tab, grid_tab, chart_tab, store_tab = st.tabs(["筆記管理", "稿子庫", "檢視資料", "數據分析", "儲存資料"])

with grid_tab:       
    exp = st.expander("篩選資料")
    with exp:
        data_filter = st.form(key="data_filter", clear_on_submit=False)
        with data_filter:
            f_keyword = st.text_input("全文檢索字詞 (搜尋標題或摘要)", value=st.session_state.filter_keyword)
            
            side_index = 0
            if st.session_state.filter_side in SIDE_OPTIONS:
                side_index = SIDE_OPTIONS.index(st.session_state.filter_side) + 1
                
            f_side = st.selectbox("選擇持方", [SIDE_ALL] + SIDE_OPTIONS, index=side_index)
            f_tags = st.multiselect("選擇標籤", get_tags(comp_name), default=st.session_state.filter_tags)

            if data_filter.form_submit_button("確認", use_container_width=True):
                st.session_state.filter_keyword = f_keyword
                st.session_state.filter_side = f_side
                st.session_state.filter_tags = f_tags
                st.session_state.needs_refresh = True
                st.rerun()

    if not st.session_state.data_grid.empty:
        gb = GridOptionsBuilder.from_dataframe(st.session_state.data_grid)
        gb = config.gen_main_gb(gb)
        g_op = gb.build()
        g_op["paginationPageSizeSelector"] = [10, 20, 50, 100]

        tb = AgGrid(
            st.session_state.data_grid, 
            gridOptions=g_op, 
            return_mode="UPDATED", 
            fit_columns_on_grid_load=True, 
            column_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, 
            domLayout="autoHeight", 
            height=465
        )
        selected = tb["selected_rows"]
        
        if selected is not None and len(selected) > 0:
            st.write("---")
            st.write("### 編輯選中資料")
            
            if isinstance(selected, pd.DataFrame):
                selected_row = selected.iloc[0]
            else:
                selected_row = selected[0]
                
            new_title = st.text_input(r"$\textbf{\Large 標題}$", value=selected_row.get("title", ""))
            
            old_side = selected_row.get("side", SIDE_OPTIONS[0])
            new_side_idx = SIDE_OPTIONS.index(old_side) if old_side in SIDE_OPTIONS else 0
            new_side = st.selectbox(r"$\textbf{\Large 持方}$", SIDE_OPTIONS, index=new_side_idx)
            
            current_tags = selected_row.get("tags", [])
            valid_tags = [t for t in current_tags if t in get_tags(comp_name)]
            new_tag = st.multiselect(r"$\textbf{\Large 標籤}$", options=get_tags(comp_name), default=valid_tags)
            
            new_content = st.text_area(r"$\textbf{\Large 摘要}$ (支援 Markdown 與 HTML 語法)", value=selected_row.get("content", ""), height=200)

            # --- 新增的 Markdown 預覽區塊 ---
            st.markdown("#### 預覽摘要", unsafe_allow_html=True)
            with st.container(border=True):
                # 讓文字能夠解析 Markdown 以及簡單的高亮如 <mark>高亮</mark>
                st.markdown(new_content, unsafe_allow_html=True)

            st.write("") # 空行排版
            col1, col2 = st.columns(2)
            if col1.button("確認修改", use_container_width=True):
                update_data(selected_row["id"], st.session_state.current_user_id, title=new_title, side=new_side, tags=new_tag, content=new_content, contest=comp_name)
                st.session_state.needs_refresh = True
                st.rerun()
                
            if col2.button("刪除資料", use_container_width=True):
                delete_data(selected_row["id"])
                st.session_state.needs_refresh = True
                st.rerun()

            # --- 歷史編輯紀錄 ---
            st.write("---")
            from Data.operation import get_debate_history
            with st.expander("檢視歷史編輯紀錄"):
                histories = get_debate_history(selected_row["id"])
                if not histories:
                    st.info("尚無歷史編輯紀錄。")
                else:
                    for h in histories:
                        st.markdown(f"**修改時間**：{h['changed_at']} | **編輯者**：{h['editor_name']}")
                        with st.container(border=True):
                            st.markdown(f"**修改前標題**：{h['old_title']} | **修改前持方**：{h['old_side']}")
                            st.markdown("**修改前內容**：")
                            st.text(h['old_content'])
                        st.write("---")
    else:
        st.info("查無資料，或尚未選擇盃賽。")

with store_tab:
    data_form = st.form(key="store_data", clear_on_submit=True)

    with data_form:
        side_chosen = st.selectbox("持方", SIDE_OPTIONS, index=st.session_state.last_choose_side)
        data_name = st.text_input("輸入資料標題")
        data_link = st.text_input("輸入資料連結")
        data_tags = st.multiselect("標籤", get_tags(comp_name))
        
        st.info("摘要支援 Markdown 語法，例如 `**粗體**`, `# 標題`, 以及HTML `<mark>螢光筆高亮</mark>`。")
        data_statement = st.text_area("輸入資料摘要", height=200)

        submit_button = data_form.form_submit_button("確認", use_container_width=True)

        if submit_button:
            if data_name == "" or data_link == "":
                st.warning("請輸入完整資料標題與連結")
            else:
                add_data(data_name, data_link, data_tags, data_statement, side_chosen, comp_name)
                st.session_state.needs_refresh = True
                st.session_state.last_choose_side = SIDE_OPTIONS.index(side_chosen)
                st.success("資料新增成功！請至「檢視資料」查看。")

    st.write("---")
    st.write("### 標籤管理")
    tag_col1, tag_col2 = st.columns(2)
    with tag_col1:
        with st.container(border=True):
            st.markdown("#### 新增標籤")
            new_tag = st.text_input("輸入新標籤", label_visibility="collapsed")
            if st.button("新增", use_container_width=True):
                if "$" in new_tag:
                    st.warning("標籤不能包含 $ 符號")
                elif new_tag == "":
                    st.warning("標籤不能為空")
                elif new_tag not in get_tags(comp_name):
                    add_tag(new_tag, comp_name)
                    st.session_state.needs_refresh = True
                    st.rerun()
                else:
                    st.warning("標籤已存在")
                    
    with tag_col2:
        with st.container(border=True):
            st.markdown("#### 刪除標籤")
            delet_tag_form = st.form(key="delete_tag", clear_on_submit=False)
            with delet_tag_form:
                tag_to_delete = st.multiselect("刪除標籤 (可多選)", get_tags(comp_name), label_visibility="collapsed")
                if delet_tag_form.form_submit_button("確認刪除", use_container_width=True):
                    if tag_to_delete:
                        for i in tag_to_delete:
                            remove_tag(i, comp_name)
                        st.session_state.needs_refresh = True
                        st.rerun()

# ----- 筆記庫 -----
with note_tab:
    st.markdown("### 筆記庫 (MD 支援)")
    if "viewing_note_id" not in st.session_state:
        st.session_state.viewing_note_id = None
        
    if st.session_state.viewing_note_id is None:
        if st.button("新增筆記", use_container_width=True):
            st.session_state.viewing_note_id = "NEW"
            st.rerun()
            
        notes = get_notes(comp_name)
        if not notes:
            st.info("目前沒有任何筆記。")
        else:
            for n in notes:
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    cols[0].markdown(f"**{n['title']}** (建立: {n['created_at'].strftime('%Y-%m-%d')})")
                    if cols[1].button("開啟", key=f"open_note_{n['id']}", use_container_width=True):
                        st.session_state.viewing_note_id = n['id']
                        st.rerun()
    else:
        if st.button("返回筆記列表", use_container_width=True):
            st.session_state.viewing_note_id = None
            st.rerun()
            
        if st.session_state.viewing_note_id == "NEW":
            n_title = st.text_input("筆記標題")
            n_content = st.text_area("筆記內容 (支援 Markdown)", height=300)
            if st.button("建立", use_container_width=True):
                add_note(n_title, n_content, comp_name)
                st.session_state.viewing_note_id = None
                st.rerun()
        else:
            n_data = next((x for x in get_notes(comp_name) if x['id'] == st.session_state.viewing_note_id), None)
            if n_data:
                st.markdown(f"> 建立日期：{n_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')} | 最後編輯日期：{n_data['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                n_title = st.text_input("筆記標題", value=n_data['title'])
                n_content = st.text_area("編輯內容 (支援 Markdown)", value=n_data['content'], height=300)
                st.markdown("#### 預覽")
                st.markdown(n_content)
                
                c1, c2 = st.columns(2)
                if c1.button("儲存修改", use_container_width=True, key="save_note"):
                    update_note(n_data['id'], n_title, n_content)
                    st.session_state.viewing_note_id = None
                    st.rerun()
                if c2.button("刪除筆記", use_container_width=True, key="del_note"):
                    delete_note(n_data['id'])
                    st.session_state.viewing_note_id = None
                    st.rerun()

# ----- 稿子庫 -----
with script_tab:
    st.markdown("### 稿子庫 (純文字與字數統計)")
    if "viewing_script_id" not in st.session_state:
        st.session_state.viewing_script_id = None
        
    if st.session_state.viewing_script_id is None:
        s_filter = st.selectbox("依持方篩選", ["全", "正方", "反方"])
        if st.button("新增稿子", use_container_width=True):
            st.session_state.viewing_script_id = "NEW"
            st.rerun()
            
        scripts = get_scripts(comp_name, s_filter)
        if not scripts:
            st.info("目前沒有任何稿子。")
        else:
            for s in scripts:
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    cols[0].markdown(f"**[{s['side']}] {s['title']}** (建立: {s['created_at'].strftime('%Y-%m-%d')})")
                    if cols[1].button("開啟", key=f"open_script_{s['id']}", use_container_width=True):
                        st.session_state.viewing_script_id = s['id']
                        st.rerun()
    else:
        if st.button("返回稿子列表", use_container_width=True):
            st.session_state.viewing_script_id = None
            st.rerun()
            
        if st.session_state.viewing_script_id == "NEW":
            s_title = st.text_input("稿子標題")
            s_side = st.selectbox("持方", ["正方", "反方"], index=0)
            s_content = st.text_area("稿子內容 (純文本)", height=400)
            st.caption(f"目前字數: {len(s_content)} 字")
            if st.button("建立", use_container_width=True):
                add_script(s_title, s_side, s_content, comp_name)
                st.session_state.viewing_script_id = None
                st.rerun()
        else:
            s_data = next((x for x in get_scripts(comp_name, "全") if x['id'] == st.session_state.viewing_script_id), None)
            if s_data:
                st.markdown(f"> 建立日期：{s_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')} | 最後編輯日期：{s_data['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                s_title = st.text_input("稿子標題", value=s_data['title'])
                s_side_idx = ["正方", "反方"].index(s_data['side']) if s_data['side'] in ["正方", "反方"] else 0
                s_side = st.selectbox("持方", ["正方", "反方"], index=s_side_idx)
                s_content = st.text_area("稿子內容 (純文本)", value=s_data['content'], height=400)
                st.caption(f"目前字數: {len(s_content)} 字")
                
                c1, c2 = st.columns(2)
                if c1.button("儲存修改", use_container_width=True, key="save_script"):
                    update_script(s_data['id'], s_title, s_side, s_content)
                    st.session_state.viewing_script_id = None
                    st.rerun()
                if c2.button("刪除稿子", use_container_width=True, key="del_script"):
                    delete_script(s_data['id'])
                    st.session_state.viewing_script_id = None
                    st.rerun()

# ----- 數據分析板塊 -----
with chart_tab:
    st.write(f"### {comp_name} - 盃賽數據儀表板")
    
    if st.session_state.data_grid.empty:
        st.warning("目前此盃賽沒有資料可以產生圖表。")
    else:
        df = st.session_state.data_grid
        
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            st.markdown("#### 持方分佈比例")
            # 統計正方、反方、中立的數量
            side_counts = df['side'].value_counts().reset_index()
            side_counts.columns = ['持方', '數量']
            
            # 使用 Plotly 畫圓餅圖
            fig_pie = px.pie(side_counts, values='數量', names='持方', 
                             color='持方', 
                             color_discrete_map={"正方": "#636EFA", "反方": "#EF553B", "中性": "#00CC96"},
                             hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_bar:
            st.markdown("#### 各個標籤資料數量")
            # Explode tags 將每一列中的陣列拆開
            if 'tags' in df.columns:
                df_exploded = df.explode('tags')
                df_exploded = df_exploded[df_exploded['tags'].notna() & (df_exploded['tags'] != '')]
                
                if not df_exploded.empty:
                    tag_counts = df_exploded['tags'].value_counts().reset_index()
                    tag_counts.columns = ['標籤', '數量']
                    
                    fig_bar = px.bar(tag_counts, x='標籤', y='數量', 
                                     color='數量',
                                     color_continuous_scale=px.colors.sequential.Teal)
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("目前所有資料皆無綁定標籤。")



