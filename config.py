#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含 MQTT 和 Socket 的配置参数
"""

# ==================== MQTT 配置 ====================

# MQTT Broker 地址
MQTT_BROKER = "mqtt.leopardaws.com"

# MQTT 端口
MQTT_PORT = 1883

# MQTT 保活时间（秒）
MQTT_KEEPALIVE = 60

# MQTT 客户端ID前缀
MQTT_CLIENT_ID_PREFIX = "ms500_server"

# MQTT 订阅主题列表
SUBSCRIBE_TOPICS = [
    "/device/ms500/+/online",   # 订阅所有设备的在线心跳消息
]

# ==================== Socket 配置 ====================

# Socket 服务器地址（接收 Backend 服务器的连接）
SOCKET_HOST = "127.0.0.1"  # 只监听本地回环地址，仅接受本地连接

# Socket 服务器端口（与 Backend 的 DEFAULT_SOCKET_PORT 保持一致）
SOCKET_PORT = 6080

# Socket 缓冲区大小
SOCKET_BUFFER_SIZE = 65536  # 64KB，用于接收大的 JSON 数据

# ==================== 日志配置 ====================

# 日志级别
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
