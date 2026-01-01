#!/usr/bin/env python3
"""
测试脚本：验证RPC连接和VaultResolver数据获取
"""

from web3 import Web3
import json

# 配置
RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu"
VAULT_RESOLVER_ADDRESS = "0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0"

# VaultResolver ABI (简化版，只包含需要的方法)
VAULT_RESOLVER_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "user_", "type": "address"}],
        "name": "positionsByUser",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "nftId", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "bool", "name": "isLiquidated", "type": "bool"},
                    {"internalType": "bool", "name": "isSupplyPosition", "type": "bool"},
                    {"internalType": "int256", "name": "tick", "type": "int256"},
                    {"internalType": "uint256", "name": "tickId", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeSupply", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeBorrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeDustBorrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "supply", "type": "uint256"},
                    {"internalType": "uint256", "name": "borrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "dustBorrow", "type": "uint256"}
                ],
                "internalType": "struct Structs.UserPosition[]",
                "name": "userPositions_",
                "type": "tuple[]"
            },
            {
                "components": [
                    {"internalType": "address", "name": "vault", "type": "address"},
                    {"internalType": "bool", "name": "isSmartCol", "type": "bool"},
                    {"internalType": "bool", "name": "isSmartDebt", "type": "bool"},
                    {
                        "components": [
                            {"internalType": "address", "name": "supplyToken", "type": "address"},
                            {"internalType": "address", "name": "borrowToken", "type": "address"}
                        ],
                        "internalType": "struct IFluidVault.ConstantViews",
                        "name": "constantVariables",
                        "type": "tuple"
                    },
                    {
                        "components": [
                            {"internalType": "uint16", "name": "supplyRateMagnifier", "type": "uint16"},
                            {"internalType": "uint16", "name": "borrowRateMagnifier", "type": "uint16"},
                            {"internalType": "uint16", "name": "collateralFactor", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationThreshold", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationMaxLimit", "type": "uint16"},
                            {"internalType": "uint16", "name": "withdrawalGap", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationPenalty", "type": "uint16"},
                            {"internalType": "uint16", "name": "borrowFee", "type": "uint16"},
                            {"internalType": "address", "name": "oracle", "type": "address"},
                            {"internalType": "uint256", "name": "oraclePriceOperate", "type": "uint256"},
                            {"internalType": "uint256", "name": "oraclePriceLiquidate", "type": "uint256"},
                            {"internalType": "address", "name": "rebalancer", "type": "address"},
                            {"internalType": "uint256", "name": "lastUpdateTimestamp", "type": "uint256"}
                        ],
                        "internalType": "struct Structs.Configs",
                        "name": "configs",
                        "type": "tuple"
                    }
                ],
                "internalType": "struct Structs.VaultEntireData[]",
                "name": "vaultsData_",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "nftId_", "type": "uint256"}],
        "name": "positionByNftId",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "nftId", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "bool", "name": "isLiquidated", "type": "bool"},
                    {"internalType": "bool", "name": "isSupplyPosition", "type": "bool"},
                    {"internalType": "int256", "name": "tick", "type": "int256"},
                    {"internalType": "uint256", "name": "tickId", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeSupply", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeBorrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "beforeDustBorrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "supply", "type": "uint256"},
                    {"internalType": "uint256", "name": "borrow", "type": "uint256"},
                    {"internalType": "uint256", "name": "dustBorrow", "type": "uint256"}
                ],
                "internalType": "struct Structs.UserPosition",
                "name": "userPosition_",
                "type": "tuple"
            },
            {
                "components": [
                    {"internalType": "address", "name": "vault", "type": "address"},
                    {"internalType": "bool", "name": "isSmartCol", "type": "bool"},
                    {"internalType": "bool", "name": "isSmartDebt", "type": "bool"},
                    {
                        "components": [
                            {"internalType": "address", "name": "supplyToken", "type": "address"},
                            {"internalType": "address", "name": "borrowToken", "type": "address"}
                        ],
                        "internalType": "struct IFluidVault.ConstantViews",
                        "name": "constantVariables",
                        "type": "tuple"
                    },
                    {
                        "components": [
                            {"internalType": "uint16", "name": "supplyRateMagnifier", "type": "uint16"},
                            {"internalType": "uint16", "name": "borrowRateMagnifier", "type": "uint16"},
                            {"internalType": "uint16", "name": "collateralFactor", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationThreshold", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationMaxLimit", "type": "uint16"},
                            {"internalType": "uint16", "name": "withdrawalGap", "type": "uint16"},
                            {"internalType": "uint16", "name": "liquidationPenalty", "type": "uint16"},
                            {"internalType": "uint16", "name": "borrowFee", "type": "uint16"},
                            {"internalType": "address", "name": "oracle", "type": "address"},
                            {"internalType": "uint256", "name": "oraclePriceOperate", "type": "uint256"},
                            {"internalType": "uint256", "name": "oraclePriceLiquidate", "type": "uint256"},
                            {"internalType": "address", "name": "rebalancer", "type": "address"},
                            {"internalType": "uint256", "name": "lastUpdateTimestamp", "type": "uint256"}
                        ],
                        "internalType": "struct Structs.Configs",
                        "name": "configs",
                        "type": "tuple"
                    }
                ],
                "internalType": "struct Structs.VaultEntireData",
                "name": "vaultData_",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

def test_connection():
    """测试RPC连接"""
    print("=" * 50)
    print("测试1: RPC连接")
    print("=" * 50)
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if w3.is_connected():
            print(f"✅ RPC连接成功!")
            print(f"   当前区块: {w3.eth.block_number}")
            print(f"   链ID: {w3.eth.chain_id}")
            return w3
        else:
            print("❌ RPC连接失败")
            return None
    except Exception as e:
        print(f"❌ RPC连接错误: {e}")
        return None

def test_position_by_id(w3, nft_id=9540):
    """测试通过NFT ID获取position"""
    print("\n" + "=" * 50)
    print(f"测试2: 获取Position #{nft_id}")
    print("=" * 50)
    
    try:
        resolver = w3.eth.contract(
            address=w3.to_checksum_address(VAULT_RESOLVER_ADDRESS),
            abi=VAULT_RESOLVER_ABI
        )
        
        position, vault_data = resolver.functions.positionByNftId(nft_id).call()
        
        print(f"✅ 成功获取Position数据!")
        print(f"\n📊 Position信息:")
        print(f"   NFT ID: {position[0]}")
        print(f"   Owner: {position[1]}")
        print(f"   Is Liquidated: {position[2]}")
        print(f"   Supply (raw): {position[9]}")
        print(f"   Borrow (raw): {position[10]}")
        
        print(f"\n🏦 Vault信息:")
        print(f"   Vault地址: {vault_data[0]}")
        print(f"   Is Smart Col: {vault_data[1]}")
        print(f"   Is Smart Debt: {vault_data[2]}")
        
        # constantVariables
        constant_vars = vault_data[3]
        print(f"   Supply Token: {constant_vars[0]}")
        print(f"   Borrow Token: {constant_vars[1]}")
        
        # configs
        configs = vault_data[4]
        print(f"\n⚙️ Configs:")
        print(f"   Collateral Factor: {configs[2] / 100}%")
        print(f"   Liquidation Threshold: {configs[3] / 100}%")
        print(f"   Oracle Price Operate: {configs[9]}")
        print(f"   Oracle Price Liquidate: {configs[10]}")
        
        return position, vault_data
        
    except Exception as e:
        print(f"❌ 获取Position失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def get_token_info(w3, token_address):
    """获取token信息"""
    try:
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

def calculate_health_factor(position, vault_data, w3):
    """计算健康因子"""
    print("\n" + "=" * 50)
    print("测试3: 计算健康因子")
    print("=" * 50)
    
    try:
        supply_raw = position[9]
        borrow_raw = position[10]
        
        constant_vars = vault_data[3]
        configs = vault_data[4]
        
        supply_token = constant_vars[0]
        borrow_token = constant_vars[1]
        
        # 获取token信息
        supply_symbol, supply_decimals = get_token_info(w3, supply_token)
        borrow_symbol, borrow_decimals = get_token_info(w3, borrow_token)
        
        print(f"\n📈 Token信息:")
        print(f"   Supply Token: {supply_symbol} (decimals: {supply_decimals})")
        print(f"   Borrow Token: {borrow_symbol} (decimals: {borrow_decimals})")
        
        # 计算实际数量
        supply_amount = supply_raw / (10 ** supply_decimals)
        borrow_amount = borrow_raw / (10 ** borrow_decimals)
        
        print(f"\n💰 数量:")
        print(f"   Supply: {supply_amount:.6f} {supply_symbol}")
        print(f"   Borrow: {borrow_amount:.6f} {borrow_symbol}")
        
        # Oracle价格 (1e27精度)
        oracle_price = configs[9]  # oraclePriceOperate
        liquidation_threshold = configs[3]  # 1e2精度
        
        print(f"\n📊 价格和阈值:")
        print(f"   Oracle Price: {oracle_price} (raw)")
        print(f"   Oracle Price (normalized): {oracle_price / 1e27}")
        print(f"   Liquidation Threshold: {liquidation_threshold / 100}%")
        
        # 计算USD价值
        # 对于稳定币对，oracle价格表示 supply_token / borrow_token 的比率
        supply_usd = supply_amount * (oracle_price / 1e27)
        borrow_usd = borrow_amount  # 假设borrow token是USD稳定币
        
        print(f"\n💵 USD价值 (估算):")
        print(f"   Supply USD: ${supply_usd:.2f}")
        print(f"   Borrow USD: ${borrow_usd:.2f}")
        
        # 计算抵押率 (Ratio)
        if supply_usd > 0:
            ratio = (borrow_usd / supply_usd) * 100
            print(f"\n📊 抵押率: {ratio:.2f}%")
        
        # 计算健康因子
        # Health Factor = (supply * oracle_price * liquidation_threshold) / (borrow * 1e27 * 10000)
        if borrow_raw > 0:
            # 调整decimals差异
            decimal_adjustment = 10 ** (supply_decimals - borrow_decimals) if supply_decimals != borrow_decimals else 1
            
            health_factor = (supply_raw * oracle_price * liquidation_threshold) / (borrow_raw * 1e27 * 10000 * decimal_adjustment)
            print(f"\n🛡️ 健康因子: {health_factor:.6f}")
        else:
            print(f"\n🛡️ 健康因子: ∞ (无借款)")
            health_factor = float('inf')
        
        return {
            "nft_id": position[0],
            "owner": position[1],
            "supply_token": supply_symbol,
            "supply_amount": supply_amount,
            "supply_usd": supply_usd,
            "borrow_token": borrow_symbol,
            "borrow_amount": borrow_amount,
            "borrow_usd": borrow_usd,
            "health_factor": health_factor,
            "is_liquidated": position[2]
        }
        
    except Exception as e:
        print(f"❌ 计算健康因子失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_user_positions(w3, user_address="0x1247739ac8e238D21574D18dEAce064675546cfC"):
    """测试获取用户所有positions"""
    print("\n" + "=" * 50)
    print(f"测试4: 获取用户 {user_address[:10]}... 的所有Positions")
    print("=" * 50)
    
    try:
        resolver = w3.eth.contract(
            address=w3.to_checksum_address(VAULT_RESOLVER_ADDRESS),
            abi=VAULT_RESOLVER_ABI
        )
        
        positions, vaults_data = resolver.functions.positionsByUser(
            w3.to_checksum_address(user_address)
        ).call()
        
        print(f"✅ 找到 {len(positions)} 个positions")
        
        for i, (pos, vault) in enumerate(zip(positions, vaults_data)):
            print(f"\n--- Position {i+1} ---")
            print(f"   NFT ID: {pos[0]}")
            print(f"   Supply (raw): {pos[9]}")
            print(f"   Borrow (raw): {pos[10]}")
            
        return positions, vaults_data
        
    except Exception as e:
        print(f"❌ 获取用户positions失败: {e}")
        import traceback
        traceback.print_exc()
        return [], []

if __name__ == "__main__":
    print("🚀 Fluid Protocol RPC测试")
    print("=" * 50)
    
    # 测试1: RPC连接
    w3 = test_connection()
    if not w3:
        exit(1)
    
    # 测试2: 获取Position #9540 (从网站上看到的示例)
    position, vault_data = test_position_by_id(w3, 9540)
    
    # 测试3: 计算健康因子
    if position and vault_data:
        result = calculate_health_factor(position, vault_data, w3)
        if result:
            print("\n" + "=" * 50)
            print("📋 最终结果汇总")
            print("=" * 50)
            print(f"Position ID: {result['nft_id']}")
            print(f"Owner: {result['owner']}")
            print(f"Collateral: {result['supply_amount']:.4f} {result['supply_token']} (${result['supply_usd']:.2f})")
            print(f"Debt: {result['borrow_amount']:.4f} {result['borrow_token']} (${result['borrow_usd']:.2f})")
            print(f"Health Factor: {result['health_factor']:.6f}")
    
    # 测试4: 获取用户positions
    test_user_positions(w3)
    
    print("\n✅ 测试完成!")
