# AI Structured Extraction Tool

這是一個基於大語言模型 (LLM) 的**結構化資料提取工具**。它可以將混亂、非結構化的文字（如會議記錄、專案簡報、Email 內容）精準地轉化為具備類型校驗的 JSON 格式。

## 🚀 這可以幹嘛用？
- **自動化會議摘要**：從一段文字中快速提取摘要、關鍵實體。
- **行動清單追蹤**：自動辨識文字中的 Action Items 與截止日期 (Deadlines)。
- **風險評估**：從報告中篩選出潛在風險 (Risks)。
- **整合工作流**：提供 API 接口，可輕易整合進既有的自動化流程或 Web 應用。

## ✨ 核心特色
- **雙介面支持**：同時提供高效的 **CLI** 指令與強大的 **FastAPI** 伺服器。
- **結構化校驗**：利用 Pydantic 確保所有輸出均符合預定義的資料合約。
- **靈活的 Extractor 設計**：
    - `LLMExtractor`：使用 OpenAI + `instructor` 進行精準提取。
    - `MockExtractor`：用於開發與測試，無需 API Key 即可快速驗證流程。
- **提示詞解耦**：獨立的 `prompts/` 模組，方便優化 LLM 的提取效果。

## 🏗️ 模組化架構
本專案採用清晰的層級化設計，確保易於維護與擴充：
- **`app/services/`**: 業務邏輯編排層，負責協調提取流程。
- **`app/extractors/`**: 核心提取引擎（支援 LLM 與 Mock 策略）。
- **`app/schemas/`**: 資料模型定義，定義系統的資料交換格式。
- **`app/prompts/`**: 集中管理 LLM 的系統與用戶提示詞。
- **`app/utils/`**: 提供 Logger、JSON 處理等通用工具。

## 🛠️ 快速開始

### 環境設定
1. **建立虛擬環境**：
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **安裝依賴**：
   ```bash
   pip install -r requirements.txt
   ```
3. **設定環境變數**：
   ```bash
   cp .env.example .env
   # 在 .env 中填入你的 OPENAI_API_KEY
   ```

### 執行方式

#### 1. CLI 提取
```bash
python run.py extract "專案 A 預計在 6 月 1 日交付，小明負責設計，目前有預算超支的風險。"
```

#### 2. 啟動 API 伺服器
```bash
python run.py serve --port 8000
```
啟動後可訪問 `http://localhost:8000/docs` 查看 Swagger 文件。

#### 3. 執行測試
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

## 🧪 開發者工具
- **Mock 模式**：如果你想在沒有 API Key 的情況下測試 API 或 CLI，可以在 `app/services/extraction_service.py` 中將預設的 `LLMExtractor` 更換為 `MockExtractor`。
