#!/usr/bin/env python3
"""
Web Change Monitor - Main Monitor Script
主监控程序：定时轮询检测网页内容变化
"""

import json
import os
import sys
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 技能目录
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"
HISTORY_DIR = DATA_DIR / "history"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)


class WebChangeMonitor:
    """网页变化监控器"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(CONFIG_FILE)
        self.targets = []
        self.history = {}
        self.running = False
        self.threads = []
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.targets = config.get('targets', [])
                self.interval = config.get('interval', 30)
                self.return_on_change_only = config.get('return_on_change_only', True)
        else:
            self.targets = []
            self.interval = 30
            self.return_on_change_only = True
    
    def save_config(self):
        """保存配置"""
        config = {
            'targets': self.targets,
            'interval': self.interval,
            'return_on_change_only': self.return_on_change_only
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def add_target(self, target: Dict[str, Any]):
        """添加监控目标"""
        if 'url' not in target:
            raise ValueError("url is required")
        
        # 检查是否已存在
        for t in self.targets:
            if t['url'] == target['url']:
                logger.warning(f"Target {target['url']} already exists, updating...")
                t.update(target)
                self.save_config()
                return
        
        self.targets.append(target)
        self.save_config()
        logger.info(f"Added target: {target['url']}")
    
    def remove_target(self, url: str):
        """移除监控目标"""
        self.targets = [t for t in self.targets if t['url'] != url]
        self.save_config()
        logger.info(f"Removed target: {url}")
    
    def fetch_page(self, target: Dict[str, Any]) -> str:
        """抓取网页内容"""
        url = target['url']
        method = target.get('method', 'GET').upper()
        headers = target.get('headers', {})
        payload = target.get('payload')
        
        # 默认 User-Agent
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=payload, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return f"ERROR: {e}"
    
    def extract_content(self, html: str, target: Dict[str, Any]) -> str:
        """从 HTML 中提取内容"""
        selector = target.get('selector')
        xpath = target.get('xpath')
        keyword = target.get('keyword')
        
        # 错误页面
        if html.startswith('ERROR:'):
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # XPath 提取（需要 lxml）
        if xpath:
            try:
                elements = soup.xpath(xpath)
                if elements:
                    return ' '.join([el.text.strip() for el in elements])
            except Exception as e:
                logger.warning(f"XPath failed: {e}")
        
        # CSS 选择器提取
        if selector:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # 关键词搜索
        if keyword:
            text = soup.get_text()
            if keyword in text:
                # 返回包含关键词的上下文
                idx = text.find(keyword)
                start = max(0, idx - 50)
                end = min(len(text), idx + len(keyword) + 50)
                return f"...{text[start:end]}..."
        
        # 默认返回纯文本
        return soup.get_text(strip=True)[:500]
    
    def compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def load_history(self, url: str) -> Optional[str]:
        """加载历史哈希"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        history_file = HISTORY_DIR / f"{url_hash}.jsonl"
        
        if not history_file.exists():
            return None
        
        # 读取最后一行
        with open(history_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_record = json.loads(lines[-1])
                return last_record.get('hash')
        
        return None
    
    def save_history(self, url: str, content: str, content_hash: str):
        """保存历史记录"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        history_file = HISTORY_DIR / f"{url_hash}.jsonl"
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'content': content[:200],  # 只保存前 200 字符
            'hash': content_hash
        }
        
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def check_target(self, target: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查单个目标"""
        url = target['url']
        
        # 抓取页面
        html = self.fetch_page(target)
        
        # 提取内容
        content = self.extract_content(html, target)
        
        # 计算哈希
        content_hash = self.compute_hash(content)
        
        # 加载历史
        previous_hash = self.load_history(url)
        
        # 检测变化
        changed = previous_hash is not None and content_hash != previous_hash
        
        # 保存历史
        self.save_history(url, content, content_hash)
        
        # 返回结果
        if changed or not self.return_on_change_only:
            return {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'content': content,
                'changed': changed,
                'hash': content_hash,
                'previous_hash': previous_hash
            }
        
        return None
    
    def monitor_target(self, target: Dict[str, Any], stop_event: threading.Event):
        """监控单个目标（后台线程）"""
        interval = target.get('interval', self.interval)
        url = target.get('url', 'unknown')
        
        logger.info(f"Started monitoring {url} every {interval}s")
        
        while not stop_event.is_set():
            try:
                result = self.check_target(target)
                
                if result:
                    # 输出结果
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    
            except Exception as e:
                logger.error(f"Error monitoring {url}: {e}")
            
            # 等待下一次检查
            stop_event.wait(interval)
        
        logger.info(f"Stopped monitoring {url}")
    
    def start(self):
        """启动监控"""
        if self.running:
            logger.warning("Monitor is already running")
            return
        
        self.running = True
        stop_event = threading.Event()
        
        for target in self.targets:
            thread = threading.Thread(
                target=self.monitor_target,
                args=(target, stop_event),
                daemon=True
            )
            thread.start()
            self.threads.append((thread, stop_event))
        
        logger.info(f"Started monitoring {len(self.targets)} targets")
    
    def stop(self):
        """停止监控"""
        for thread, stop_event in self.threads:
            stop_event.set()
        
        for thread, _ in self.threads:
            thread.join(timeout=5)
        
        self.threads = []
        self.running = False
        
        logger.info("Stopped all monitors")
    
    def status(self) -> Dict[str, Any]:
        """查看状态"""
        return {
            'running': self.running,
            'targets_count': len(self.targets),
            'targets': self.targets,
            'interval': self.interval,
            'return_on_change_only': self.return_on_change_only
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Change Monitor')
    parser.add_argument('--config', type=str, default=str(CONFIG_FILE), help='配置文件路径')
    parser.add_argument('--add', type=str, help='添加监控目标（JSON 格式）')
    parser.add_argument('--remove', type=str, help='移除监控目标（URL）')
    parser.add_argument('--start', action='store_true', help='启动监控')
    parser.add_argument('--stop', action='store_true', help='停止监控')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--once', action='store_true', help='只检查一次')
    
    args = parser.parse_args()
    
    monitor = WebChangeMonitor(args.config)
    
    if args.add:
        target = json.loads(args.add)
        monitor.add_target(target)
        print(f"Added target: {target.get('url')}")
    
    elif args.remove:
        monitor.remove_target(args.remove)
        print(f"Removed target: {args.remove}")
    
    elif args.status:
        status = monitor.status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.start:
        monitor.start()
        print("Monitor started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
    
    elif args.stop:
        monitor.stop()
        print("Monitor stopped")
    
    elif args.once:
        results = []
        for target in monitor.targets:
            result = monitor.check_target(target)
            if result:
                results.append(result)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
