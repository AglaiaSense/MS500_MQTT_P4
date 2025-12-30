#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Socket 服务器
专门接收 Backend 服务器发送的 Socket 命令，并通过 MQTT 转发到设备
"""

import socket
import threading
import json
import logging
from config import *

logger = logging.getLogger(__name__)


class SocketService:
    """Socket 服务器类 - 专门处理 Backend 的 Socket 命令"""

    def __init__(self, mqtt_publisher):
        """
        初始化Socket服务器

        Args:
            mqtt_publisher: MQTTPublisher实例
        """
        self.mqtt_publisher = mqtt_publisher
        self.server_socket = None
        self.running = False

        # unit_sn → socket连接 映射表 (内存存储)
        self.unit_socket_map = {}
        # 线程锁，保护映射表的并发访问
        self.map_lock = threading.Lock()

    def start(self):
        """启动Socket服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((SOCKET_HOST, SOCKET_PORT))
            self.server_socket.listen(5)
            self.running = True

            logger.info(f"✓ Socket服务器已启动: {SOCKET_HOST}:{SOCKET_PORT}")
            logger.info(f"  等待 Backend 服务器连接...")

            # 启动接受连接的线程
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()

            return True

        except Exception as e:
            logger.error(f"启动Socket服务器失败: {e}")
            return False

    def stop(self):
        """停止Socket服务器"""
        self.running = False

        # 关闭服务器socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        logger.info("Socket服务器已停止")

    def _accept_connections(self):
        """接受客户端连接"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"✓ Backend 服务器连接: {address[0]}:{address[1]}")

                # 启动客户端处理线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()

            except Exception as e:
                if self.running:
                    logger.error(f"接受连接时出错: {e}")

    def _handle_client(self, client_socket, address):
        """
        处理客户端请求
        接收 Backend 发送的 JSON 命令并转发到 MQTT
        """
        current_unit = None  # 当前连接对应的 unit_sn

        try:
            # 设置 Socket 超时 (60秒)
            client_socket.settimeout(60.0)

            while self.running:
                # 接收数据
                try:
                    data = client_socket.recv(SOCKET_BUFFER_SIZE)
                except socket.timeout:
                    logger.warning(f"客户端 {address} 接收超时，继续等待...")
                    continue

                if not data:
                    break

                # 解码JSON数据
                try:
                    json_str = data.decode('utf-8')
                    json_data = json.loads(json_str)

                    logger.info(f"📥 收到 Backend 命令:")
                    logger.info(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)}")

                    # 只为 SCS/UDS 命令保存映射关系（这两个命令需要通过 Socket 回复数据）
                    command_type = json_data.get('type')
                    unit = json_data.get('unit')

                    if command_type in ['SCS', 'UDS'] and unit:
                        with self.map_lock:
                            self.unit_socket_map[unit] = client_socket
                            current_unit = unit
                        logger.info(f"✓ 已保存映射 ({command_type}): unit={unit} → socket={address}")
                    elif command_type in ['SCS', 'UDS'] and not unit:
                        logger.warning(f"⚠️ {command_type} 命令缺少 unit 字段，无法保存映射")
                    else:
                        logger.debug(f"命令类型 {command_type} 不需要 Socket 映射")

                    # 转发到 MQTT
                    success = self.mqtt_publisher.forward_socket_command(json_data)

                    if success:
                        logger.info(f"✓ 命令已转发到 MQTT")
                    else:
                        logger.error(f"✗ 命令转发失败")

                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"原始数据: {data}")
                except UnicodeDecodeError as e:
                    logger.error(f"UTF-8解码失败: {e}")

        except Exception as e:
            logger.error(f"处理客户端 {address} 时出错: {e}")

        finally:
            # 清除映射关系
            if current_unit:
                with self.map_lock:
                    if current_unit in self.unit_socket_map:
                        del self.unit_socket_map[current_unit]
                        logger.info(f"✓ 已移除映射: unit={current_unit}")

            try:
                client_socket.close()
            except:
                pass

            logger.info(f"Backend 断开连接: {address}")

    def send_socket_reply(self, unit, data):
        """
        发送回复数据到 Backend Socket
        通过 unit_sn 查找对应的 Socket 连接并发送数据

        Args:
            unit: 设备单元标识 (unit_sn)
            data: 要发送的数据 (dict 或 str)

        Returns:
            bool: 发送成功返回True
        """
        try:
            # 查找对应的 Socket 连接
            with self.map_lock:
                client_socket = self.unit_socket_map.get(unit)

            if not client_socket:
                logger.error(f"✗ 未找到 unit={unit} 的 Socket 连接，无法发送回复")
                logger.error(f"  当前映射表: {list(self.unit_socket_map.keys())}")
                return False

            # 转换为 JSON 字符串
            if isinstance(data, dict):
                json_str = json.dumps(data, ensure_ascii=False)
            else:
                json_str = data

            # 发送数据
            client_socket.sendall(json_str.encode('utf-8'))

            logger.info(f"✓ 已发送回复到 Backend (unit={unit})")
            logger.debug(f"  回复数据: {json_str[:200]}...")  # 只显示前200字符

            return True

        except Exception as e:
            logger.error(f"✗ 发送回复失败 (unit={unit}): {e}")
            return False
