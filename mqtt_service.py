#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT 服务管理
负责 MQTT 连接、断线重连、状态管理
"""

import paho.mqtt.client as mqtt
import logging
import time
from datetime import datetime
from config import *

logger = logging.getLogger(__name__)


class MQTTService:
    """MQTT 服务管理类"""

    def __init__(self):
        """初始化 MQTT 服务"""
        self.client = None
        self.connected = False
        self.message_callback = None
        self.connect_callback = None
        self.socket_reply_callback = None  # Socket回复消息的回调

        # 创建 MQTT 客户端
        client_id = f"{MQTT_CLIENT_ID_PREFIX}_{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)

        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        logger.info(f"MQTT 客户端已创建: {client_id}")

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 连接回调"""
        if rc == 0:
            self.connected = True
            logger.info(f"✓ 成功连接到 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")

            # 订阅 ESP32 回复主题 (通配符订阅所有设备的回复)
            reply_topic = "/device/ms500/+/socket_reply"
            self.client.subscribe(reply_topic)
            logger.info(f"✓ 已订阅 Socket 回复主题: {reply_topic}")

            # 调用外部连接回调
            if self.connect_callback:
                self.connect_callback()

        else:
            self.connected = False
            logger.error(f"✗ MQTT 连接失败，错误码: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT 断开连接回调"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ MQTT 意外断开连接，错误码: {rc}")
            logger.info("尝试重新连接...")

    def _on_message(self, client, userdata, msg):
        """MQTT 消息回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            # 判断是否是 Socket 回复消息
            if "/socket_reply" in topic:
                # 处理 Socket 回复消息
                logger.info(f"📬 收到 ESP32 Socket 回复:")
                logger.info(f"   主题: {topic}")
                logger.debug(f"   数据: {payload[:200]}...")

                # 从主题中提取 unit_sn
                # topic格式: /device/ms500/{unit}/socket_reply
                parts = topic.split('/')
                if len(parts) >= 4:
                    unit = parts[3]  # 提取 unit_sn

                    # 调用 Socket 回复回调
                    if self.socket_reply_callback:
                        self.socket_reply_callback(unit, payload)
                    else:
                        logger.warning("Socket回复回调未设置，无法转发回复")
                else:
                    logger.error(f"无法从主题中提取 unit_sn: {topic}")

            else:
                # 其他类型的消息，调用通用回调
                if self.message_callback:
                    self.message_callback(topic, payload)

        except Exception as e:
            logger.error(f"处理 MQTT 消息时出错: {e}")

    def set_message_callback(self, callback):
        """设置消息处理回调函数"""
        self.message_callback = callback

    def set_connect_callback(self, callback):
        """设置连接成功回调函数"""
        self.connect_callback = callback

    def set_socket_reply_callback(self, callback):
        """
        设置 Socket 回复消息的回调函数

        Args:
            callback: 回调函数，接收 (unit, payload) 两个参数
        """
        self.socket_reply_callback = callback

    def connect(self):
        """连接到 MQTT Broker"""
        try:
            logger.info(f"正在连接到 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}...")
            self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            return True
        except Exception as e:
            logger.error(f"连接 MQTT Broker 失败: {e}")
            return False

    def start(self):
        """启动 MQTT 服务（非阻塞）"""
        if self.connect():
            self.client.loop_start()
            logger.info("MQTT 服务已启动")
            return True
        return False

    def stop(self):
        """停止 MQTT 服务"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("MQTT 服务已停止")

    def publish(self, topic, payload):
        """发布消息到 MQTT"""
        if not self.connected:
            logger.error("MQTT 未连接，无法发布消息")
            return False

        try:
            result = self.client.publish(topic, payload)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"消息已发布到主题: {topic}")
                return True
            else:
                logger.error(f"发布消息失败，错误码: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"发布消息时出错: {e}")
            return False

    def is_connected(self):
        """检查 MQTT 连接状态"""
        return self.connected
