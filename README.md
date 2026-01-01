# Fluid Position Monitor Bot - 部署包

## 快速部署

### 1. 环境变量
```bash
BOT_TOKEN=8560001067:AAGN272A94m9_xCN-SLS-j_WP9mQJ4MkP6w
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行
```bash
python bot.py
```

## Render 部署

1. 上传到 GitHub
2. 在 Render 连接仓库
3. 设置环境变量 `BOT_TOKEN`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python bot.py`

## 功能

- Position 查询
- 钱包地址查询
- 多链支持 (ETH/Base/Arbitrum/Polygon/Plasma)
- 自动监控 (每30分钟)
- Telegram 提醒
- 速率限制 (10次/天)

## 命令

- `/start` - 开始
- `/monitor <address>` - 监控地址
- `/mymonitors` - 查看监控列表
- `/unmonitor <address>` - 停止监控
- `/stats` - 查看统计

## 测试

发送 `9540` 查询 Position #9540
