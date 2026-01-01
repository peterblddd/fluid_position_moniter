#!/usr/bin/env python3
"""
Fluid Protocol 客户端
使用完整ABI通过RPC获取链上数据
"""

from web3 import Web3
import json
import logging
from typing import List, Dict, Optional, Union

logger = logging.getLogger(__name__)

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

KNOWN_TOKENS = {
    "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": ("ETH", 18),
    "0x0000000000000000000000000000000000000000": ("ETH", 18),
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH", 18),
    "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": ("wstETH", 18),
    "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": ("GHO", 18),
    "0x80ac24aa929eaf5013f6436cda2a7ba190f5cc0b": ("syrupUSDC", 6),
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", 6),
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
}


class FluidClient:
    """Fluid Protocol 数据客户端"""
    
    DEFAULT_RESOLVER_ADDRESS = "0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0"
    
    def __init__(self, rpc_url: str, resolver_address: str = None, abi_path: str = None):
        self.rpc_url = rpc_url
        self.resolver_address = resolver_address or self.DEFAULT_RESOLVER_ADDRESS
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        try:
            block = self.w3.eth.block_number
            logger.info(f"RPC连接成功，当前区块: {block}")
        except Exception as e:
            raise ConnectionError(f"无法连接到RPC: {rpc_url}, 错误: {e}")
        
        if abi_path:
            with open(abi_path, 'r') as f:
                abi = json.load(f)
        else:
            import os
            default_abi_path = os.path.join(os.path.dirname(__file__), 'FluidVaultResolver.json')
            with open(default_abi_path, 'r') as f:
                abi = json.load(f)
        
        self.resolver = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.resolver_address),
            abi=abi
        )
        
        self._token_cache = {k.lower(): v for k, v in KNOWN_TOKENS.items()}
    
    def _get_token_info(self, token_address: str) -> tuple:
        """获取token的symbol和decimals"""
        addr_lower = token_address.lower()
        
        if addr_lower in self._token_cache:
            return self._token_cache[addr_lower]
        
        if addr_lower in ["0x0000000000000000000000000000000000000000", 
                          "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"]:
            return "ETH", 18
        
        try:
            token = self.w3.eth.contract(
                address=self.w3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            symbol = token.functions.symbol().call()
            decimals = token.functions.decimals().call()
            self._token_cache[addr_lower] = (symbol, decimals)
            return symbol, decimals
        except Exception as e:
            logger.warning(f"获取token信息失败 {token_address}: {e}")
            return "Unknown", 18
    
    def get_position_by_id(self, nft_id: Union[int, str]) -> List[Dict]:
        """通过NFT ID获取position信息"""
        try:
            nft_id = int(str(nft_id).strip())
            logger.info(f"获取Position #{nft_id}")
            
            result = self.resolver.functions.positionByNftId(nft_id).call()
            position = self._parse_position_data(result[0], result[1])
            
            if position:
                return [position]
            return []
            
        except Exception as e:
            logger.error(f"获取Position #{nft_id} 失败: {e}")
            return []
    
    def get_user_positions(self, address: str) -> List[Dict]:
        """获取用户的所有positions"""
        try:
            address = self.w3.to_checksum_address(address.strip())
            logger.info(f"获取用户 {address[:10]}... 的positions")
            
            result = self.resolver.functions.positionsByUser(address).call()
            
            user_positions = result[0]
            vaults_data = result[1]
            
            positions = []
            for i in range(len(user_positions)):
                position = self._parse_position_data(user_positions[i], vaults_data[i])
                if position:
                    positions.append(position)
            
            logger.info(f"找到 {len(positions)} 个positions")
            return positions
            
        except Exception as e:
            logger.error(f"获取用户positions失败: {e}")
            return []
    
    def _parse_position_data(self, user_position: tuple, vault_data: tuple) -> Optional[Dict]:
        """解析position数据"""
        try:
            nft_id = user_position[0]
            owner = user_position[1]
            is_liquidated = user_position[2]
            supply_raw = user_position[9]
            borrow_raw = user_position[10]
            
            vault_address = vault_data[0]
            constant_views = vault_data[3]
            configs = vault_data[4]
            
            supply_tokens = constant_views[8]
            borrow_tokens = constant_views[9]
            
            supply_token_addr = supply_tokens[0] if supply_tokens[0] != "0x0000000000000000000000000000000000000000" else supply_tokens[1]
            borrow_token_addr = borrow_tokens[0] if borrow_tokens[0] != "0x0000000000000000000000000000000000000000" else borrow_tokens[1]
            
            supply_symbol, supply_decimals = self._get_token_info(supply_token_addr)
            borrow_symbol, borrow_decimals = self._get_token_info(borrow_token_addr)
            
            # configs: [2] collateralFactor, [3] liquidationThreshold (1e2精度，即9200=92%)
            collateral_factor = configs[2]  # 例如 9000 = 90%
            liquidation_threshold = configs[3]  # 例如 9200 = 92%
            oracle_price = configs[9]
            
            supply_amount = supply_raw / (10 ** supply_decimals)
            borrow_amount = borrow_raw / (10 ** borrow_decimals)
            
            # 计算USD价值
            # supply_value_in_borrow = supply_raw * oracle_price / 1e27 / 10^borrow_decimals
            supply_value_in_borrow = (supply_raw * oracle_price) / (10 ** 27) / (10 ** borrow_decimals)
            
            # 假设 borrow_token 是稳定币，价值约为 1 USD
            supply_usd = supply_value_in_borrow
            borrow_usd = borrow_amount
            
            # 计算抵押率 (Ratio) = borrow_usd / supply_usd * 100
            if supply_usd > 0:
                ratio = (borrow_usd / supply_usd) * 100
            else:
                ratio = 0
            
            # 计算健康因子
            # Health Factor = (Liquidation Threshold %) / (Ratio %)
            # 例如: 92% / 85.77% = 1.0726
            # liquidation_threshold 是 1e2 精度，所以 9200 = 92%
            # ratio 已经是百分比形式
            if ratio > 0:
                health_factor = (liquidation_threshold / 100) / ratio
            else:
                health_factor = float('inf')
            
            return {
                'nftId': nft_id,
                'owner': owner,
                'vault': vault_address,
                'supply_token': supply_symbol,
                'supply_amount': supply_amount,
                'supply_usd': supply_usd,
                'borrow_token': borrow_symbol,
                'borrow_amount': borrow_amount,
                'borrow_usd': borrow_usd,
                'health_factor': health_factor,
                'ratio': ratio,
                'collateral_factor': collateral_factor / 100,
                'liquidation_threshold': liquidation_threshold / 100,
                'is_liquidated': is_liquidated,
            }
            
        except Exception as e:
            logger.error(f"解析position数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def create_fluid_client(rpc_url: str, resolver_address: str = None) -> FluidClient:
    """创建Fluid客户端实例"""
    return FluidClient(rpc_url, resolver_address)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu"
    
    print("=" * 60)
    print("Fluid Protocol 客户端测试")
    print("=" * 60)
    
    try:
        client = FluidClient(RPC_URL)
        
        print("\n测试1: 通过ID获取Position #9540")
        print("-" * 40)
        positions = client.get_position_by_id(9540)
        for pos in positions:
            print(f"\nPosition #{pos['nftId']}:")
            print(f"  Owner: {pos['owner']}")
            print(f"  Collateral: {pos['supply_amount']:.4f} {pos['supply_token']} (${pos['supply_usd']:.2f})")
            print(f"  Debt: {pos['borrow_amount']:.4f} {pos['borrow_token']} (${pos['borrow_usd']:.2f})")
            print(f"  Ratio: {pos['ratio']:.2f}%")
            print(f"  Health Factor: {pos['health_factor']:.6f}")
            print(f"  Liquidation Threshold: {pos['liquidation_threshold']:.2f}%")
        
        print("\n\n测试2: 通过地址获取Positions")
        print("-" * 40)
        test_address = "0x478E169b3f828806Fb655A4ea46D40eAde7B1d61"
        positions = client.get_user_positions(test_address)
        print(f"地址 {test_address[:10]}... 有 {len(positions)} 个positions")
        for pos in positions:
            print(f"\n  Position #{pos['nftId']}: {pos['supply_token']}/{pos['borrow_token']}")
            print(f"    Collateral: {pos['supply_amount']:.6f} {pos['supply_token']} (${pos['supply_usd']:.2f})")
            print(f"    Debt: {pos['borrow_amount']:.6f} {pos['borrow_token']} (${pos['borrow_usd']:.2f})")
            print(f"    Health Factor: {pos['health_factor']:.6f}")
            print(f"    Ratio: {pos['ratio']:.2f}%")
        
        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
