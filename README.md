# NGL Link CLI

通过命令行发送匿名消息到 ngl.link 的工具。

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或者直接运行
python3 ngl-cli.py <command>
```

## 使用方法

### 发送单条消息

```bash
python3 ngl-cli.py send <username> <message>
```

**示例：**
```bash
python3 ngl-cli.py send username Hi
python3 ngl-cli.py send username "Hello from CLI!"
```

### 发送多条消息（刷屏）

```bash
python3 ngl-cli.py spam <username> <message> <count> [options]
```

**示例：**
```bash
# 发送 10 条消息，每条间隔 1 秒
python3 ngl-cli.py spam username Hi 10 --delay 1

# 发送 100 条消息，使用 5 个并发线程
python3 ngl-cli.py spam username Hi 100 --threads 5

# 发送 50 条消息，每条使用随机设备 ID
python3 ngl-cli.py spam username Hi 50 --random-device

# 综合使用
python3 ngl-cli.py spam username Hi 100 --delay 0.5 --threads 3 --random-device
```

## 命令行参数

### send 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `username` | 是 | NGL 用户名（不含 @） |
| `message` | 是 | 要发送的消息内容（可用空格，如 `Hi` 或 `"Hello world"`） |
| `--device-id` | 否 | 指定设备 ID |

### spam 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `username` | 是 | NGL 用户名（不含 @） |
| `message` | 是 | 要发送的消息内容（可用空格，如 `Hi`） |
| `count` | 是 | 发送消息数量 |
| `--delay` | 否 | 每条消息间隔秒数（默认 0） |
| `--threads` | 否 | 并发线程数（默认 1） |
| `--random-device` | 否 | 每条消息使用随机设备 ID |

## API 分析

通过逆向 ngl.link 的 `main.js` 发现的实际接口：

- **端点**: `POST https://ngl.link/api/submit`
- **参数**:
  - `username` - 目标用户名
  - `question` - 消息内容
  - `deviceId` - 设备标识
  - `gameSlug` - 游戏标识（可选）
  - `referrer` - 来源（可选）
  - `push_ref` - 推送引用（可选）

## 注意事项

- 请负责任地使用，不要用于骚扰他人
- 大量发送消息可能导致 IP 被封禁
- 建议使用 `--delay` 参数控制发送频率
- 使用 `--random-device` 可以避免同一设备被限制

## 完整示例

```bash
# 基本发送
python3 ngl-cli.py send username Hi

# 带空格的消息用引号
python3 ngl-cli.py send username "Hello World"

# 查看帮助
python3 ngl-cli.py --help
python3 ngl-cli.py send --help
python3 ngl-cli.py spam --help

# 批量发送（带延迟和随机设备）
python3 ngl-cli.py spam username Hi 20 --delay 2 --random-device
```
