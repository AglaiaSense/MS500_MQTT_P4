#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MS500 MQTT 服务器端主程序
集成 MQTT 和 Socket 服务
"""

import sys
import time
import signal
import logging
import json
from config import *
from mqtt_service import MQTTService
from mqtt_pub import MQTTPublisher
from socket_service import SocketService

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def handle_online_message(topic, payload):
    """处理设备在线消息"""
    try:
        # 解析 JSON 数据
        data = json.loads(payload)

        # 提取设备信息
        device_id = data.get('device_id', 'unknown')
        msg_type = data.get('msg_type', 'unknown')
        timestamp = data.get('timestamp', 'unknown')

        logger.info("=" * 60)
        logger.info(f"📱 收到设备在线消息")
        logger.info(f"  主题: {topic}")
        logger.info(f"  设备ID: {device_id}")
        logger.info(f"  时间戳: {timestamp}")

        # 显示网络信息
        ip = data.get('ip', 'N/A')
        network = data.get('network', 'N/A')
        logger.info(f"  IP地址: {ip}")
        logger.info(f"  网络类型: {network}")

        # 显示连接状态
        eth_connected = data.get('eth_connected', False)
        wifi_connected = data.get('wifi_connected', False)
        lte_connected = data.get('lte_connected', False)
        logger.info(f"  以太网: {'✓' if eth_connected else '✗'}")
        logger.info(f"  WiFi: {'✓' if wifi_connected else '✗'}")
        logger.info(f"  LTE: {'✓' if lte_connected else '✗'}")

        # 显示温度和帧率信息
        cpu_temp = data.get('cpu_temp', 0)
        sense_temp = data.get('sense_temp', 0)
        video_fps = data.get('video_fps', 0)
        spi_fps = data.get('spi_fps', 0)

        if cpu_temp > 0:
            logger.info(f"  CPU温度: {cpu_temp}°C")
        if sense_temp > 0:
            logger.info(f"  Sense温度: {sense_temp}°C")
        if video_fps > 0:
            logger.info(f"  视频帧率: {video_fps} FPS")
        if spi_fps > 0:
            logger.info(f"  SPI帧率: {spi_fps} FPS")

        # 显示LTE信号强度（如果有）
        lte_signal = data.get('lte_signal')
        if lte_signal:
            logger.info(f"  LTE信号: {lte_signal}")

        logger.info("=" * 60)

    except json.JSONDecodeError as e:
        logger.error(f"✗ 解析在线消息JSON失败: {e}")
    except Exception as e:
        logger.error(f"✗ 处理在线消息时出错: {e}")


class MS500Server:
    """MS500 服务器主类"""

    def __init__(self):
        """初始化服务器"""
        self.mqtt_service = None
        self.mqtt_publisher = None
        self.socket_service = None
        self.running = False

    def start(self):
        """启动服务器"""
        logger.info("=" * 60)
        logger.info("MS500 MQTT 中转服务启动中...")
        logger.info("  Backend <-> Socket(6080) <-> MQTT <-> ESP32")
        logger.info("  (支持双向通信)")
        logger.info("=" * 60)

        # 1. 创建MQTT服务
        logger.info("\n[1/3] 初始化 MQTT 服务...")
        self.mqtt_service = MQTTService()

        # 设置MQTT消息回调（处理设备在线消息）
        # self.mqtt_service.set_message_callback(handle_online_message)

        # 2. 创建MQTT发布器
        logger.info("[2/3] 初始化 MQTT 发布器...")
        self.mqtt_publisher = MQTTPublisher(self.mqtt_service)

        # 3. 创建Socket服务（接收 Backend 命令）
        logger.info("[3/3] 初始化 Socket 服务...")
        self.socket_service = SocketService(self.mqtt_publisher)

        # 4. 设置 Socket 回复回调 (MQTT回复 -> Socket)
        self.mqtt_service.set_socket_reply_callback(self.socket_service.send_socket_reply)
        logger.info("✓ Socket 回复回调已设置")

        # 启动MQTT服务
        if not self.mqtt_service.start():
            logger.error("MQTT 服务启动失败")
            return False

        # 等待MQTT连接
        logger.info("等待 MQTT 连接...")
        for i in range(10):
            if self.mqtt_service.is_connected():
                break
            time.sleep(0.5)

        if not self.mqtt_service.is_connected():
            logger.error("MQTT 连接超时")
            return False

        # 启动Socket服务
        if not self.socket_service.start():
            logger.error("Socket 服务启动失败")
            self.mqtt_service.stop()
            return False

        self.running = True

        logger.info("\n" + "=" * 60)
        logger.info("✓ 服务器启动成功！")
        logger.info("=" * 60)
        logger.info(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        logger.info(f"Socket 服务: {SOCKET_HOST}:{SOCKET_PORT}")
        logger.info("=" * 60)
        logger.info("\n等待客户端连接和设备消息...")
        logger.info("按 Ctrl+C 停止服务器\n")

        return True

    def stop(self):
        """停止服务器"""
        if not self.running:
            return

        logger.info("\n正在停止服务器...")

        # 停止Socket服务
        if self.socket_service:
            self.socket_service.stop()

        # 停止MQTT服务
        if self.mqtt_service:
            self.mqtt_service.stop()

        self.running = False
        logger.info("服务器已停止")

    def run(self):
        """运行服务器（阻塞）"""
        if not self.start():
            return False

        try:
            # 主循环
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n收到停止信号...")

        finally:
            self.stop()

        return True


def signal_handler(sig, frame):
    """信号处理函数"""
    logger.info("\n收到中断信号，正在退出...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 创建并运行服务器
    server = MS500Server()

    try:
        success = server.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"服务器运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
