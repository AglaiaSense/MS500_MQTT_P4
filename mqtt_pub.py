#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT 消息发布
负责转发 Backend Socket 命令到 MQTT
"""

import json
import logging

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """MQTT 消息发布类 - 专门用于转发 Socket 命令"""

    def __init__(self, mqtt_service):
        """
        初始化发布器

        Args:
            mqtt_service: MQTTService 实例
        """
        self.mqtt_service = mqtt_service

    def forward_socket_command(self, json_data):
        """
        转发 Backend 的 Socket 命令到设备

        Args:
            json_data: Backend 发送的 JSON 数据（dict）

        Returns:
            bool: 发送成功返回True
        """
        # 提取 unit 字段（设备单元标识）
        unit = json_data.get('unit')
        if not unit:
            logger.error("Socket命令缺少 'unit' 字段")
            return False

        # 拼装 topic: /service/ms500/{unit}/socket
        topic = f"/service/ms500/{unit}/socket"
        print(topic)

        # 转换为JSON字符串
        try:
            json_payload = json.dumps(json_data, ensure_ascii=False)
        except Exception as e:
            logger.error(f"构建JSON失败: {e}")
            return False

        # 发布消息
        success = self.mqtt_service.publish(topic, json_payload)

        if success:
            logger.info(f"✓ Socket命令已转发到 MQTT")
            logger.info(f"  主题: {topic}")
            logger.info(f"  类型: {json_data.get('type', 'UNKNOWN')}")
            logger.info(f"  设备: {unit}")
        else:
            logger.error(f"✗ Socket命令转发失败")

        return success
