# AIOps 專案 Python 環境設定完整說明

## 📋 目錄
- [專案結構](#專案結構)
- [Python 安裝步驟](#python-安裝步驟)
- [使用方法](#使用方法)
- [快速開始](#快速開始)
- [維護說明](#維護說明)

## 📁 專案結構

```
AIOps/
├── python_config/          # Python配置子資料夾
│   ├── .python_config      # Python路徑配置檔案（隱藏檔案）
│   ├── python.bat          # Python執行器
│   ├── pip.bat             # pip執行器
│   └── setup_python.bat    # Python環境設定腳本
└── README.md               # 完整說明文件（本檔案）
```

## 🐍 Python 安裝步驟

### 1. 下載 Python 安裝程式
- 檔案路徑：`C:\Users\odric\Downloads\python-3.13.5-amd64.exe`
- 版本：Python 3.13.5 (64-bit)

### 2. 執行安裝程式
```cmd
# 使用CMD執行安裝（推薦）
"C:\Users\odric\Downloads\python-3.13.5-amd64.exe" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir=C:\Python313
```

### 3. 重要安裝選項
- ✅ **Install for all users**: 選擇「否」（安裝到使用者目錄）
- ❌ **Add Python to PATH**: **不要勾選**（避免影響系統環境變數）
- ✅ **Include pip**: 勾選（包含套件管理工具）
- 📁 **安裝路徑**: `C:\Python313`

## 🚀 使用方法（不影響系統環境變數）

### 方法一：使用本地批次檔案（推薦）
```cmd
# 進入python_config資料夾
cd python_config

# 直接使用python命令（透過python.bat）
python --version
pip --version
```

### 方法二：臨時設定環境變數
```cmd
# 進入python_config資料夾
cd python_config

# 執行設定檔案（僅在當前會話有效）
setup_python.bat
```

### 方法三：直接使用絕對路徑
```cmd
# 直接使用完整路徑
C:\Python313\python.exe --version
C:\Python313\Scripts\pip.exe --version
```

## ✅ 驗證安裝

設定完成後，可以使用以下命令驗證：

```cmd
# 檢查Python版本
python --version

# 檢查pip版本
pip --version

# 檢查Python安裝路徑
python -c "import sys; print(sys.executable)"
```

## 🔧 快速開始

### 1. 基本使用
```cmd
# 進入python_config資料夾
cd python_config

# 測試Python
python --version

# 測試pip
pip --version
```

### 2. 安裝套件
```cmd
# 安裝套件
pip install package_name

# 列出已安裝套件
pip list
```

### 3. 建立虛擬環境（推薦）
```cmd
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate

# 停用虛擬環境
deactivate
```

## 📋 檔案說明

### 核心配置檔案
- **`.python_config`** - Python路徑配置檔案，包含所有Python相關路徑設定
- **`python.bat`** - Python命令執行器，讓您可以直接使用 `python` 命令
- **`pip.bat`** - pip命令執行器，讓您可以直接使用 `pip` 命令
- **`setup_python.bat`** - 一鍵設定Python環境的批次檔案

## ⭐ 優點

- ✅ **不影響系統PATH** - 所有設定都是專案本地的
- ✅ **版本隔離** - 每個專案可以有自己的Python環境
- ✅ **避免衝突** - 避免不同Python版本之間的衝突
- ✅ **安全管理** - 更安全的開發環境管理
- ✅ **易於維護** - 配置集中在`.python_config`檔案中

## ⚠️ 注意事項

- 每次開啟新的命令提示字元都需要重新執行設定
- 建議將設定檔案加入專案的版本控制中
- 如果Python安裝路徑不同，請修改`.python_config`檔案中的路徑
- 使用虛擬環境可以進一步隔離專案依賴

## 🔄 維護說明

### 修改Python路徑
如需修改Python路徑，請編輯 `python_config\.python_config` 檔案：

```ini
PYTHON_EXE=C:\Python313\python.exe
PIP_EXE=C:\Python313\Scripts\pip.exe
PYTHON_DIR=C:\Python313
PYTHON_SCRIPTS=C:\Python313\Scripts
```

### 更新Python版本
1. 下載新版本Python安裝程式
2. 安裝到新的目錄（如 `C:\Python314`）
3. 更新 `.python_config` 檔案中的路徑
4. 測試新版本是否正常工作

---

**最後更新**: 2025年7月2日  
**Python版本**: 3.13.5  
**安裝路徑**: `C:\Python313` 