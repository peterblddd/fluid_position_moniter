#!/usr/bin/env python3
"""
简化测试脚本：验证RPC连接
"""

from web3 import Web3

RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/2-zA_FKx0g4_IltX8wwnu"

print("测试RPC连接...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():
    print(f"✅ RPC连接成功!")
    print(f"   当前区块: {w3.eth.block_number}")
    print(f"   链ID: {w3.eth.chain_id}")
else:
    print("❌ RPC连接失败")
