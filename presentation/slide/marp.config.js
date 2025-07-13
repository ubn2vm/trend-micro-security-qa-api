module.exports = {
  // 啟用 HTML 輸出
  html: true,
  
  // 設定主題
  themeSet: './themes',
  
  // 自訂 CSS
  css: `
    /* 自訂樣式 */
    section {
      background-color: #ffffff;
      color: #333333;
      font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* 標題樣式 */
    h1 {
      color: #1976d2;
      font-size: 2.5em;
      margin-bottom: 0.5em;
    }
    
    h2 {
      color: #388e3c;
      font-size: 1.8em;
      margin-bottom: 0.3em;
    }
    
    /* 程式碼區塊樣式 */
    code {
      background-color: #f5f5f5;
      color: #d32f2f;
      padding: 0.2em 0.4em;
      border-radius: 3px;
    }
    
    pre {
      background-color: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 6px;
      padding: 1em;
    }
    
    /* 列表樣式 */
    ul, ol {
      margin-left: 1.5em;
    }
    
    li {
      margin-bottom: 0.5em;
    }
    
    /* 強調文字 */
    strong {
      color: #1976d2;
      font-weight: 600;
    }
    
    /* 連結樣式 */
    a {
      color: #1976d2;
      text-decoration: none;
    }
    
    a:hover {
      text-decoration: underline;
    }
    
    /* 表格樣式 */
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
    }
    
    th, td {
      border: 1px solid #ddd;
      padding: 8px 12px;
      text-align: left;
    }
    
    th {
      background-color: #f2f2f2;
      font-weight: 600;
    }
    
    /* 引用區塊 */
    blockquote {
      border-left: 4px solid #1976d2;
      margin: 1em 0;
      padding-left: 1em;
      color: #666;
    }
    
    /* 特殊頁面樣式 */
    section.lead {
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    
    section.lead h1 {
      font-size: 3em;
      margin-bottom: 0.3em;
    }
    
    section.lead h2 {
      font-size: 2em;
      color: #666;
      margin-bottom: 0.5em;
    }
    
    /* 圖表容器 */
    .mermaid {
      text-align: center;
      margin: 1em 0;
    }
    
    /* 響應式設計 */
    @media (max-width: 768px) {
      section {
        font-size: 0.9em;
      }
      
      h1 {
        font-size: 2em;
      }
      
      h2 {
        font-size: 1.5em;
      }
    }
  `,
  
  // 輸出選項
  output: {
    html: {
      // 包含 CSS
      includeCSS: true,
      // 包含 JavaScript
      includeJS: true,
    },
    pdf: {
      // PDF 輸出設定
      format: 'A4',
      margin: '1cm',
    },
  },
  
  // 開發伺服器設定
  server: {
    port: 8080,
    host: 'localhost',
  },
}; 