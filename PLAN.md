# PLAN: 小红书笔记数据全自动抓取 (XHS Scraper)

## 1. 目标文件: `src/xhs_scraper.py`
## 2. 核心逻辑:
- 使用 `playwright` (async API) 库。
- 实现 `fetch_note_data(url)` 异步函数。
- 启动浏览器时必须设置 `headless=False` 以规避简单的人机检测。
- 导航到 URL 后，等待 `.note-content` 或类似的核心内容加载 (Timeout 10s)。
- 抓取字段：
    - `likes`: 点赞数 (CSS: .interact-container .like-wrapper .count)
    - `collects`: 收藏数 (CSS: .interact-container .collect-wrapper .count)
    - `title`: 标题 (CSS: #detail-title)
- 返回字典 `{'likes': '...', 'collects': '...', 'title': '...'}`。
- 错误处理：如果超时或选择器未找到，返回 `None` 或抛出包含 `ScraperError` 的异常。

## 3. 测试要求:
- 创建 `tests/test_xhs_scraper.py`。
- 使用 `pytest-asyncio`。
- 测试必须 Mock `playwright` 的 Page 对象，不要真的发起网络请求（为了快速验证逻辑）。
- 验证当 HTML 包含特定结构时，能否正确解析出数字。
