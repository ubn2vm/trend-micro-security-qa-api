# 引入 logging 模組
import logging

# 設定日誌
# basicConfig 是ㄧ個簡易的日誌設定函式，通常在程式啟動時執行一次
logging.basicConfig(
    # level=logging.INFO: 設定日誌記錄的最低層級。
    # 意思是，只有嚴重程度在 INFO 以上的訊息才會被記錄下來。
    # 層級由低到高分別是：DEBUG, INFO, WARNING, ERROR, CRITICAL
    level=logging.INFO,

    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s':
    # 這是在定義日誌輸出的格式。
    # %(asctime)s: 事件發生的時間 (例如：2025-07-04 13:00:00,123)
    # %(name)s:    Logger 的名稱。使用 __name__ 是ㄧ個好習慣，它會自動設為該 Python 模組的名稱。
    # %(levelname)s: 日誌的層級名稱 (例如：INFO, WARNING)
    # %(message)s:  你實際要記錄的訊息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 獲取一個 Logger 實例。
# 傳入 __name__ 可以讓你知道這條日誌是從哪個模組發出的，
# 這在大型專案中對於追蹤問題來源非常有幫助。
logger = logging.getLogger(__name__)

# --- 如何使用 ---
def my_function(a, b):
    logger.info(f"開始執行 my_function，傳入參數 a={a}, b={b}")
    try:
        result = a / b
        logger.info(f"計算成功，結果為 {result}")
        return result
    except ZeroDivisionError as e:
        # 使用 logger.error 或 logger.exception 來記錄錯誤
        # logger.exception 會額外附加詳細的錯誤堆疊資訊
        logger.exception(f"發生除以零的錯誤: {e}")
        return None

my_function(10, 2)
my_function(10, 0)