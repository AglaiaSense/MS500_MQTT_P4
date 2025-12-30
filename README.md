# MS500 MQTT 中转服务

Backend Socket 命令到 ESP32 设备的 MQTT 中转服务

## 📋 系统架构

```
Backend 服务器 (端口 6080)
    ↓ Socket JSON (12种命令类型)
python_mqtt 中转服务 (监听 6080)
    ↓ MQTT (/service/ms500/{unit}/socket)
ESP32 设备 (订阅 socket 主题)
    ↓ 解析 JSON
bsp_mqtt_handle.c (处理命令)

ESP32 设备 (定时发送在线消息)
    ↓ MQTT (/device/ms500/{device_id}/online)
python_mqtt 中转服务 (订阅在线消息)
    ↓ 显示设备状态
```

## 操作步骤：

```
# 进入目录
cd /home/sjx/MQTT

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 功能说明

### 下行通信（Backend → ESP32）
- 接收 Backend 的 Socket 命令（端口 6080）
- 通过 MQTT 转发到 ESP32 设备
- 支持 12 种命令类型：AIM, FMW, APP, CDN, CFG, CTS, WFI, SCS, UDS, FRS, IMG, RSR

### 上行通信（ESP32 → python_mqtt）
- 订阅 `/device/ms500/+/online` 主题
- 接收并显示设备在线心跳消息
- 显示设备状态：IP、网络类型、连接状态、温度、帧率等

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install paho-mqtt
```

### 2. 配置服务 (`config.py`)

修改 MQTT Broker 地址：

```python
# MQTT 配置
MQTT_BROKER = "your_broker_ip"  # 修改为你的 MQTT Broker 地址
MQTT_PORT = 1883

# Socket 配置
SOCKET_PORT = 6080  # Backend 连接端口
```

### 3. 启动中转服务

```bash
python main.py
```

预期输出：

```
============================================================
MS500 MQTT 中转服务启动中...
  Backend -> Socket(6080) -> MQTT -> ESP32
============================================================

[1/3] 初始化 MQTT 服务...
✓ 成功连接到 MQTT Broker: your_broker_ip:1883
✓ 已订阅主题: /device/ms500/+/online

[2/3] 初始化 MQTT 发布器...

[3/3] 初始化 Socket 服务...
✓ Socket服务器已启动: 127.0.0.1:6080

============================================================
✓ 服务器启动成功！
============================================================

等待客户端连接和设备消息...
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `config.py` | ⚙️ 配置文件（MQTT、Socket） |
| `main.py` | 🚀 主程序（启动中转服务） |
| `socket_service.py` | 📡 Socket 服务器（接收 Backend 命令） |
| `mqtt_pub.py` | 📤 MQTT 发布器（转发命令到设备） |
| `mqtt_service.py` | 🔌 MQTT 客户端服务 |

## ⚙️ 配置说明

### MQTT 配置

```python
# MQTT Broker 地址
MQTT_BROKER = "mqtt.leopardaws.com"

# MQTT 端口
MQTT_PORT = 1883

# MQTT 保活时间（秒）
MQTT_KEEPALIVE = 60

# MQTT 订阅主题列表
SUBSCRIBE_TOPICS = [
    "/device/ms500/+/online",   # 订阅所有设备的在线心跳消息
]
```

### Socket 配置

```python
# Socket 服务器地址（接收 Backend 服务器的连接）
SOCKET_HOST = "127.0.0.1"  # 只监听本地回环地址，仅接受本地连接

# Socket 服务器端口（与 Backend 的 DEFAULT_SOCKET_PORT 保持一致）
SOCKET_PORT = 6080

# Socket 缓冲区大小
SOCKET_BUFFER_SIZE = 65536  # 64KB
```


## 📦 支持的命令类型

| 命令代码 | 说明 | 主要字段 |
|---------|------|---------|
| **AIM** | 更新 AI 模型 | model_id, link, md5 |
| **FMW** | 更新固件 | firmware_id, link, md5 |
| **APP** | 更新应用程序 | application_id, link, md5 |
| **CDN** | 更新 ROI 坐标 | coordinates |
| **CFG** | 更新配置参数 | configs |
| **CTS** | 更新采集设置 | cs_picEnable, cs_vidFps, etc. |
| **WFI** | 更新 WiFi 设置 | wifi_enabled, wifi_password |
| **SCS** | 请求设备当前设置 | - |
| **UDS** | 更新设备系统设置 | settings |
| **FRS** | 恢复出厂设置 | reset_level |
| **IMG** | 请求发送图片 | - |
| **RSR** | 重新发送请求 | - |

## 🔍 调试技巧

### 1. 查看中转服务日志

中转服务会打印接收到的命令：

```
📥 收到 Backend 命令:
   {
     "type": "AIM",
     "camera": "30eda0e27100",
     "unit": "MS500-H090-EP-2549-0038",
     "model_id": 5,
     "link": "/media/Organization1/AIModel/yolov8n.rpk",
     "md5": "5d41402abc4b2a76b9719d911017c592"
   }
✓ Socket命令已转发到 MQTT
  主题: /service/ms500/MS500-H090-EP-2549-0038/socket
  类型: AIM
  设备: MS500-H090-EP-2549-0038
```

### 2. 查看 ESP32 输出

ESP32 会打印接收到的命令：

```
I (12345) bsp_mqtt_handle: ========== Socket Command Received ==========
I (12345) bsp_mqtt_handle: Command Type: AIM
I (12345) bsp_mqtt_handle: Full JSON Data:
{
  "type": "AIM",
  "camera": "30eda0e27100",
  "unit": "MS500-H090-EP-2549-0038",
  "model_id": 5,
  ...
}
I (12345) bsp_mqtt_handle: =============================================
```

### 3. 查看设备在线消息

当 ESP32 设备发送在线心跳时，python_mqtt 会打印设备状态：

```
============================================================
📱 收到设备在线消息
  主题: /device/ms500/A0B1C2D3E4F5/online
  设备ID: A0B1C2D3E4F5
  时间戳: 12345
  IP地址: 192.168.1.100
  网络类型: eth
  以太网: ✓
  WiFi: ✗
  LTE: ✗
  CPU温度: 45.5°C
  Sense温度: 42.3°C
  视频帧率: 30.0 FPS
  SPI帧率: 29.8 FPS
============================================================
```

## 🔧 常见问题

### Q: 无法连接到 MQTT Broker

**A:** 检查 `config.py` 中的 `MQTT_BROKER` 地址是否正确，确保网络可达。

### Q: Backend 连接被拒绝

**A:** 确保 `main.py` 中转服务已启动。检查端口 6080 是否被占用：

```bash
# Windows
netstat -an | findstr "6080"

# Linux/Mac
lsof -i :6080
```

### Q: 为什么只监听 127.0.0.1，如何允许远程连接

**A:** 默认配置 `SOCKET_HOST = "127.0.0.1"` 只接受本地连接，这是出于安全考虑。

如果需要接受远程 Backend 连接，修改 `config.py`：

```python
# 允许所有网络接口连接
SOCKET_HOST = "0.0.0.0"

# 或指定具体网卡IP
SOCKET_HOST = "192.168.1.100"
```

⚠️ **注意**：开放远程连接时需要注意网络安全，建议配置防火墙规则。

## 📝 注意事项

1. **端口占用**：确保端口 6080 未被其他程序占用
2. **MQTT 连接**：确保 MQTT Broker 正常运行且网络可达
3. **ESP32 订阅**：确保 ESP32 已订阅 `/service/ms500/{unit}/socket` 主题
4. **JSON 格式**：所有命令必须包含 `type` 和 `unit` 字段
