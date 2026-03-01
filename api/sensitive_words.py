# -*- coding: utf-8 -*-
"""
抖音/自媒体平台敏感词过滤模块
"""

import re

# 抖音常见违禁词分类
SENSITIVE_WORDS = {
    # 政治敏感
    'political': [
        '习近平', '李克强', '温家宝', '胡锦涛', '江泽民', '毛泽东', '邓小平',
        '共产党', '国民党', '台独', '港独', '疆独', '藏独', '反华', '颠覆',
        '政权', '革命', '起义', '暴动', '游行', '示威', '静坐'
    ],
    
    # 色情低俗
    'porn': [
        '色情', '淫秽', '性爱', '性交', '做爱', '上床', '约炮', '裸聊', '裸照',
        '乳房', '乳头', '阴道', '阴茎', '生殖器', '嫖娼', '卖淫', '性服务',
        'SM', '性奴', '迷药', '催情', '春药'
    ],
    
    # 暴力恐怖
    'violence': [
        '杀人', '自杀', '他杀', '谋杀', '砍人', '爆炸', '炸弹', '枪支', '弹药',
        ' terrorist', '恐怖组织', 'ISIS', '基地组织', '暴力', '血腥', '残忍',
        '虐待', '殴打', '霸凌', '校园暴力'
    ],
    
    # 违法违规
    'illegal': [
        '毒品', '吸毒', '贩毒', '制毒', '大麻', '冰毒', '海洛因', '可卡因',
        '赌博', '博彩', '彩票', '赌球', '赌马', '老虎机', '洗钱', '诈骗',
        '传销', '非法集资', '套路贷', '高利贷', '裸贷'
    ],
    
    # 医疗健康违规
    'medical': [
        '特效药', '神药', '秘方', '偏方', '根治', '治愈', '药到病除',
        '减肥神药', '增高药', '壮阳药', '丰胸', '整容', '整形', '医美',
        '瘦脸针', '玻尿酸', '肉毒素', '非法行医'
    ],
    
    # 封建迷信
    'superstition': [
        '算命', '占卜', '看相', '风水', '改运', '转运', '辟邪', '驱鬼',
        '请神', '跳大神', '巫术', '法术', '符咒', '开光', '法事'
    ],
    
    # 极限词/虚假宣传
    'extreme': [
        '第一', '最好', '最强', '顶级', '极品', '终极', '绝对', '百分百',
        '万能', '永久', '独家', '首创', '国家级', '最高级', '顶级', '第一品牌'
    ],
    
    # 金融投资违规
    'financial': [
        '稳赚', '保本', '高收益', '零风险', '内幕消息', '涨停', '黑马',
        '荐股', '代客理财', '配资', '杠杆', '虚拟货币', '比特币', '挖矿'
    ]
}

# 需要替换的敏感词（替换成*）
REPLACE_WORDS = [
    '死', '杀', '血', '尸', '坟', '墓', '鬼', '妖', '魔', '邪',
    '赌', '毒', '黄', '嫖', '娼', '妓', '婊', '蠢', '笨', '傻',
    '滚', '他妈的', '傻逼', '脑残', '垃圾', '废物'
]

def check_sensitive_words(text):
    """
    检查文本中的敏感词
    返回: (是否包含敏感词, 敏感词列表)
    """
    found_words = []
    
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in text:
                found_words.append((category, word))
    
    return len(found_words) > 0, found_words

def filter_sensitive_words(text):
    """
    过滤敏感词，替换为*
    """
    filtered_text = text
    
    # 替换敏感词
    for word in REPLACE_WORDS:
        if word in filtered_text:
            replacement = '*' * len(word)
            filtered_text = filtered_text.replace(word, replacement)
    
    return filtered_text

def get_prompt_addition():
    """
    获取Prompt附加要求，要求AI避免使用敏感词
    """
    return """
重要提示：请确保生成的内容符合抖音社区规范，避免出现以下类型的词汇：
1. 政治敏感词汇
2. 色情低俗内容
3. 暴力恐怖描述
4. 违法违规信息
5. 医疗虚假宣传
6. 封建迷信活动（可用"传统文化""民俗"等中性词替代）
7. 极限词和虚假宣传
8. 金融投资违规承诺

如有涉及死亡、杀戮等概念，请用"离去""结束""竞争"等中性词替代。
如有涉及算命占卜，请用"文化探讨""传统智慧""心理慰藉"等角度表述。
"""

def clean_for_douyin(text):
    """
    全面清理文本，确保符合抖音规范
    """
    # 先进行敏感词替换
    cleaned = filter_sensitive_words(text)
    
    # 检查是否还有敏感词
    has_sensitive, words = check_sensitive_words(cleaned)
    
    return {
        'cleaned_text': cleaned,
        'has_sensitive': has_sensitive,
        'sensitive_words': words
    }
