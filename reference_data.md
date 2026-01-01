# Position #9540 实际数据 (来自 fluid.io)

## 基本信息
- Position ID: 9540
- Owner: 0x1247...6cfC
- Vault: syrupUSDC / GHO

## 配置参数
- Collateral Factor: 90%
- Liquidation Threshold: 92%
- Liquidation Penalty: 2%
- Liquidation Price: 1.067117 GHO

## 当前状态
- Ratio: 85.77%
- Status: Safe

## 抵押品 (Collateral)
- 数量: 3,495.5 syrupUSDC
- USD价值: $4,000
- Net APR: 5.76%

## 债务 (Debt)
- 数量: 3,431.7 GHO
- USD价值: $3,428.74
- Net APR: 3.1%

## 计算验证
- Ratio = Debt USD / Collateral USD = 3428.74 / 4000 = 85.72% (接近85.77%)
- Health Factor = Liquidation Threshold / Ratio = 92% / 85.77% = 1.0726

## 关键发现
1. syrupUSDC 的 USD 价值约为 $1.144/token (4000 / 3495.5 = 1.1443)
2. GHO 的 USD 价值约为 $0.999/token (3428.74 / 3431.7 = 0.9991)
3. Oracle价格反映的是 syrupUSDC 相对于 GHO 的价格比率

## 修复方向
需要正确计算:
1. supply_usd = supply_amount * (oracle_price / 1e27) 但需要正确处理decimals
2. 对于 syrupUSDC (6 decimals) / GHO (18 decimals):
   - oracle_price ≈ 1.1446e27 * 1e12 = 1.1446e39
   - 实际 oracle_price = 1144622748538609333680592482000000000000 ≈ 1.14e39
   - 这说明 oracle_price 已经包含了 decimals 调整 (1e27 * 1e12 = 1e39)
   - 所以 supply_usd = supply_amount * oracle_price / 1e39 (而不是 1e27)
