# Formosa Trail EPh 配速計算器

非官方的 Formosa Trail 54K / 40K 配速規劃網站。

## 網站檔案
- index.html：手機與電腦適用的組別選擇首頁。
- ft54.html：FT54 Pace-0.4，加上返回首頁與組別切換導覽。
- ft40.html：FT40 Pace-0.1，加上返回首頁與組別切換導覽。

## 完整性與修改範圍
來源套件還原後會核對原始 HTML 的 SHA-256，並驗證插入導覽後的 JavaScript 與原始檔案相同。不修改計算邏輯或賽道資料。這不代表已完成瀏覽器操作或 JPEG 匯出實測。

## 首次發布
Settings → Pages → Build and deployment → Source 選擇 GitHub Actions。
Actions → Formosa Trail Pages 可查看建置與部署結果，也可按 Run workflow 重新執行。
只有部署成功後，網站才算正式上線；預期網址為 https://xiang0630.github.io/Formosa-Trail-Pace/ 。

## 更新
.site-source 包含壓縮的原始來源與還原程式。修改來源套件或首頁會觸發建置，還原程式會將兩份計算器提交回 main，再發布網站。
直接修改生成的計算器，之後重新建置時會被來源套件覆寫。要調整計算器，請先更新來源套件。

## 資料與隱私
距離、爬升、起跑與關門時間沿用使用者提供的 HTML，未重新驗證官方公告。請以主辦單位最新公告為準。
新增首頁沒有第三方追蹤，不會自動上傳配速設定。兩份原始計算器既有的外部資源維持原狀。
