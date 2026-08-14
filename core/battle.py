import math
import random

from .data_manager import DataManager
from .utils import probabilistic_decision, random_normal_distribution_int, \
    format_length, get_add_text


class Battle:
    def __init__(self):
        self.data_manager = DataManager()
        self.record_breaking_reward = 10  

    def niu_vs_niu_win_prob(self, user1_id, user2_id, user1_type: str = 'niu', user2_type: str = 'niu'):
        HARDNESS_WEIGHT = 0.7  
        LENGTH_WEIGHT = 0.3  

        user1_data = self.data_manager.get_user_data(user1_id)
        user2_data = self.data_manager.get_user_data(user2_id)

        if user1_type == 'niu':
            user1_1, user1_2 = user1_data['length'], user1_data['hardness']
        else:
            user1_1, user1_2 = user1_data['hole'], user1_data['sensitivity']
            
        if user2_type == 'niu':
            user2_1, user2_2 = user2_data['length'], user2_data['hardness']
        else:
            user2_1, user2_2 = user2_data['hole'], user2_data['sensitivity']
            
        attack_power = user1_1 * LENGTH_WEIGHT + user1_2 * HARDNESS_WEIGHT
        defend_power = user2_1 * LENGTH_WEIGHT + user2_2 * HARDNESS_WEIGHT

        power_diff = attack_power - defend_power
        if user1_data['items']['pills']:
            user1_data['items']['pills'] = False
            self.data_manager.save_user_data(user1_id, user1_data)
            return 'user1', power_diff
            
        clamped_diff = max(-100, min(100, power_diff))
        base_prob = 1 / (1 + math.exp(-clamped_diff * 0.5)) 

        if power_diff > 0:
            random_factor = random.uniform(-0.40, 0.0)
        else:
            random_factor = random.uniform(0.0, 0.40)
        final_prob = max(0.1, min(0.9, base_prob + random_factor)) 

        draw_prob = max(0, 0.3 - 0.03 * abs(power_diff)) 

        rand = random.random()
        if rand < draw_prob:
            return 'draw', power_diff
        elif rand < draw_prob + final_prob * (1 - draw_prob):
            return 'user1', power_diff
        else:
            return 'user2', power_diff

    def user1_vs_user2(self, group_id, user1_id, user2_id) -> str:
        if user1_id == user2_id:
            return "❌ 精神分裂了吗？你不能和自己决斗！"
            
        user1_data = self.data_manager.get_user_data(user1_id)
        user2_data = self.data_manager.get_user_data(user2_id)
        user1_niuniu_name = user1_data['niuniu_name']
        user2_niuniu_name = user2_data['niuniu_name']
        user1_name = user1_data['user_name']
        user2_name = user2_data['user_name']
        
        user1_type = "mao" if user1_data['items']['transfer'] else "niu"
        user2_type = "mao" if user2_data['items']['transfer'] else "niu"
        
        winner, power_diff = self.niu_vs_niu_win_prob(user1_id, user2_id, user1_type, user2_type)
        text = ''
        
        if winner == 'draw':
            text += "⚖️ 双方势均力敌！\n"
            random_num = random.random()
            if random_num < 0.2:
                # 防刷：平局不再给予双方成长，避免双号互刷长度/深度
                text += "📢 双方打得难解难分，最终握手言和，无事发生\n\n"
            elif random_num < 0.4:
                if user1_type == 'niu' and user2_type == 'niu':
                    more_harder_id = user1_id if user1_data['hardness'] >= user2_data['hardness'] else user2_id
                    less_harder_id = user2_id if user1_data['hardness'] >= user2_data['hardness'] else user1_id
                    more_data = self.data_manager.get_user_data(more_harder_id)
                    less_data = self.data_manager.get_user_data(less_harder_id)
                    random_num = random.random()
                    if random_num < 0.3:
                        text += f'📢 双方的牛牛即使激战过后依然缠绕在一起，但是由于{more_data["niuniu_name"]}更硬，强制分开也没有断裂\n\n'
                        less_del = int(less_data['length'] / 2)
                        text += f"📏 {more_data['niuniu_name']}的长度无变化\n"
                        text += f"📏 {less_data['niuniu_name']}的长度减少{less_del}cm\n"
                        self.data_manager.del_length(less_harder_id, less_del)
                    else:
                        text += "📢 双方的牛牛即使激战过后依然缠绕在一起，强制分开导致长度减半\n\n"
                        user1_del = int(user1_data['length'] / 2)
                        user2_del = int(user2_data['length'] / 2)
                        text += f"📏 {user1_niuniu_name}的长度减少{user1_del}cm\n"
                        text += f"📏 {user2_niuniu_name}的长度减少{user2_del}cm\n"
                        self.data_manager.del_length(user1_id, user1_del)
                        self.data_manager.del_length(user2_id, user2_del)
                elif user1_type == 'mao' and user2_type == 'niu':
                    more_harder_id = user1_id if user1_data['sensitivity'] >= user2_data['hardness'] else user2_id
                    less_harder_id = user2_id if user1_data['sensitivity'] >= user2_data['hardness'] else user1_id
                    more_data = self.data_manager.get_user_data(more_harder_id)
                    less_data = self.data_manager.get_user_data(less_harder_id)
                    random_num = random.random()
                    if random_num < 0.3:
                        if more_harder_id == user1_id:
                            text += f'📢 双方紧紧交合无法分开，但是由于{more_data["user_name"]}的猫猫敏感度强于对方的硬度，强制分开时夹得太紧导致对方的牛牛断裂\n\n'
                            less_del = int(less_data['length'] / 2)
                            text += f"📏 {more_data['user_name']}的猫猫深度无变化\n"
                            text += f"📏 {less_data['niuniu_name']}的长度减少{less_del}cm\n"
                            self.data_manager.del_length(less_harder_id, less_del)
                        else:
                            text += f'📢 双方紧紧交合无法分开，但是由于{more_data["niuniu_name"]}更硬，强制分开使对方的猫猫不满自闭了\n\n'
                            less_del = int(less_data['hole'] / 2)
                            text += f"📏 {more_data['niuniu_name']}的长度无变化\n"
                            text += f"📏 {less_data['user_name']}的猫猫深度减少{less_del}cm\n"
                            self.data_manager.del_hole(less_harder_id, less_del)
                    else:
                        text += "📢 双方紧紧交合无法分开，强制分开导致双方长度减半\n\n"
                        user1_del = int(user1_data['hole'] / 2)
                        user2_del = int(user2_data['length'] / 2)
                        text += f"📏 {user1_name}的猫猫深度减少{user1_del}cm\n"
                        text += f"📏 {user2_niuniu_name}的长度减少{user2_del}cm\n"
                        self.data_manager.del_hole(user1_id, user1_del)
                        self.data_manager.del_length(user2_id, user2_del)
                elif user1_type == 'niu' and user2_type == 'mao':
                    more_harder_id = user1_id if user1_data['hardness'] >= user2_data['sensitivity'] else user2_id
                    less_harder_id = user2_id if user1_data['hardness'] >= user2_data['sensitivity'] else user1_id
                    more_data = self.data_manager.get_user_data(more_harder_id)
                    less_data = self.data_manager.get_user_data(less_harder_id)
                    random_num = random.random()
                    if random_num < 0.3:
                        if more_harder_id == user2_id:
                            text += f'📢 双方紧紧交合无法分开，但是由于{more_data["user_name"]}的猫猫敏感度强于对方的硬度，强制分开时夹得太紧导致对方的牛牛断裂\n\n'
                            less_del = int(less_data['length'] / 2)
                            text += f"📏 {more_data['user_name']}的猫猫深度无变化\n"
                            text += f"📏 {less_data['niuniu_name']}的长度减少{less_del}cm\n"
                            self.data_manager.del_length(less_harder_id, less_del)
                        else:
                            text += f'📢 双方紧紧交合无法分开，但是由于{more_data["niuniu_name"]}更硬，强制分开使对方的猫猫不满自闭了\n\n'
                            less_del = int(less_data['hole'] / 2)
                            text += f"📏 {more_data['niuniu_name']}的长度无变化\n"
                            text += f"📏 {less_data['user_name']}的猫猫深度减少{less_del}cm\n"
                            self.data_manager.del_hole(less_harder_id, less_del)
                    else:
                        text += "📢 双方紧紧交合无法分开，强制分开导致双方长度减半\n\n"
                        user1_del = int(user1_data['length'] / 2)
                        user2_del = int(user2_data['hole'] / 2)
                        text += f"📏 {user1_niuniu_name}的长度减少{user1_del}cm\n"
                        text += f"📏 {user2_name}的猫猫深度减少{user2_del}cm\n"
                        self.data_manager.del_hole(user2_id, user2_del)
                        self.data_manager.del_length(user1_id, user1_del)
                else:
                    more_id = user1_id if user1_data['sensitivity'] >= user2_data['sensitivity'] else user2_id
                    less_id = user2_id if user1_data['sensitivity'] >= user2_data['sensitivity'] else user1_id
                    more_data = self.data_manager.get_user_data(more_id)
                    less_data = self.data_manager.get_user_data(less_id)
                    random_num = random.random()
                    if random_num < 0.3:
                        text += f'📢 双方的猫猫被蛟龙似的棍状物联结在一起，但是由于{more_data["user_name"]}的猫猫敏感度强于对方，已经提前满足，强制分开时导致对方的的猫猫未能满足而自闭\n\n'
                        less_del = int(less_data['hole'] / 2)
                        text += f"📏 {more_data['user_name']}的猫猫深度无变化\n"
                        text += f"📏 {less_data['user_name']}的猫猫深度减少{less_del}cm\n"
                        self.data_manager.del_hole(less_id, less_del)
                    else:
                        text += f'📢 双方的猫猫被蛟龙似的棍状物联结在一起，强制分开时导致双方的的猫猫都未能满足而自闭\n\n'
                        user1_del = int(user1_data['hole'] / 2)
                        user2_del = int(user2_data['hole'] / 2)
                        text += f"📏 {user1_name}的猫猫深度减少{user1_del}cm\n"
                        text += f"📏 {user2_name}的猫猫深度减少{user2_del}cm\n"
                        self.data_manager.del_hole(user2_id, user2_del)
                        self.data_manager.del_hole(user1_id, user1_del)
            elif random_num < 0.6:
                if user1_type == 'niu' and user2_type == 'niu':
                    loser_id = random.choice([user1_id, user2_id])
                    loser_name = user1_niuniu_name if loser_id == user1_id else user2_niuniu_name
                    text += f"📢 {loser_name}不愿承认平局，对自己的长度产生了自我怀疑\n\n"
                    loser_del = random_normal_distribution_int(1, 6, 1)
                    self.data_manager.del_length(loser_id, loser_del)
                    text += f"📏 {loser_name}的长度减少{loser_del}cm\n"
                elif user1_type == 'mao' and user2_type == 'niu':
                    loser_id = random.choice([user1_id, user2_id])
                    if loser_id == user2_id:
                        loser_name = user2_niuniu_name
                        text += f"📢 {loser_name}不愿承认平局，对自己的长度产生了自我怀疑\n\n"
                        loser_del = random_normal_distribution_int(1, 6, 1)
                        self.data_manager.del_length(loser_id, loser_del)
                        text += f"📏 {loser_name}的长度减少{loser_del}cm\n"
                    else:
                        loser_name = user1_name
                        text += f"📢 {loser_name}的猫猫不愿承认平局，对自己的深度产生了自我怀疑\n\n"
                        loser_del = random_normal_distribution_int(1, 6, 1)
                        self.data_manager.del_hole(loser_id, loser_del)
                        text += f"📏 {loser_name}的深度减少{loser_del}cm\n"
                elif user1_type == 'niu' and user2_type == 'mao':
                    loser_id = random.choice([user1_id, user2_id])
                    if loser_id == user1_id:
                        loser_name = user1_niuniu_name
                        text += f"📢 {loser_name}不愿承认平局，对自己的长度产生了自我怀疑\n\n"
                        loser_del = random_normal_distribution_int(1, 6, 1)
                        self.data_manager.del_length(loser_id, loser_del)
                        text += f"📏 {loser_name}的长度减少{loser_del}cm\n"
                    else:
                        loser_name = user2_name
                        text += f"📢 {loser_name}的猫猫不愿承认平局，对自己的深度产生了自我怀疑\n\n"
                        loser_del = random_normal_distribution_int(1, 6, 1)
                        self.data_manager.del_hole(loser_id, loser_del)
                        text += f"📏 {loser_name}的深度减少{loser_del}cm\n"
                else:
                    loser_id = random.choice([user1_id, user2_id])
                    loser_name = self.data_manager.get_user_data(loser_id)['user_name']
                    text += f"📢 {loser_name}的猫猫不愿承认平局，对自己的深度产生了自我怀疑\n\n"
                    loser_del = random_normal_distribution_int(1, 6, 1)
                    self.data_manager.del_hole(loser_id, loser_del)
                    text += f"📏 {loser_name}的深度减少{loser_del}cm\n"
            else:
                text += "📢 之后无事发生，下一次再见面想必又会有一场厮杀吧\n"
            text += "💰 平局双方均无收益"
            return text
        elif winner == 'user1':
            winner_id, loser_id = user1_id, user2_id
        else:
            winner_id, loser_id = user2_id, user1_id
            power_diff = -power_diff
            
        winner_data = self.data_manager.get_user_data(winner_id)
        loser_data = self.data_manager.get_user_data(loser_id)
        winner_type = "mao" if winner_data['items']['transfer'] else 'niu'
        loser_type = "mao" if loser_data['items']['transfer'] else 'niu'
        
        if power_diff > 0:
            if winner_type == 'niu' and loser_type == 'niu':
                winner_name, loser_name = winner_data['niuniu_name'], loser_data['niuniu_name']
                winner_user = winner_data['user_name']
                text += random.choice([
                    f"🥊 {winner_name}在这场决斗中势不可挡\n\n",
                    f"🥊 {winner_name}展现了天牛下凡般的实力\n\n",
                    f"🥊 {winner_name}获得了胜利并擦了擦身上在决斗时留下的液体\n\n",
                    f"🥊 整个战场变成{winner_name}的单方面碾压，{loser_name}被按在地上摩擦\n\n",
                ])
                winner_add_length = random_normal_distribution_int(1, 6, 1)
                winner_ture_add = self.data_manager.add_length(group_id, winner_id, winner_add_length)
                text += get_add_text(winner_ture_add, winner_add_length, self.data_manager.get_user_data(winner_id))

                loser_del_length = random_normal_distribution_int(1, 6, 1)
                self.data_manager.del_length(loser_id, loser_del_length)
                text += f"📏 {loser_name}的长度减少{loser_del_length}cm，当前长度：{format_length(self.data_manager.get_user_data(loser_id)['length'])}\n"
            elif winner_type == 'mao' and loser_type == 'niu':
                winner_user, loser_name = winner_data['user_name'], loser_data['niuniu_name']
                text += random.choice([
                    f"🥊 {winner_user}的猫猫在这场决斗中势不可挡\n\n",
                    f"🥊 {winner_user}的猫猫展现了天猫下凡般的实力\n\n",
                    f"🥊 {winner_user}的猫猫获得了胜利并擦了擦身上在决斗时留下的液体\n\n",
                    f"🥊 整个战场变成{winner_user}猫猫的单方面碾压，{loser_name}被压在地上摩擦\n\n",
                ])
                winner_add_length = random_normal_distribution_int(1, 6, 1)
                self.data_manager.add_hole(winner_id, winner_add_length)
                text += f"📏 {winner_user}的猫猫深度增加{winner_add_length}cm，当前深度：{format_length(self.data_manager.get_user_data(winner_id)['hole'])}\n"

                loser_del_length = random_normal_distribution_int(1, 6, 1)
                self.data_manager.del_length(loser_id, loser_del_length)
                text += f"📏 {loser_name}的长度减少{loser_del_length}cm，当前长度：{format_length(self.data_manager.get_user_data(loser_id)['length'])}\n"
            elif winner_type == 'mao' and loser_type == 'mao':
                winner_user, loser_user, loser_name = winner_data['user_name'], loser_data['user_name'], loser_data['niuniu_name']
                text += random.choice([
                    f"🥊 {winner_user}的猫猫在这场决斗中势不可挡\n\n",
                    f"🥊 {winner_user}的猫猫展现了天猫下凡般的实力\n\n",
                    f"🥊 {winner_user}的猫猫获得了胜利并擦了擦身上在决斗时留下的液体\n\n",
                    f"🥊 整个战场变成{winner_user}猫猫的单方面碾压，{loser_name}被压在地上摩擦\n\n",
                ])
                winner_add_length = random_normal_distribution_int(1, 6, 1)
                self.data_manager.add_hole(winner_id, winner_add_length)
                text += f"📏 {winner_user}的猫猫深度增加{winner_add_length}cm，当前深度：{format_length(self.data_manager.get_user_data(winner_id)['hole'])}\n"

                loser_del_length = random_normal_distribution_int(1, 6, 1)
                self.data_manager.del_hole(loser_id, loser_del_length)
                text += f"📏 {loser_user}的猫猫深度减少{loser_del_length}cm，当前深度：{format_length(self.data_manager.get_user_data(loser_id)['hole'])}\n"
                
            if winner_data['items']['pills']:
                self.data_manager.set_value(winner_id, ['items', 'pills'], False)
                text += f"💰 六味地黄丸使用成功，本次胜利不获得金币\n"
            else:
                winner_add_coins = random_normal_distribution_int(1, 21, 2)
                self.data_manager.add_coins(winner_id, winner_add_coins)
                text += f"💰 {winner_user}获得了{winner_add_coins}个金币\n"
        else:
            if winner_type == 'niu' and loser_type == 'niu':
                winner_name, loser_name = winner_data['niuniu_name'], loser_data['niuniu_name']
                winner_user = winner_data['user_name']
                text += random.choice([
                    f"🥊 {winner_name}在这场决斗中觉醒出了新的实力，终结了{loser_name}\n\n",
                    f"🥊 {winner_name}顽强挣扎，活生生耗光了{loser_name}的体力\n\n",
                    f"🥊 {winner_name}失去了意识，但依旧给了{loser_name}最后一击\n\n",
                    f"🥊 {winner_name}居然是扮猪吃老虎，完全拿捏了{loser_name}\n\n",
                ])
                winner_add_length = random_normal_distribution_int(5, 11, 1)
                winner_true_add = self.data_manager.add_length(group_id, winner_id, winner_add_length)
                if winner_true_add < winner_add_length:
                    text += f"📏 {winner_name}劣势获胜，长度在被寄生虫蚕食后暴增了{winner_true_add}cm，当前长度：{format_length(self.data_manager.get_user_data(winner_id)['length'])}\n"
                    text += f'🐛 各寄生虫窃取到了{winner_add_length - winner_true_add}cm，回馈到主人的牛牛中\n'
                else:
                    text += f"📏 {winner_name}劣势获胜，长度暴增{winner_true_add}cm，当前长度：{format_length(self.data_manager.get_user_data(winner_id)['length'])}\n"

                loser_del_length = random_normal_distribution_int(5, 11, 1)
                self.data_manager.del_length(loser_id, loser_del_length)
                text += f"📏 {loser_name}优势落败，长度骤减{loser_del_length}cm，当前长度：{format_length(self.data_manager.get_user_data(loser_id)['length'])}\n"
            elif winner_type == 'mao' and loser_type == 'niu':
                winner_user, loser_name = winner_data['user_name'], loser_data['niuniu_name']
                text += random.choice([
                    f"🥊 {winner_user}的猫猫在这场决斗中越戳越勇，觉醒出了新的实力，终结了{loser_name}\n\n",
                    f"🥊 {winner_user}的猫猫顽强挣扎，活生生榨干了{loser_name}的体力\n\n",
                    f"🥊 {winner_user}的猫猫失去了意识，但依旧吸干了{loser_name}的最后一滴\n\n",
                    f"🥊 {winner_user}居然是扮猫吃老虎，完全拿捏了{loser_name}\n\n",
                ])
                winner_add_length = random_normal_distribution_int(5, 11, 1)
                self.data_manager.add_hole(winner_id, winner_add_length)
                text += f"📏 {winner_user}的猫猫由于劣势获胜，深度暴增{winner_add_length}cm，当前深度：{format_length(self.data_manager.get_user_data(winner_id)['hole'])}\n"

                loser_del_length = random_normal_distribution_int(5, 11, 1)
                self.data_manager.del_length(loser_id, loser_del_length)
                text += f"📏 {loser_name}优势落败，长度骤减{loser_del_length}cm，当前长度：{format_length(self.data_manager.get_user_data(loser_id)['length'])}\n"
            elif winner_type == 'mao' and loser_type == 'mao':
                winner_user, loser_user, loser_name = winner_data['user_name'], loser_data['user_name'], loser_data['niuniu_name']
                text += random.choice([
                    f"🥊 {winner_user}的猫猫在这场决斗中越戳越勇，觉醒出了新的实力，终结了{loser_name}\n\n",
                    f"🥊 {winner_user}的猫猫顽强挣扎，活生生榨干了{loser_name}的体力\n\n",
                    f"🥊 {winner_user}的猫猫失去了意识，但依旧吸干了{loser_name}的最后一滴\n\n",
                    f"🥊 {winner_user}居然是扮猫吃老虎，完全拿捏了{loser_name}\n\n",
                ])
                winner_add_length = random_normal_distribution_int(5, 11, 1)
                self.data_manager.add_hole(winner_id, winner_add_length)
                text += f"📏 {winner_user}的猫猫由于劣势获胜，深度暴增{winner_add_length}cm，当前深度：{format_length(self.data_manager.get_user_data(winner_id)['hole'])}\n"

                loser_del_length = random_normal_distribution_int(5, 11, 1)
                self.data_manager.del_hole(loser_id, loser_del_length)
                text += f"📏 {loser_user}的猫猫由于优势落败，深度骤减{loser_del_length}cm，当前深度：{format_length(self.data_manager.get_user_data(loser_id)['hole'])}\n"
                
            if winner_data['items']['pills']:
                self.data_manager.set_value(winner_id, ['items', 'pills'], False)
                text += f"💰 六味地黄丸使用成功，本次胜利不获得金币\n"
            else:
                winner_add_coins = random_normal_distribution_int(20, 41, 2)
                self.data_manager.add_coins(winner_id, winner_add_coins)
                text += f"💰 由于是劣势获胜，{winner_user}得到了女神的馈赠，获得{winner_add_coins}个金币\n"
                
        # 结算连胜
        loser_user = self.data_manager.get_user_data(loser_id)['user_name']
        winner_user = self.data_manager.get_user_data(winner_id)['user_name']
        loser_win_count = self.data_manager.get_user_data(loser_id)['current_win_count']
        if self.data_manager.reset_win_count(loser_id):
            text += f"😱 {winner_user}终结了{loser_user}的{loser_win_count}连胜，{winner_user}会成为下一个魔王吗？\n"
            if loser_win_count > 3:
                reward = random_normal_distribution_int(100, 151, 2)
                self.data_manager.add_coins(winner_id, reward)
                text += f"😈 {winner_user}的壮举受到了魔王的注意，额外获得{reward}个金币\n"
                
        if self.data_manager.update_win_count(winner_id):
            winner_current_win = self.data_manager.get_user_data(winner_id)['current_win_count']
            text += f"😈 {winner_user}取得了{winner_current_win}连胜，打破了自己的最高连胜记录！\n"
            reward = winner_current_win * self.record_breaking_reward
            self.data_manager.add_coins(winner_id, reward)
            text += f"💰 {winner_user}由于打破了最高记录，额外获得了{reward}个金币，下一级收益：{reward + self.record_breaking_reward}\n"
            
        user1_data = self.data_manager.get_user_data(user1_id)
        current_win_count = user1_data['current_win_count']
        win_count = user1_data['win_count']
        text += f'⚔ {user1_name}当前连胜：{current_win_count} | 最高连胜：{win_count}'
        return text