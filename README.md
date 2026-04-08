# 辯論助手 (Debate Assistive Tool)

辯論助手是一個基於 Python 和 Streamlit 開發的網頁應用程式，專為辯論比賽選手與團隊設計，用於高效整理、分類與檢索各個盃賽的辯論資料與論點。

## ✨ 核心功能

* **🌍 盃賽分類管理**：支援建立與切換不同盃賽的工作區，讓不同比賽的資料獨立儲存且井然有序。
* **📥 快速儲存資料**：提供便利的表單界面，能夠快速記錄資料的標題、連結、持方（正方、反方、中性）、標籤及重點摘要。
* **🔍 強大檢視與篩選**：結合 `streamlit-aggrid`，提供強大的動態互動式表格，支援透過標題、持方及標籤進行複合式資料篩選。
* **✏️ 編輯與維護**：在檢視列表中點選特定資料，即可直接進行詳細內容修改（標題、持方、標籤、摘要）或刪除舊有資料。
* **🏷️ 自訂標籤系統**：允許針對不同的盃賽自訂專屬標籤，並可隨時從側邊欄新增或移除標籤，方便精準歸納各類型論點。

## 🛠️ 技術棧與依賴

* **語言**: Python 3.9+
* **前端/框架**: [Streamlit](https://streamlit.io/)
* **表格元件**: [Streamlit-AgGrid](https://github.com/PablocFonseca/streamlit-aggrid)
* **資料庫 ORM**: SQLAlchemy (支援 SQLite / MySQL / PostgreSQL 等)

詳細的依賴套件可參考 `requirements.txt`。

## 🚀 如何在本地端運行

1. **進入專案目錄**：
   開啟終端機 (Terminal) 或命令提示字元 (CMD)，切換到此專案的資料夾下。

2. **安裝所需套件**：
   可直接執行專案內的安裝批次檔，或手動透過 pip 安裝：
   ```bash
   # Windows 使用者可執行:
   setup.bat

   # 或手動輸入指令:
   pip install -r requirements.txt
   ```

3. **啟動應用程式**：
   可直接執行專案內的啟動批次檔，或手動輸入指令：
   ```bash
   # Windows 使用者可執行:
   run.bat
   
   # 或手動輸入指令啟動在本機:
   python -m streamlit run app.py
   ```
   啟動後，瀏覽器將會自動開啟 `http://localhost:8501`。

## 🐳 Docker 部署

本專案已配置 `Dockerfile`，你可以透過容器化的方式快速部署：

1. **建立 Docker 映像檔**：
   ```bash
   docker build -t debate-assistive-tool .
   ```

2. **執行 Docker 容器**：
   ```bash
   docker run -p 8080:8080 debate-assistive-tool
   ```

3. 開啟瀏覽器並前往 `http://localhost:8080` 即可開始使用。

## 📂 目錄結構

```text
DebateAssistiveTool/
├── app.py                  # 應用程式 UI 介面與主程式入口
├── Data/                   # 資料庫與資料操作模組
│   ├── contest_manage.py   # 盃賽管理邏輯
│   ├── datab.py            # 資料表定義
│   ├── operation.py        # 資料 CRUD 操作
│   └── tags_manage.py      # 標籤管理邏輯
├── config/                 # 設定檔
│   └── grid_option.py      # AgGrid 表格的顯示設定
├── data.db                 # SQLite 預設資料庫檔案 (本機測試用)
├── Dockerfile              # Docker 映像檔建置配置
├── requirements.txt        # Python 依賴包列表
├── setup.bat               # 安裝依賴的批次指令檔
├── run.bat                 # 執行應用的批次指令檔
└── update_requirements.bat # 更新依賴的批次指令檔
```
