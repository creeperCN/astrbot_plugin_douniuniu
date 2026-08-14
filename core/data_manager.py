from collections import OrderedDict
import yaml
import json
import os
import time
from typing import Dict, Any
from pathlib import Path

from .exceptions import DataLoadError, DataSaveError
from .utils import random_normal_distribution_int, format_length

try:
    from astrbot.core.utils.astrbot_path import get_astrbot_data_path

    DEFAULT_DATA_FILE = Path(get_astrbot_data_path()) / 'douniuniu_plugin' / 'user.yaml'
except Exception:
    DEFAULT_DATA_FILE = Path('data/douniuniu_plugin/user.yaml')


class DataManager:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path else DEFAULT_DATA_FILE
        self.default_yaml = {
            "groups": {},
            "users": {}
        }
        self._ensure_file_exists()
        self.min_length = 1
        self.max_length = 10
        self.min_hardness = 1
        self.max_hardness = 10

    def _ensure_file_exists(self):
        """确保必要文件存在"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                yaml.dump(self.default_yaml, f)

    def load_all_data(self) -> Dict[str, Any]:
        """加载全部数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or self.default_yaml
        except Exception as e:
            raise DataLoadError(str(self.file_path), str(e))

    def save_all_data(self, data: Dict[str, Any]):
        """保存全部数据"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        except Exception as e:
            raise DataSaveError(str(self.file_path), str(e))

    def get_group_data(self, group_id: str) -> Dict[str, Any]:
        """获取群数据（不存在时初始化）"""
        data = self.load_all_data()
        group_id = str(group_id)

        if group_id not in data["groups"]:
            data["groups"][group_id] = {
                "plugin_enabled": False,
                "manager": ["1097694383"],
                "rank": {}
            }
            self.save_all_data(data)

        return data["groups"][group_id]

    def get_all_group_data(self) -> Dict[str, Any]:
        data = self.load_all_data()
        return data["groups"]

    def get_all_user_data(self) -> Dict[str, Any]:
        data = self.load_all_data()
        return data["users"]

    def save_all_group_data(self, data: Dict[str, Any]):
        all_data = self.load_all_data()
        all_data["groups"] = data
        self.save_all_data(all_data)

    def save_all_user_data(self, data: Dict[str, Any]):
        all_data = self.load_all_data()
        all_data["users"] = data
        self.save_all_data(all_data)

    def save_group_data(self, group_id: str, group_data: Dict[str, Any]):
        data = self.load_all_data()
        data["groups"][str(group_id)] = group_data
        self.save_all_data(data)

    def get_group_rank_all(self, group_id: str) -> Dict[str, Any]:
        """获取群排行榜数据，无排序"""
        group_data = self.get_group_data(group_id)
        return group_data['rank']

    def get_group_rank_n(self, group_id: str, n: int = 10) -> Dict[str, Any]:
        """获取群前n名排行榜数据，有排序，默认前十名"""
        rank_data = self.get_group_data(group_id)['rank']
        sorted_items = sorted(rank_data.items(), key=lambda x: x[1][1], reverse=True)[:n]
        sorted_rank_data_n = OrderedDict(sorted_items)
        return sorted_rank_data_n

    def save_group_rank(self, group_id: str, rank_data: Dict[str, Any]):
        group_data = self.get_group_data(group_id)
        group_data['rank'] = rank_data
        self.save_group_data(group_id, group_data)

    def update_rank(self, user_id):
        """加入/更新排行榜"""
        user_data = self.get_user_data(user_id)
        user_name = user_data['user_name']
        score = round(user_data['length'] * 0.3 + user_data['hardness'] * 0.7, 2)
        in_group_list = user_data['in_group']
        for group in in_group_list:
            rank = self.get_group_rank_all(group)
            rank[str(user_id)] = [str(user_name), score]
            self.save_group_rank(group, rank)

    def delete_user_from_group_rank(self, group_id, user_id):
        rank_data = self.get_group_rank_all(group_id)
        if user_id in rank_data:
            del rank_data[user_id]
            self.save_group_rank(group_id, rank_data)

    def add_in_group(self, user_id, group_id):
        """加入新群到user_data"""
        user_data = self.get_user_data(user_id)
        if group_id not in user_data['in_group']:
            user_data['in_group'].append(str(group_id))
            self.save_user_data(user_id, user_data)

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """获取用户数据（兼容补全老数据字段与过期状态重置）"""
        data = self.load_all_data()
        user_data = data["users"].get(str(user_id), {})
        
        if user_data:
            changed = False
            now = time.time()
            
            default_items = {'viagra': 0, 'transfer': False, 'pills': False, 'drone': [], 'elf_reminder': True, '20off': False, 'sandbag': False, 'jump_egg': False}
            default_items_num = {'伟哥': 0, '迷幻菌子': 0, '春天的药': 0, '黑店壮丁手术体验卡': 0, '诊所壮丁手术体验卡': 0, '医院壮丁手术体验卡': 0, '六味地黄丸': 0, '负重沙袋': 0, '会跳的蛋': 0, '性转针筒': 0, '牛牛转换器': 0, '猫猫转换器': 0, '春风精灵': 0, '牛牛盲盒': 0, '牛牛寄生虫': 0, '改名卡': 0, '商店8折优惠券': 0, '杀虫剂': 0}
            default_time_rec = {'sign': 0, 'do_self': 0, 'do_other': 0, 'start_work': [0, 0], 'start_exercise': [0, 0], 'start_trans': 0, 'start_20off': 0, 'start_elf': 0, 'battle': 0, 'been_do_other': 0}

            for key, val in default_items.items():
                if key not in user_data.setdefault('items', {}):
                    user_data['items'][key] = val
                    changed = True
            for key, val in default_items_num.items():
                if key not in user_data.setdefault('items_num', {}):
                    user_data['items_num'][key] = val
                    changed = True
            for key, val in default_time_rec.items():
                if key not in user_data.setdefault('time_recording', {}):
                    user_data['time_recording'][key] = val
                    changed = True

            # 状态过期检查
            if user_data['items'].get('transfer', False):
                start_trans = user_data['time_recording'].get('start_trans', 0)
                if now - start_trans > 86400:  
                    user_data['items']['transfer'] = False
                    changed = True
                    
            if user_data['items'].get('20off', False):
                start_20off = user_data['time_recording'].get('start_20off', 0)
                if now - start_20off > 300: 
                    user_data['items']['20off'] = False
                    changed = True
                    
            if changed:
                self.save_user_data(user_id, user_data)
                
        return user_data

    def save_user_data(self, user_id: str, user_data: Dict[str, Any]):
        data = self.load_all_data()
        data["users"][str(user_id)] = user_data
        self.save_all_data(data)

    def create_user(self, group_id: str, user_id: str, user_name: str):
        min_length = self.min_length
        max_length = self.max_length
        min_hardness = self.min_hardness
        max_hardness = self.max_hardness
        init_length = random_normal_distribution_int(min_length, max_length + 1, 1)
        init_hardness = random_normal_distribution_int(min_hardness, max_hardness + 1, 1)

        if init_length / (max_length - min_length + 1) < 0.3:
            message = '😑 长度好短，牛牛从小就自卑\n'
        elif init_length / (max_length - min_length + 1) <= 0.6:
            message = '🤨 长度资质平平，牛牛达到了平均水平\n'
        else:
            message = '😍 长度超长！牛牛犹如天牛下凡\n'

        if init_hardness / (max_hardness - min_hardness + 1) < 0.3:
            message += '😑 硬度好软，牛牛从小体弱多病'
        elif init_hardness / (max_hardness - min_hardness + 1) <= 0.6:
            message += '🤨 硬度资质平平，牛牛能直立行走'
        else:
            message += '😍 硬度超硬！牛牛硬的像根钢管'

        init_user_data = {
            "niuniu_name": f'{user_name}的牛牛',
            "user_name": user_name,
            "length": init_length,
            "coins": 0,
            "hardness": init_hardness,
            "hole": 0,
            "sensitivity": 0,
            "win_count": 0,
            "current_win_count": 0,
            "in_group": [group_id],
            'items': {
                'viagra': 0, 'transfer': False, 'pills': False, 'drone': [], 
                'elf_reminder': True, '20off': False, 'sandbag': False, 'jump_egg': False,
            },
            'items_num':{
                '伟哥': 0, '迷幻菌子': 0, '春天的药': 0, '黑店壮丁手术体验卡': 0, 
                '诊所壮丁手术体验卡': 0, '医院壮丁手术体验卡': 0, '六味地黄丸': 0, 
                '负重沙袋': 0, '会跳的蛋': 0, '性转针筒': 0, '牛牛转换器': 0, 
                '猫猫转换器': 0, '春风精灵': 0, '牛牛盲盒': 0, '牛牛寄生虫': 0, 
                '改名卡': 0, '商店8折优惠券': 0, '杀虫剂': 0,
            },
            'time_recording': {
                'sign': 0, 'do_self': 0, 'do_other': 0, 'start_work': [0,0], 
                'start_exercise': [0,0], 'start_trans': 0, 'start_20off': 0, 'start_elf': 0,
                'battle': 0, 'been_do_other': 0,
            },
        }
        self.save_user_data(user_id, init_user_data)
        self.update_rank(user_id)
        return message, init_length, init_hardness

    def delete_user(self, user_id: str):
        user_data = self.get_user_data(user_id)
        in_group = user_data['in_group']
        for group_id in in_group:
            self.delete_user_from_group_rank(group_id, user_id)
        all_user_data = self.get_all_user_data()
        del all_user_data[user_id]
        self.save_all_user_data(all_user_data)

    def add_group_manager(self, group_id, user_id):
        group_data = self.get_group_data(group_id)
        if user_id not in group_data['manager']:
            group_data['manager'].append(user_id)
            self.save_group_data(group_id, group_data)

    def del_group_manager(self, group_id, user_id):
        group_data = self.get_group_data(group_id)
        if user_id in group_data['manager']:
            group_data['manager'].remove(user_id)
            self.save_group_data(group_id, group_data)

    def set_group_enabled(self, group_id, enabled: bool):
        group_data = self.get_group_data(group_id)
        plugin_enabled = group_data['plugin_enabled']
        if enabled != plugin_enabled:
            group_data['plugin_enabled'] = enabled
            self.save_group_data(group_id, group_data)

    def set_value(self, user_id, item_path: list, item_value: Any):
        user_data = self.get_user_data(user_id)
        if len(item_path) == 1:
            user_data[item_path[0]] = item_value
        elif len(item_path) == 2:
            user_data[item_path[0]][item_path[1]] = item_value
        self.save_user_data(user_id, user_data)

    def set_niuniu_name(self, user_id, niuniu_name: str) -> bool:
        user_data = self.get_user_data(user_id)
        if user_data['niuniu_name'] != str(niuniu_name):
            user_data['niuniu_name'] = str(niuniu_name)
            self.save_user_data(user_id, user_data)
            return True
        return False

    def add_length(self, group_id, user_id, length: int):
        user_data = self.get_user_data(user_id)
        user_drone = user_data['items']['drone']
        if len(user_drone) > 0:
            length = int(length / (len(user_drone) + 1))
            if length > 0:
                for i in user_drone:
                    # 寄生虫主人可能已注销，跳过不存在的用户防止崩溃
                    if self.get_user_data(i):
                        self.add_length(group_id, i, length)
        user_data['length'] += length
        self.save_user_data(user_id, user_data)
        self.update_rank(user_id)
        return length

    def del_length(self, user_id, length: int):
        user_data = self.get_user_data(user_id)
        user_data['length'] = max(1, user_data['length'] - length)
        self.save_user_data(user_id, user_data)
        self.update_rank(user_id)

    def add_hole(self, user_id, deep: int):
        user_data = self.get_user_data(user_id)
        user_data['hole'] += deep
        self.save_user_data(user_id, user_data)

    def del_hole(self, user_id, deep: int):
        user_data = self.get_user_data(user_id)
        user_data['hole'] = max(0, user_data['hole'] - deep)
        self.save_user_data(user_id, user_data)

    def add_sensitivity(self, user_id, sensitivity: int):
        user_data = self.get_user_data(user_id)
        user_data['sensitivity'] += sensitivity
        self.save_user_data(user_id, user_data)

    def del_sensitivity(self, user_id, sensitivity: int):
        user_data = self.get_user_data(user_id)
        user_data['sensitivity'] = max(0, user_data['sensitivity'] - sensitivity)
        self.save_user_data(user_id, user_data)

    def add_hardness(self, user_id, hardness: int):
        user_data = self.get_user_data(user_id)
        user_data['hardness'] += hardness
        self.save_user_data(user_id, user_data)
        self.update_rank(user_id)

    def del_hardness(self, user_id, hardness: int):
        user_data = self.get_user_data(user_id)
        user_data['hardness'] = max(1, user_data['hardness'] - hardness)
        self.save_user_data(user_id, user_data)
        self.update_rank(user_id)

    def add_coins(self, user_id, coins: int):
        user_data = self.get_user_data(user_id)
        user_data['coins'] += coins
        self.save_user_data(user_id, user_data)

    def del_coins(self, user_id, coins: int):
        user_data = self.get_user_data(user_id)
        user_data['coins'] -= coins
        self.save_user_data(user_id, user_data)

    def reset_win_count(self, user_id):
        user_data = self.get_user_data(user_id)
        if user_data['current_win_count'] == 0:
            return False
        else:
            user_data['current_win_count'] = 0
            self.save_user_data(user_id, user_data)
            return True

    def update_win_count(self, user_id):
        user_data = self.get_user_data(user_id)
        user_data['current_win_count'] += 1
        self.save_user_data(user_id, user_data)
        if user_data['current_win_count'] > user_data['win_count']:
            user_data['win_count'] = user_data['current_win_count']
            self.save_user_data(user_id, user_data)
            return True
        return False

    def use_item(self, user_id, item_path: list, num: int = 1):
        user_data = self.get_user_data(user_id)
        if len(item_path) == 2:
            if user_data[item_path[0]][item_path[1]] >= num:
                user_data[item_path[0]][item_path[1]] -= num
                self.save_user_data(user_id, user_data)
                return True
            else:
                return False

    def add_drone(self, user1_id, user2_id, num) -> int:
        user1_data = self.get_user_data(user1_id)
        user2_data = self.get_user_data(user2_id)
        for _ in range(num):
            user2_data['items']['drone'].append(user1_id)
        user1_data['items_num']['牛牛寄生虫'] -= num
        self.save_user_data(user1_id, user1_data)
        self.save_user_data(user2_id, user2_data)

        return user2_data['items']['drone'].count(user1_id)

    def remove_drone(self, user_id, num):
        """移除用户身上前 num 只寄生虫，并扣除对应数量的杀虫剂"""
        user_data = self.get_user_data(user_id)
        exist_drone = user_data['items']['drone']
        num = max(0, int(num))
        if num >= len(exist_drone):
            user_data['items']['drone'] = []
        else:
            user_data['items']['drone'] = user_data['items']['drone'][num:]
        # 防止数量被扣成负数导致杀虫剂自锁
        user_data['items_num']['杀虫剂'] = max(0, user_data['items_num'].get('杀虫剂', 0) - num)
        self.save_user_data(user_id, user_data)