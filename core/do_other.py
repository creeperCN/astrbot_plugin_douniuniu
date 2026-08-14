import random
import time

from .data_manager import DataManager
from .utils import random_normal_distribution_int, get_add_text, \
    format_length, check_cooldown


class DoOther:
    def __init__(self):
        self.data_manager = DataManager()
        self.probabilities_niu = {
            '锁爽了': 50,
            '锁痛了': 30,
            '躲了': 15,
            '锁断了': 5,
        }
        self.reason_niu = {
            '锁爽了': [
                '🥵 对方完全陶醉在你的口技之中',
                '🥵 对方对你的技术赞不绝口，他的牛牛在这个过程中获得了成长',
            ],
            '锁痛了': [
                '😡 锁的过程中你突然想磨牙，最终没控制好力道把对方锁痛了',
                '😡 对方想脱离你的夺命连环锁，但是你就是不松口，强制脱离导致断了一节',
            ],
            '躲了': [
                '🤡 对方一个转身躲过了你的血盆大口',
                '🤡 对方牛牛捏捏的说：“今天状态不好，还是算了吧”',
                '🤡 就在你准备开始的时候，对方的牛牛突然被另一个群友锁住',
            ],
            '锁断了': [
                '😱 对方的牛牛突然开始融化，你在完全融化之前松了口',
                '😱 对方的牛牛堵得你喘不过气，快窒息的你求生意识下咬断了一节',
            ]
        }
        self.reason_mao = {
            '锁爽了': [
                '🥵 对方完全陶醉在你的舔技之中', 
                '🥵 对方对你的技术赞不绝口，他的猫猫在这个过程中获得了成长'
            ],
            '锁痛了': [
                '😡 舔的过程中你突然想磨牙，最终没控制好力道把对方弄痛了', 
                '😡 对方想脱离你的夺命连环吸，强制脱离导致受损'
            ],
            '躲了': [
                '🤡 对方一个转身躲过了你的血盆大口', 
                '🤡 对方捏捏的说：“今天状态不好，还是算了吧”', 
                '🤡 就在你准备开始的时候，对方的猫猫突然被另一个群友吸住'
            ],
            '锁断了': [
                '😱 对方的猫猫突然开始泛滥，你在完全溺水之前松了口', 
                '😱 对方的猫猫堵得你喘不过气，快窒息的你求生意识下咬了一口'
            ]
        }

    def do_other_niu(self, group_id, user1_id, user2_id, do_other_cd, bypass_victim_cd=False) -> str:
        """1锁2的牛牛"""
        user1_data = self.data_manager.get_user_data(user1_id)
        user2_data = self.data_manager.get_user_data(user2_id)
        text = ''
        can_do_other, remain_time = check_cooldown(user1_data['time_recording']['do_other'], do_other_cd)
        if not can_do_other:
            text += f'❌ 心急锁不到热牛牛，cd剩余：{remain_time}'
            return text

        # 防刷：被锁方短时免疫，避免多人围锁同一目标
        if not bypass_victim_cd:
            can_be_locked, victim_remain = check_cooldown(
                user2_data['time_recording'].get('been_do_other', 0), do_other_cd)
            if not can_be_locked:
                text += f'❌ 对方刚被锁过还没缓过来，cd剩余：{victim_remain}'
                return text

        self.data_manager.set_value(user1_id, ['time_recording', 'do_other'], time.time())
        if not bypass_victim_cd:
            self.data_manager.set_value(user2_id, ['time_recording', 'been_do_other'], time.time())
        result = random.choices(
            list(self.probabilities_niu.keys()),
            weights=list(self.probabilities_niu.values()),
            k=1
        )[0]
        text += f"{random.choice(self.reason_niu[result])}\n"
        niuniu_name = user2_data['niuniu_name']
        
        if result == '锁爽了':
            add_length = random_normal_distribution_int(1, 6, 1)
            true_length = self.data_manager.add_length(group_id, user2_id, add_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += get_add_text(true_length, add_length, user2_data)
        elif result == '锁痛了':
            del_length = random_normal_distribution_int(1, 4, 1)
            self.data_manager.del_length(user2_id, del_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += f"📏 {niuniu_name}的长度减少了{del_length}cm，当前长度：{format_length(user2_data['length'])}\n"
        elif result == '躲了':
            pass
        elif result == '锁断了':
            del_length = int(user2_data['length'] / 2)
            self.data_manager.del_length(user2_id, del_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += f"📏 {niuniu_name}的长度减少了{del_length}cm，当前长度：{format_length(user2_data['length'])}\n"
        return text

    def do_other_mao(self, group_id, user1_id, user2_id, do_other_cd, bypass_victim_cd=False) -> str:
        """1吸2的猫猫"""
        user1_data = self.data_manager.get_user_data(user1_id)
        user2_data = self.data_manager.get_user_data(user2_id)
        text = ''
        can_do_other, remain_time = check_cooldown(user1_data['time_recording']['do_other'], do_other_cd)
        if not can_do_other:
            text += f'❌ 心急吸不到热猫猫，cd剩余：{remain_time}'
            return text

        # 防刷：被锁方短时免疫，避免多人围锁同一目标
        if not bypass_victim_cd:
            can_be_locked, victim_remain = check_cooldown(
                user2_data['time_recording'].get('been_do_other', 0), do_other_cd)
            if not can_be_locked:
                text += f'❌ 对方刚被锁过还没缓过来，cd剩余：{victim_remain}'
                return text

        self.data_manager.set_value(user1_id, ['time_recording', 'do_other'], time.time())
        if not bypass_victim_cd:
            self.data_manager.set_value(user2_id, ['time_recording', 'been_do_other'], time.time())
        result = random.choices(list(self.probabilities_niu.keys()), weights=list(self.probabilities_niu.values()), k=1)[0]
        text += f"{random.choice(self.reason_mao[result])}\n"
        niuniu_name = user2_data['user_name'] + "的猫猫"
        
        if result == '锁爽了':
            add_length = random_normal_distribution_int(1, 6, 1)
            self.data_manager.add_hole(user2_id, add_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += f"📏 {niuniu_name}的深度增加了{add_length}cm，当前深度：{format_length(user2_data['hole'])}\n"
        elif result == '锁痛了':
            del_length = random_normal_distribution_int(1, 4, 1)
            self.data_manager.del_hole(user2_id, del_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += f"📏 {niuniu_name}的深度减少了{del_length}cm，当前深度：{format_length(user2_data['hole'])}\n"
        elif result == '躲了':
            pass
        elif result == '锁断了':
            del_length = int(user2_data['hole'] / 2)
            self.data_manager.del_hole(user2_id, del_length)
            user2_data = self.data_manager.get_user_data(user2_id)
            text += f"📏 {niuniu_name}的深度减少了{del_length}cm，当前深度：{format_length(user2_data['hole'])}\n"
        return text