from constants import FONT_BIG, FONT_SMALL

TRANSLATION_ID = {'en': 0, 'zh': 1}

TR_FONTS = (
    (  # en
        FONT_BIG, FONT_SMALL),
    (  # cht
        ('Microsoft JhengHei', '12'), ('Segoe UI', '9')))

TRANSLATIONS = (
    (  # en
        'Kitava-Touched', 'Innocence-Touched', 'Shakari-Touched', 'Abberath-Touched',
        'Tukohama-Touched', 'Brine King-Touched', 'Arakaali-Touched', 'Solaris-Touched',
        'Lunaris-Touched', 'Effigy', 'Empowered Elements', 'Crystal-Skinned', 'Invulnerable',
        'Corrupter', 'Mana Siphoner', 'Storm Strider', 'Mirror Image', 'Magma Barrier',
        'Evocationist', 'Corpse Detonator', 'Flame Strider', 'Soul Eater', 'Ice Prison',
        'Frost Strider', 'Treant Horde', 'Temporal Bubble', 'Entangler', 'Drought Bringer', 'Hexer',
        'Executioner', 'Rejuvenating', 'Necromancer', 'Trickster', 'Assassin', 'Empowered Minions',
        'Heralding Minions', 'Arcane Buffer', 'Berserker', 'Bloodletter', 'Bombardier',
        'Bonebreaker', 'Chaosweaver', 'Consecrator', 'Deadeye', 'Dynamo', 'Echoist', 'Flameweaver',
        'Frenzied', 'Frostweaver', 'Gargantuan', 'Hasted', 'Incendiary', 'Juggernaut',
        'Malediction', 'Opulent', 'Overcharged', 'Permafrost', 'Sentinel', 'Soul Conduit',
        'Steel-Infused', 'Stormweaver', 'Toxic', 'Vampiric', 'Trash'),
    (  # cht
        '奇塔弗之觸', '善之觸', '夏卡莉之觸', '艾貝拉斯之觸', '圖克哈瑪之觸', '海洋王之觸', '艾爾卡莉之觸', '日神之觸', '月神之觸', '雕像',
        '強化元素', '晶瑩剔透', '刀槍不入', '腐化者', '魔靈吸取', '風行者', '鏡像幻影', '熔岩屏障', '招魂師', '陰屍爆破', '炎行者', '嗜魂者',
        '冰牢', '霜行者', '樹人部落', '短暫幻想', '尾隨魔', '乾旱先鋒', '咒術師', '劊子手', '振興', '死靈師', '詐欺師', '刺客', '增幅召喚物',
        '先鋒召喚物', '奧術緩衝', '狂戰士', '放血者', '投彈手', '裂骨者', '混沌編織', '奉獻使徒', '銳眼', '發電機', '回聲者', '烈焰編織',
        '喪心病狂', '冰霜編織', '龐然大物', '急速', '縱火', '勇士', '憎惡', '豐饒', '超負荷', '永凍土', '哨兵', '魂靈牽引', '鑄鋼',
        '風暴編織', '毒素', '吸血魔', '垃圾'))

class Translation:

    def __init__(self, id='en') -> None:
        self._tr_idx = TRANSLATION_ID.get(id, 0)
        self._tr_tbl = None if self._tr_idx == 0 else dict(
            zip(TRANSLATIONS[0], TRANSLATIONS[self._tr_idx]))

    def get_text(self, text) -> str:
        if self._tr_tbl is None:
            return text
        elif text[0] == 'x':
            _splitted = text.split(' ', 1)
            _splitted[1] = self._tr_tbl.get(_splitted[1], 'N/A')
            tr_str = ' '.join(_splitted)
        else:
            tr_str = self._tr_tbl.get(text, 'N/A')
        return tr_str

    def get_font_big(self):
        return TR_FONTS[self._tr_idx][0]

    def get_font_small(self):
        return TR_FONTS[self._tr_idx][1]
