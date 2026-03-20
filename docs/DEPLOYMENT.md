# ARIA v2.0 GitHub Pages 部署說明

## 🌐 GitHub Pages 部署選項

由於主專案已有 GitHub Pages 部署，為避免覆蓋原有地圖，建議採用以下方案：

### **方案 1：使用 GitHub Pages 自定義網域（推薦）**
1. 在 ARIA_V2 分支設定中，將 GitHub Pages 設定為：
   - **Branch**: ARIA_V2
   - **Folder**: /docs
   - **Custom domain**: `aria-v2.hankc0215.github.io`

### **方案 2：建立獨立倉庫**
1. 建立新的獨立倉庫：`https://github.com/hankc0215/ARIA_V2`
2. 獨立部署 GitHub Pages

### **方案 3：使用 gh-pages 分支**
1. 建立 gh-pages 分支專門用於 ARIA_V2
2. 推送 docs 目錄到 gh-pages 分支
3. GitHub Pages 會自動從 gh-pages 分支提供服務

### **方案 4：子路徑部署**
1. 將檔案部署到 `docs/aria-v2/` 子目錄
2. 透過 `https://hankc0215.github.io/ARIA/aria-v2/` 存取

## 🎯 建議方案

**推薦方案 1**，因為：
- 不會影響主專案
- 獨立的網域名稱
- 專業的部署方式
- 易於維護

## 📋 當前狀態

- ✅ ARIA_V2 分支已建立
- ✅ docs/ 目錄已準備
- ✅ 地圖檔案已上傳
- ⏳ 等待 GitHub Pages 設定

## 🚀 下一步

請選擇你偏好的部署方案，我會協助你完成相應的設定。
