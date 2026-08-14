import json
import os
import random
import time
from datetime import datetime


def random_normal_distribution_int(a, b, n=15):
    """
    在区间 [a, b) 内生成近似正态分布的随机整数。
    通过取 n 个均匀分布随机数的平均值实现中心极限定理。
    :param a: 最小值（包含）
    :param b: 最大值（不包含）
    :param n: 采样数量（值越大分布越集中）
    :return: 符合近似正态分布的整数
    """
    if a >= b:
        return b
    # 生成 n 个均匀分布的随机数并计算均值
    samples = [random.randint(a, b - 1) for _ in range(n)]
    mean = sum(samples) / n
    # 四舍五入返回整数
    return round(mean)


def format_length(length: str) -> str:
    """格式化长度输出"""
    try:
        length = int(length)
    except Exception as e:
        print(f"转换长度出错：{e}")
        return length
        
    if length < 100:
        # 100cm 以下显示厘米
        return f"{length}cm"
    elif length < 100000:
        # 100cm 到 99999cm 显示米 (除以100)
        # 例如 1000cm = 10.0m
        return f"{round(length / 100, 2)}m"
    else:
        # 100000cm 及以上显示千米 (除以100,000)
        # 例如 150000cm = 1.5km
        return f"{round(length / 100000, 2)}km"


def is_super_user(user_id: str) -> bool:
    """检查是否为超级用户"""
    try:
        from astrbot.core.utils.astrbot_path import get_astrbot_data_path

        config_path = os.path.join(get_astrbot_data_path(), "cmd_config.json")
    except Exception:
        config_path = "data/cmd_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if str(user_id) in {str(a) for a in config.get("admins_id", [])}:
            return True
        else:
            return False
    except Exception as e:
        print(f"获取cmd_config.json出错：{e}")
        return False


def probabilistic_decision(probability: float) -> bool:
    """
    根据传入的概率返回 True 或 False。
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("概率必须在 0.0 到 1.0 之间")
    return random.random() <= probability


def is_timestamp_today(timestamp: float) -> bool:
    """判断时间戳是否属于今天（本地时区）"""
    try:
        # 转换为本地时区日期
        dt = datetime.fromtimestamp(timestamp)
        today = datetime.now()
        # 比较年月日是否相同
        return (dt.year, dt.month, dt.day) == (today.year, today.month, today.day)
    except (TypeError, OverflowError, OSError):
        return False


def check_cooldown(start_timestamp: float, cd: float) -> tuple[bool, str]:
    """检查冷却时间是否结束"""
    current_time = time.time()
    elapsed = current_time - start_timestamp
    remaining = cd - elapsed

    if remaining <= 0:
        return True, "0秒"

    remaining_int = int(remaining)
    if remaining < 60:
        text = f"{remaining_int}秒"
    elif remaining < 3600:
        mins, secs = divmod(remaining_int, 60)
        text = f"{mins:02d}分{secs:02d}秒"
    else:
        hours, remainder = divmod(remaining_int, 3600)
        mins, secs = divmod(remainder, 60)
        text = f"{hours}小时{mins:02d}分{secs:02d}秒"

    return False, text


def get_add_text(true_add, original_add, user_data) -> str:
    text = ''
    if true_add < original_add:
        # 修复逻辑：窃取的长度是 原始增加量 - 实际增加量
        stolen = original_add - true_add
        text += f"📏 {user_data['niuniu_name']}的长度在被寄生虫蚕食后增加了{true_add}cm，当前长度：{format_length(user_data['length'])}\n"
        text += f'🐛 各寄生虫窃取到了{stolen}cm，回馈到主人的牛牛中\n'
    else:
        text += f"📏 {user_data['niuniu_name']}的长度增加{true_add}cm，当前长度：{format_length(user_data['length'])}\n"
    return text


def timestamp_to_hhmm(timestamp):
    """将时间戳转换为hh:mm格式的字符串"""
    time_tuple = time.localtime(timestamp)
    return time.strftime("%H:%M", time_tuple)