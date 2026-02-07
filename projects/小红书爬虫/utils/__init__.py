"""
Antigravity 核心工具模块

提供 Antigravity 框架的核心工具函数和类。
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs

import pandas as pd
import requests
from playwright.async_api import async_playwright, Browser, Page

from antigravity.performance_monitor import track_performance


class XiaohongshuHelper:
    """小红书爬虫工具类"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化小红书爬虫工具
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self._setup_session()
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "settings.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"配置文件加载成功: {config_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1.0,
                "data_dir": "data"
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            raise
    
    def _setup_session(self) -> None:
        """设置请求会话"""
        user_agent = self.config.get(
            "user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
    
    @track_performance
    def make_request(
        self, 
        url: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Optional[requests.Response]:
        """
        发送HTTP请求，支持重试机制
        
        Args:
            url: 请求URL
            method: HTTP方法
            params: 查询参数
            data: 请求体数据
            headers: 请求头
            timeout: 超时时间
            
        Returns:
            响应对象，失败时返回None
        """
        if timeout is None:
            timeout = self.config.get("timeout", 30)
        
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)
        
        for attempt in range(max_retries):
            try:
                # 添加随机延迟避免被检测
                if attempt > 0:
                    delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                
                # 合并请求头
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # 发送请求
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=timeout
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                self.logger.debug(f"请求成功: {url} (状态码: {response.status_code})")
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"请求最终失败: {url}")
                    return None
    
    def extract_user_id_from_url(self, url: str) -> Optional[str]:
        """
        从小红书用户URL中提取用户ID
        
        Args:
            url: 小红书用户主页URL
            
        Returns:
            用户ID，如果无法提取则返回None
        """
        try:
            parsed_url = urlparse(url)
            
            # 处理不同格式的URL
            if "xiaohongshu.com/user/profile" in url:
                # 格式: https://www.xiaohongshu.com/user/profile/{user_id}
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 3 and path_parts[-2] == "profile":
                    return path_parts[-1]
            
            elif "xiaohongshu.com/user" in url:
                # 格式: https://www.xiaohongshu.com/user/{user_id}
                path_parts = parsed_url.path.strip('/').split('/')
                if len(path_parts) >= 2 and path_parts[0] == "user":
                    return path_parts[1]
            
            # 尝试从查询参数中提取
            query_params = parse_qs(parsed_url.query)
            if 'user_id' in query_params:
                return query_params['user_id'][0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"提取用户ID失败: {e}")
            return None
    
    def validate_user_url(self, url: str) -> bool:
        """
        验证小红书用户URL是否有效
        
        Args:
            url: 待验证的URL
            
        Returns:
            是否有效
        """
        if not url:
            return False
        
        # 检查URL格式
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
        
        # 检查是否为小红书域名
        if "xiaohongshu.com" not in parsed_url.netloc:
            return False
        
        # 检查是否为用户相关页面
        if "/user/" not in parsed_url.path:
            return False
        
        return True
    
    @track_performance
    async def create_browser_context(
        self, 
        headless: bool = True,
        proxy: Optional[Dict[str, str]] = None
    ) -> tuple[Browser, Page]:
        """
        创建浏览器上下文
        
        Args:
            headless: 是否无头模式
            proxy: 代理设置
            
        Returns:
            (浏览器实例, 页面实例)
        """
        try:
            playwright = await async_playwright().start()
            
            launch_options = {
                "headless": headless,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            }
            
            if proxy:
                launch_options["proxy"] = proxy
            
            browser = await playwright.chromium.launch(**launch_options)
            
            # 创建上下文和页面
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=self.config.get(
                    "user_agent", 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            )
            
            # 添加反检测脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
            """)
            
            page = await context.new_page()
            
            self.logger.info("浏览器上下文创建成功")
            return browser, page
            
        except Exception as e:
            self.logger.error(f"创建浏览器上下文失败: {e}")
            raise
    
    async def wait_for_network_idle(
        self, 
        page: Page, 
        timeout: float = 30.0,
        idle_time: float = 2.0
    ) -> None:
        """
        等待网络空闲
        
        Args:
            page: 页面对象
            timeout: 超时时间
            idle_time: 空闲时间阈值
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
            # 额外等待确保完全加载
            await asyncio.sleep(idle_time)
        except Exception as e:
            self.logger.warning(f"等待网络空闲超时: {e}")
    
    def generate_filename(
        self, 
        task_name: str, 
        file_format: str = "json",
        timestamp_format: str = "%Y%m%d_%H%M%S"
    ) -> str:
        """
        生成数据文件名
        
        Args:
            task_name: 任务名称
            file_format: 文件格式
            timestamp_format: 时间戳格式
            
        Returns:
            文件名
        """
        timestamp = datetime.now().strftime(timestamp_format)
        return f"{task_name}_{timestamp}.{file_format}"
    
    def save_data(
        self, 
        data: Union[Dict, List, pd.DataFrame], 
        task_name: str,
        data_dir: Optional[Path] = None
    ) -> Path:
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            task_name: 任务名称
            data_dir: 数据目录，如果为None则使用配置中的目录
            
        Returns:
            保存的文件路径
        """
        if data_dir is None:
            data_dir = Path(self.config.get("data_dir", "data"))
        
        # 确保目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if isinstance(data, pd.DataFrame):
            file_format = "csv"
        else:
            file_format = "json"
        
        filename = self.generate_filename(task_name, file_format)
        file_path = data_dir / filename
        
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据保存成功: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            raise
    
    def load_data(self, file_path: Path) -> Union[Dict, List, pd.DataFrame]:
        """
        从文件加载数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据
        """
        try:
            if file_path.suffix == '.csv':
                return pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
                
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            raise
    
    def cleanup_old_files(
        self, 
        data_dir: Optional[Path] = None,
        max_files: int = 100,
        max_age_days: int = 30
    ) -> None:
        """
        清理旧的数据文件
        
        Args:
            data_dir: 数据目录
            max_files: 最大文件数量
            max_age_days: 最大保留天数
        """
        if data_dir is None:
            data_dir = Path(self.config.get("data_dir", "data"))
        
        if not data_dir.exists():
            return
        
        # 获取所有文件并按修改时间排序
        files = list(data_dir.glob("*.*"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        deleted_count = 0
        for i, file_path in enumerate(files):
            should_delete = False
            
            # 检查文件数量限制
            if i >= max_files:
                should_delete = True
            
            # 检查文件年龄
            file_age = time.time() - file_path.stat().st_mtime
            if file_age > cutoff_time:
                should_delete = True
            
            if should_delete:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.logger.warning(f"删除文件失败 {file_path}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"清理了 {deleted_count} 个旧文件")
    
    def close(self) -> None:
        """清理资源"""
        self.session.close()
        self.logger.info("资源清理完成")


# 单例实例
_helper_instance: Optional[XiaohongshuHelper] = None


def get_helper(config_path: Optional[Path] = None) -> XiaohongshuHelper:
    """
    获取小红书爬虫工具实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        小红书爬虫工具实例
    """
    global _helper_instance
    
    if _helper_instance is None:
        _helper_instance = XiaohongshuHelper(config_path)
    
    return _helper_instance


def setup_logging(level: int = logging.INFO) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_related_test(file_path: Path) -> Optional[Path]:
    """
    获取与给定文件相关的测试文件路径
    
    Args:
        file_path: 源文件路径
        
    Returns:
        测试文件路径，如果不存在则返回None
    """
    # 将文件路径转换为测试文件路径
    # 例如: projects/xiaohongshu_crawler/core/crawler.py -> 
    #       tests/test_crawler.py
    
    # 获取文件名（不含扩展名）
    file_name = file_path.stem
    
    # 构建测试文件名
    test_file_name = f"test_{file_name}.py"
    
    # 查找测试文件
    # 首先在项目根目录的tests文件夹中查找
    project_root = file_path.parent.parent
    test_path = project_root / "tests" / test_file_name
    
    if test_path.exists():
        return test_path
    
    # 如果不存在，返回None
    return None