#!/usr/bin/env python3
"""
使用完整ABI测试RPC数据获取
"""

from web3 import Web3
import json

# 配置
RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu"
VAULT_RESOLVER_ADDRESS = "0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0"

# 加载完整ABI
with open('/home/ubuntu/fluid_bot/FluidVaultResolver.json', 'r') as f:
    VAULT_RESOLVER_ABI = json.load(f)

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

def get_token_info(w3, token_address):
    """获取token信息"""
    try:
        if token_address == "0x0000000000000000000000000000000000000000":
            return "ETH", 18
        token = w3.eth.contract(
            address=w3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        symbol = token.functions.symbol().call()
        decimals = token.functions.decimals().call()
        return symbol, decimals
    except Exception as e:
        print(f"   ⚠️ 获取token信息失败 {token_address}: {e}")
        return "Unknown", 18

def test_position_by_id(w3, resolver, nft_id=9540):
    """测试通过NFT ID获取position"""
    print(f"\n获取Position #{nft_id}...")
    
    try:
        result = resolver.functions.positionByNftId(nft_id).call()
        
        # 解析返回结果
        user_position = result[0]
        vault_data = result[1]
        
        print(f"\n✅ 成功获取Position数据!")
        
        # UserPosition 结构
        print(f"\n📊 Position信息:")
        print(f"   NFT ID: {user_position[0]}")
        print(f"   Owner: {user_position[1]}")
        print(f"   Is Liquidated: {user_position[2]}")
        print(f"   Is Supply Position: {user_position[3]}")
        print(f"   Supply (raw): {user_position[9]}")
        print(f"   Borrow (raw): {user_position[10]}")
        
        # VaultEntireData 结构
        print(f"\n🏦 Vault信息:")
        print(f"   Vault地址: {vault_data[0]}")
        print(f"   Is Smart Col: {vault_data[1]}")
        print(f"   Is Smart Debt: {vault_data[2]}")
        
        # ConstantViews (索引3)
        constant_views = vault_data[3]
        print(f"\n📋 ConstantViews:")
        print(f"   Liquidity: {constant_views[0]}")
        print(f"   Factory: {constant_views[1]}")
        print(f"   Supply address: {constant_views[6]}")
        print(f"   Borrow address: {constant_views[7]}")
        
        # supplyToken (索引8) 和 borrowToken (索引9) 是 Tokens 结构
        supply_tokens = constant_views[8]  # (token0, token1)
        borrow_tokens = constant_views[9]  # (token0, token1)
        
        print(f"   Supply Token0: {supply_tokens[0]}")
        print(f"   Supply Token1: {supply_tokens[1]}")
        print(f"   Borrow Token0: {borrow_tokens[0]}")
        print(f"   Borrow Token1: {borrow_tokens[1]}")
        
        # 获取token信息
        # 对于普通vault，token0是主要token，token1是零地址
        supply_token_addr = supply_tokens[0] if supply_tokens[0] != "0x0000000000000000000000000000000000000000" else supply_tokens[1]
        borrow_token_addr = borrow_tokens[0] if borrow_tokens[0] != "0x0000000000000000000000000000000000000000" else borrow_tokens[1]
        
        supply_symbol, supply_decimals = get_token_info(w3, supply_token_addr)
        borrow_symbol, borrow_decimals = get_token_info(w3, borrow_token_addr)
        
        print(f"\n📈 Token信息:")
        print(f"   Supply Token: {supply_symbol} (decimals: {supply_decimals})")
        print(f"   Borrow Token: {borrow_symbol} (decimals: {borrow_decimals})")
        
        # Configs (索引4)
        configs = vault_data[4]
        print(f"\n⚙️ Configs:")
        print(f"   Supply Rate Magnifier: {configs[0]}")
        print(f"   Borrow Rate Magnifier: {configs[1]}")
        print(f"   Collateral Factor: {configs[2] / 100}%")
        print(f"   Liquidation Threshold: {configs[3] / 100}%")
        print(f"   Oracle: {configs[8]}")
        print(f"   Oracle Price Operate: {configs[9]}")
        print(f"   Oracle Price Liquidate: {configs[10]}")
        
        # 计算实际数量
        supply_raw = user_position[9]
        borrow_raw = user_position[10]
        supply_amount = supply_raw / (10 ** supply_decimals)
        borrow_amount = borrow_raw / (10 ** borrow_decimals)
        
        print(f"\n💰 数量:")
        print(f"   Supply: {supply_amount:.6f} {supply_symbol}")
        print(f"   Borrow: {borrow_amount:.6f} {borrow_symbol}")
        
        # 计算USD价值和健康因子
        oracle_price = configs[9]  # oraclePriceOperate
        liquidation_threshold = configs[3]  # 1e2精度
        
        # Oracle价格是 supply/borrow 的比率，精度是 1e27
        # 对于稳定币对，价格接近1
        price_ratio = oracle_price / 1e27
        
        # 计算抵押率 (Ratio) = (borrow * price) / supply * 100
        if supply_amount > 0:
            # 需要考虑decimals差异
            ratio = (borrow_amount / (supply_amount * price_ratio)) * 100
            print(f"\n📊 抵押率: {ratio:.2f}%")
        
        # 计算健康因子
        # Health Factor = (supply * oracle_price * liquidation_threshold) / (borrow * 1e27 * 10000)
        if borrow_raw > 0:
            # 调整decimals差异
            decimal_adjustment = 10 ** (borrow_decimals - supply_decimals) if borrow_decimals != supply_decimals else 1
            health_factor = (supply_raw * oracle_price * liquidation_threshold) / (borrow_raw * 1e27 * 10000 * decimal_adjustment)
            print(f"🛡️ 健康因子: {health_factor:.6f}")
        else:
            print(f"🛡️ 健康因子: ∞ (无借款)")
        
        return {
            'nftId': user_position[0],
            'owner': user_position[1],
            'is_liquidated': user_position[2],
            'supply_token': supply_symbol,
            'supply_amount': supply_amount,
            'supply_decimals': supply_decimals,
            'borrow_token': borrow_symbol,
            'borrow_amount': borrow_amount,
            'borrow_decimals': borrow_decimals,
            'oracle_price': oracle_price,
            'liquidation_threshold': liquidation_threshold,
            'collateral_factor': configs[2],
            'supply_raw': supply_raw,
            'borrow_raw': borrow_raw,
        }
        
    except Exception as e:
        print(f"❌ 获取Position失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Fluid Protocol RPC测试 (使用完整ABI)")
    print("=" * 60)
    
    # 连接RPC
    print("连接RPC...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("❌ RPC连接失败")
        return
    
    print(f"✅ RPC连接成功! 区块: {w3.eth.block_number}")
    
    # 创建合约实例
    resolver = w3.eth.contract(
        address=w3.to_checksum_address(VAULT_RESOLVER_ADDRESS),
        abi=VAULT_RESOLVER_ABI
    )
    
    # 测试获取Position #9540
    result = test_position_by_id(w3, resolver, 9540)
    
    if result:
        print("\n" + "=" * 60)
        print("📋 最终结果汇总")
        print("=" * 60)
        print(f"Position ID: {result['nftId']}")
        print(f"Owner: {result['owner']}")
        print(f"Collateral: {result['supply_amount']:.4f} {result['supply_token']}")
        print(f"Debt: {result['borrow_amount']:.4f} {result['borrow_token']}")
        print(f"Is Liquidated: {result['is_liquidated']}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main()
