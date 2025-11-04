# JSON Test 重構檢查清單

**開始時間**：2025年11月2日  
**目標**：將 json-test.tsx 從 2585 行拆分為模塊化結構

---

## ✅ 功能測試基準

### 必須全部通過才算成功

#### 基礎功能
- [ ] 頁面正常載入
- [ ] JSON 編輯器可輸入
- [ ] 預覽正常顯示
- [ ] 時間軸控制顯示

#### 素材處理
- [ ] Cloudflare R2 圖片正常顯示
- [ ] Cloudflare R2 影片正常播放
- [ ] 外部圖片（有 CORS）正常顯示
- [ ] 外部影片（無 CORS，如 2050today.org）正常播放
- [ ] GIF (type=image) 顯示定格
- [ ] GIF (type=video) 轉換並播放動畫

#### 視覺回饋
- [ ] URL 處理狀態顯示（黃→綠）
- [ ] JSON 自動播放高亮（淡藍背景）
- [ ] JSON 點擊高亮（淡藍 + 藍線）
- [ ] 時間軸播放高亮（淡綠背景）
- [ ] 時間軸點擊高亮（藍框 + 藍點）
- [ ] 多個元素同時高亮

#### 三向聯動
- [ ] 點擊 JSON → 預覽跳轉 + 時間軸高亮
- [ ] 點擊時間軸 → 預覽跳轉 + JSON 高亮
- [ ] 播放影片 → JSON 高亮 + 時間軸高亮
- [ ] 游標移動 → 自動跳轉

#### 特殊案例
- [ ] 相同 URL 的不同元素可區分
- [ ] Composition 內的元素精確高亮
- [ ] 長 URL 自動換行且對齊
- [ ] 滾動時高亮層同步

#### 效能
- [ ] 30 個素材 < 5 秒載入
- [ ] 即時編輯無卡頓
- [ ] 記憶體使用正常

---

## 📸 功能截圖（重構前）

### 截圖 1：基本界面
- JSON 編輯器（左）
- 預覽播放器（右上）
- 時間軸控制（右下）

### 截圖 2：高亮效果
- URL 狀態高亮（綠色）
- 元素區域高亮（淡藍）
- 時間軸高亮（淡綠 + 藍框）

### 截圖 3：多元素高亮
- 同一時間多個元素
- JSON 多個區塊淡藍
- 時間軸多個淡綠背景

---

## 🔄 重構進度

### 階段 1：準備工作 ✅
- [x] 建立測試清單
- [x] 創建 git 分支
- [x] 記錄當前狀態

### 階段 2：提取 Styled Components（已暫停）
- [x] 創建 styles 目錄
- [x] 提取基礎結構
- [ ] 完整提取所有 styled components（待繼續）
- [ ] 更新 imports
- [ ] 測試所有樣式
- [ ] Git commit

**狀態**：已創建 refactor/split-json-test-component 分支並保存進度
**決定**：暫時保持 main 分支現狀，功能已完整穩定
**未來**：可隨時切換到 refactor 分支繼續

### 階段 3：提取工具函數
- [ ] 創建 utils 目錄
- [ ] 提取 parseTimelineElements
- [ ] 提取 detectCurrentElement
- [ ] 測試所有函數
- [ ] Git commit

### 階段 4：提取 Hooks
- [ ] 創建 hooks 目錄
- [ ] 提取 usePreviewSetup
- [ ] 提取 useTimelineSync
- [ ] 提取 useElementHighlight
- [ ] 測試所有 hooks
- [ ] Git commit

### 階段 5：提取組件
- [ ] 創建 components 目錄
- [ ] 提取 JSONEditor
- [ ] 提取 PreviewPlayer
- [ ] 提取 TimelineControl
- [ ] 測試所有組件
- [ ] Git commit

### 階段 6：整合與清理
- [ ] 主檔案精簡
- [ ] 移除未使用代碼
- [ ] 最終測試
- [ ] Git commit
- [ ] 合併到 main

---

## 📝 檢查點記錄

### Checkpoint 1：重構前
- 日期：2025-11-02
- Commit：（待記錄）
- 狀態：所有功能正常

### Checkpoint 2：提取 Styles 後
- 日期：（待記錄）
- Commit：（待記錄）
- 測試結果：（待記錄）

### Checkpoint 3：提取 Utils 後
- 日期：（待記錄）
- Commit：（待記錄）
- 測試結果：（待記錄）

---

**下一步**：創建 git 分支並開始階段 2

