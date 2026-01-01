#!/usr/bin/env python3
"""
Fluid Protocol 网页抓取器
使用Selenium获取实时数据
"""

import re
import json
import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class FluidScraper:
    """
    使用Selenium抓取Fluid.io数据
    """
    
    BASE_URL = "https://fluid.io"
    POSITIONS_URL = "https://fluid.io/stats/1/vaults/positions"
    
    def __init__(self):
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver初始化成功")
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {e}")
            self.driver = None
    
    def close(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def __del__(self):
        self.close()
    
    def get_positions(self, limit: int = 100) -> List[Dict]:
        """
        获取positions列表
        """
        if not self.driver:
            logger.error("WebDriver未初始化")
            return []
        
        try:
            logger.info(f"访问 {self.POSITIONS_URL}")
            self.driver.get(self.POSITIONS_URL)
            
            # 等待页面加载
            time.sleep(5)
            
            # 等待表格出现
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
            except TimeoutException:
                logger.warning("等待表格超时")
            
            # 获取页面源码
            html = self.driver.page_source
            
            # 解析positions
            positions = self._parse_positions_html(html)
            
            logger.info(f"获取到 {len(positions)} 个positions")
            return positions[:limit]
            
        except Exception as e:
            logger.error(f"获取positions失败: {e}")
            return []
    
    def _parse_positions_html(self, html: str) -> List[Dict]:
        """解析HTML中的positions数据"""
        positions = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找表格行
            rows = soup.find_all('tr')
            
            for row in rows:
                try:
                    # 获取行文本
                    row_text = row.get_text(' ', strip=True)
                    
                    # 跳过表头
                    if 'ID' in row_text and 'Symbol' in row_text:
                        continue
                    
                    # 尝试提取NFT ID (4-5位数字)
                    id_match = re.search(r'\b(\d{4,5})\b', row_text)
                    if not id_match:
                        continue
                    
                    nft_id = int(id_match.group(1))
                    
                    # 提取其他数据
                    position = self._extract_position_data(row_text, nft_id)
                    if position:
                        positions.append(position)
                        
                except Exception as e:
                    logger.debug(f"解析行失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析HTML失败: {e}")
        
        return positions
    
    def _extract_position_data(self, text: str, nft_id: int) -> Optional[Dict]:
        """从文本中提取position数据"""
        try:
            position = {
                'nftId': nft_id,
                'owner': '',
                'supply_token': '',
                'supply_amount': 0,
                'supply_usd': 0,
                'borrow_token': '',
                'borrow_amount': 0,
                'borrow_usd': 0,
                'health_factor': 0,
                'ratio': 0,
                'is_liquidated': False,
            }
            
            # 提取owner地址 (格式: 0x1234...5678)
            owner_match = re.search(r'(0x[a-fA-F0-9]{4}\.{3}[a-fA-F0-9]{4})', text)
            if owner_match:
                position['owner'] = owner_match.group(1)
            
            # 提取symbol (格式: TOKEN1 / TOKEN2)
            symbol_match = re.search(r'(\w+(?:USDC|ETH|USDT|GHO|wstETH|BTC)?)\s*/\s*(\w+)', text)
            if symbol_match:
                position['supply_token'] = symbol_match.group(1)
                position['borrow_token'] = symbol_match.group(2)
            
            # 提取ratio (百分比)
            ratio_match = re.search(r'(\d+\.?\d*)%', text)
            if ratio_match:
                position['ratio'] = float(ratio_match.group(1))
            
            # 提取health factor (格式: 1.234567)
            hf_match = re.search(r'(\d+\.\d{4,})', text)
            if hf_match:
                position['health_factor'] = float(hf_match.group(1))
            
            # 提取supply金额
            supply_match = re.search(r'([\d,]+\.?\d*)\s+' + re.escape(position['supply_token']), text)
            if supply_match:
                position['supply_amount'] = float(supply_match.group(1).replace(',', ''))
            
            # 提取borrow金额
            borrow_match = re.search(r'([\d,]+\.?\d*)\s+' + re.escape(position['borrow_token']), text)
            if borrow_match:
                position['borrow_amount'] = float(borrow_match.group(1).replace(',', ''))
            
            # 提取USD价值
            usd_matches = re.findall(r'\$([\d,]+\.?\d*)', text)
            if len(usd_matches) >= 2:
                position['supply_usd'] = float(usd_matches[0].replace(',', ''))
                position['borrow_usd'] = float(usd_matches[1].replace(',', ''))
            
            # 检查是否已清算
            position['is_liquidated'] = 'liquidated' in text.lower()
            
            return position
            
        except Exception as e:
            logger.error(f"提取position数据失败: {e}")
            return None
    
    def get_position_by_id(self, nft_id: int) -> Optional[Dict]:
        """通过NFT ID获取单个position"""
        positions = self.get_positions()
        for pos in positions:
            if pos['nftId'] == nft_id:
                return pos
        return None
    
    def get_user_positions(self, address: str) -> List[Dict]:
        """获取用户的所有positions"""
        address = address.lower()
        positions = self.get_positions()
        
        user_positions = []
        for pos in positions:
            owner = pos.get('owner', '').lower()
            if address in owner or owner in address:
                user_positions.append(pos)
            # 支持缩写地址匹配
            elif address.startswith('0x') and len(address) > 10:
                short_addr = f"{address[:6]}...{address[-4:]}"
                if short_addr.lower() in owner.lower():
                    user_positions.append(pos)
        
        return user_positions


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("初始化Scraper...")
    scraper = FluidScraper()
    
    if scraper.driver:
        print("\n获取positions...")
        positions = scraper.get_positions(limit=10)
        
        print(f"\n获取到 {len(positions)} 个positions:")
        for pos in positions:
            print(f"\n  #{pos['nftId']}: {pos['supply_token']}/{pos['borrow_token']}")
            print(f"    Owner: {pos['owner']}")
            print(f"    Health Factor: {pos['health_factor']}")
            print(f"    Ratio: {pos['ratio']}%")
        
        scraper.close()
    else:
        print("WebDriver初始化失败")
