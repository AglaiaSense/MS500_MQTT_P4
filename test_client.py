#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端 - 模拟 Backend 服务器发送 Socket 命令
用于测试 python_mqtt 中转服务和 ESP32 设备的 Socket 命令处理
"""

import socket
import json
import time
import sys

# ==================== 测试配置 ====================
# 测试服务器配置
SERVER_HOST = "localhost"  # 本地测试使用 localhost，远程测试使用实际 IP
SERVER_PORT = 6080  # Socket 服务器端口

# 默认测试参数
TEST_CAMERA_ID = "2622"  # 默认相机ID
TEST_UNIT_ID = "MS500-H120-EP-zlcu-0059"  # 默认设备单元标识

# 是否显示详细的 JSON 数据（调试用）
VERBOSE_JSON = True

# 测试命令默认参数配置
TEST_COMMANDS_CONFIG = {
    "AIM": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "model_id": 5,
        "link": "/media/Organization1/AIModel/yolov8n.rpk",
        "md5": "5d41402abc4b2a76b9719d911017c592"
    },
    "FMW": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "firmware_id": 3,
        "link": "/media/Organization1/Firmware/v2.1.0.img",
        "md5": "d8e8fca2dc0f896fd7cb4cb0031ba249"
    },
    "APP": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "application_id": 8,
        "link": "/media/Organization1/Application/app_v1.2.3.tar.gz",
        "md5": "098f6bcd4621d373cade4e832627b4f6"
    },
    "CDN": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "coordinates": {
            "roi1": [[100, 100], [200, 100], [200, 200], [100, 200]],
            "roi2": [[300, 150], [400, 150], [400, 250], [300, 250]]
        }
    },
    "CFG": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "configs": [
            {"name": "brightness", "value": "80"},
            {"name": "contrast", "value": "60"},
            {"name": "detection_threshold", "value": "0.6"}
        ]
    },
    "CTS": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "cs_picEnable": True,
        "cs_vidEnable": False,
        "cs_picMode": 0,
        "cs_picQuality": 95,
        "cs_vidFps": 30
    },
    "WFI": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "wifi_enabled": True,
        "wifi_password": "new_secure_password_123"
    },
    "SCS": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID
    },
    "UDS": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "settings": {
            "brightness": 90,
            "exposure": "manual",
            "exposure_value": 1000
        }
    },
    "FRS": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID,
        "reset_level": "full"
    },
    "IMG": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID
    },
    "RSR": {
        "camera": TEST_CAMERA_ID,
        "unit": TEST_UNIT_ID
    }
}


def send_socket_command(host, port, command_data):
    """
    发送 Socket 命令到 python_mqtt 中转服务

    Args:
        host: 服务器地址
        port: 服务器端口
        command_data: 命令数据（dict）

    Returns:
        bool: 发送成功返回True
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((host, port))

            # 发送 JSON 数据
            json_str = json.dumps(command_data, ensure_ascii=False)
            s.sendall(json_str.encode('utf-8'))

            print(f"✓ 命令发送成功: {command_data.get('type', 'UNKNOWN')}")

            # 如果启用详细模式，打印完整 JSON
            if VERBOSE_JSON:
                print(f"  JSON: {json_str}")

            return True

    except ConnectionRefusedError:
        print(f"✗ 连接被拒绝: {host}:{port}")
        print("  请确保 python_mqtt 中转服务已启动 (python main.py)")
        return False
    except Exception as e:
        print(f"✗ 发送失败: {e}")
        return False


def test_aim_command():
    """测试 AIM - AI Model Update 命令"""
    print("\n1️⃣ 测试 AIM (AI Model Update)")
    command = {"type": "AIM", **TEST_COMMANDS_CONFIG["AIM"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_fmw_command():
    """测试 FMW - Firmware Update 命令"""
    print("\n2️⃣ 测试 FMW (Firmware Update)")
    command = {"type": "FMW", **TEST_COMMANDS_CONFIG["FMW"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_app_command():
    """测试 APP - Application Update 命令"""
    print("\n3️⃣ 测试 APP (Application Update)")
    command = {"type": "APP", **TEST_COMMANDS_CONFIG["APP"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_cdn_command():
    """测试 CDN - Coordinates Update 命令"""
    print("\n4️⃣ 测试 CDN (Coordinates Update)")
    command = {"type": "CDN", **TEST_COMMANDS_CONFIG["CDN"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_cfg_command():
    """测试 CFG - Configuration Update 命令"""
    print("\n5️⃣ 测试 CFG (Configuration Update)")
    command = {"type": "CFG", **TEST_COMMANDS_CONFIG["CFG"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_cts_command():
    """测试 CTS - Capture Settings Update 命令"""
    print("\n6️⃣ 测试 CTS (Capture Settings Update)")
    command = {"type": "CTS", **TEST_COMMANDS_CONFIG["CTS"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_wfi_command():
    """测试 WFI - WiFi Settings Update 命令"""
    print("\n7️⃣ 测试 WFI (WiFi Settings Update)")
    command = {"type": "WFI", **TEST_COMMANDS_CONFIG["WFI"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_scs_command():
    """测试 SCS - Send Current Settings 命令"""
    print("\n8️⃣ 测试 SCS (Send Current Settings)")
    command = {"type": "SCS", **TEST_COMMANDS_CONFIG["SCS"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_uds_command():
    """测试 UDS - Update Device Settings 命令"""
    print("\n9️⃣ 测试 UDS (Update Device Settings)")
    command = {"type": "UDS", **TEST_COMMANDS_CONFIG["UDS"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_frs_command():
    """测试 FRS - Factory Reset 命令"""
    print("\n🔟 测试 FRS (Factory Reset)")
    command = {"type": "FRS", **TEST_COMMANDS_CONFIG["FRS"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_img_command():
    """测试 IMG - Image Request 命令"""
    print("\n1️⃣1️⃣ 测试 IMG (Image Request)")
    command = {"type": "IMG", **TEST_COMMANDS_CONFIG["IMG"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def test_rsr_command():
    """测试 RSR - Resend Request 命令"""
    print("\n1️⃣2️⃣ 测试 RSR (Resend Request)")
    command = {"type": "RSR", **TEST_COMMANDS_CONFIG["RSR"]}
    return send_socket_command(SERVER_HOST, SERVER_PORT, command)


def interactive_mode():
    """交互模式 - 选择要测试的命令"""
    print("=" * 60)
    print("MS500 Socket 命令测试工具")
    print("模拟 Backend 服务器发送命令到 python_mqtt 中转服务")
    print("=" * 60)
    print(f"目标服务器: {SERVER_HOST}:{SERVER_PORT}")
    print(f"默认 Camera ID: {TEST_COMMANDS_CONFIG['AIM']['camera']}")
    print(f"详细模式: {'开启' if VERBOSE_JSON else '关闭'}")
    print("=" * 60)
    print("\n提示: 可在 config.py 中修改默认配置")

    commands = {
        '1': ('AIM - AI Model Update', test_aim_command),
        '2': ('FMW - Firmware Update', test_fmw_command),
        '3': ('APP - Application Update', test_app_command),
        '4': ('CDN - Coordinates Update', test_cdn_command),
        '5': ('CFG - Configuration Update', test_cfg_command),
        '6': ('CTS - Capture Settings Update', test_cts_command),
        '7': ('WFI - WiFi Settings Update', test_wfi_command),
        '8': ('SCS - Send Current Settings', test_scs_command),
        '9': ('UDS - Update Device Settings', test_uds_command),
        '10': ('FRS - Factory Reset', test_frs_command),
        '11': ('IMG - Image Request', test_img_command),
        '12': ('RSR - Resend Request', test_rsr_command),
        'all': ('测试所有命令', None),
        'q': ('退出', None)
    }

    while True:
        print("\n" + "=" * 60)
        print("可用命令:")
        print("=" * 60)
        for key, (desc, _) in commands.items():
            print(f"  {key:4s} - {desc}")
        print("=" * 60)

        choice = input("\n请选择命令 (输入编号): ").strip()

        if choice == 'q':
            print("退出测试工具")
            break

        if choice == 'all':
            print("\n开始测试所有命令...")
            for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
                _, test_func = commands[key]
                if test_func:
                    test_func()
                    time.sleep(1)
            print("\n✓ 所有命令测试完成!")
            continue

        if choice in commands:
            _, test_func = commands[choice]
            if test_func:
                test_func()
        else:
            print(f"✗ 无效的选择: {choice}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1].upper()

        commands = {
            'AIM': test_aim_command,
            'FMW': test_fmw_command,
            'APP': test_app_command,
            'CDN': test_cdn_command,
            'CFG': test_cfg_command,
            'CTS': test_cts_command,
            'WFI': test_wfi_command,
            'SCS': test_scs_command,
            'UDS': test_uds_command,
            'FRS': test_frs_command,
            'IMG': test_img_command,
            'RSR': test_rsr_command,
            'ALL': None
        }

        if command == 'ALL':
            for test_func in commands.values():
                if test_func:
                    test_func()
                    time.sleep(1)
        elif command in commands:
            commands[command]()
        else:
            print(f"未知命令: {command}")
            print("可用命令: AIM, FMW, APP, CDN, CFG, CTS, WFI, SCS, UDS, FRS, IMG, RSR, ALL")
    else:
        # 交互模式
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\n退出测试工具")


if __name__ == "__main__":
    main()
