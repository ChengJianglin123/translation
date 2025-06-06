from automatic_translation2.csv_method import get_data_from_csv, write_pd_data_to_csv_file
from automatic_translation2.google_translation import GoogleTranslation


class GoogleTranslator_EXCEPTION(GoogleTranslation):
    def __init__(self):
        # 翻译查找目标语言的网站 https://pygtrans.readthedocs.io/zh-cn/latest/target.html
        super().__init__()
        self.data = {'data_path': r"/Users/admin/Desktop/翻译/临时翻译文件/",  # 数据路径
                     'raw_data_name': "翻译文件.csv",  # 初始数据
                     "old_language": "zh-CN",  # 翻译源语言
                     "new_language_list_ios_app": ["zh-TW", "fr", "ja", "de", "es", "ko", "pt", "it", "nl", "sv", "pl",
                                                   "ru", "da", "fi", "no", "id", "vi", "th", "ar", "tr"],  # 翻译的目标语言列表
                     "new_language_list_pica_web": ["key", "en1", "zh-CN1", "zh-TW", "fr", "ja", "de", "es", "ko", "pt",
                                                    "it", "nl", "sv", "pl", "ru", "da", "fi", "no", "id", "vi", "th",
                                                    "ar", 'tr'],  # 翻译的目标语言列表
                     "new_language_list_artguru_web": ["key", "en1", "es", "ja", "ko", "zh-TW", "de", "fr",
                                                       "ar", "it", "pt", "ru", "id", "tr", "vi", "th", "nl", "sv", "pl",
                                                       "fi", "da", 'no'],
                     'language_list_cn': {"zh-CN1": "简体中文", "en1": "英语", "fr": "法语", "ja": "日语", "de": "德语",
                                          "es": "西语", "zh-TW": "繁体中文", "ko": "韩语", "pt": "葡语",
                                          "it": "意大利语",
                                          "nl": "荷兰语",
                                          "sv": "瑞典语", "pl": "波兰语", "ru": "俄语", "da": "丹麦语", "fi": "芬兰语",
                                          "no": "挪威语",
                                          "id": "印尼语", "vi": "越南语", "th": "泰语", "ar": "阿语", "key": "文案键",
                                          'tr': '土耳其'}
                     }

    def csv_translation_write_to_csv(self, data_path, raw_data_name, new_language_list, language_list_cn, old_data,
                                     client):
        """
        :param client:
        :param old_data: 仅支持 "en_英语" 和 “zh-CN_中文"
        :param data_path: 需要翻译的文件地址
        :param raw_data_name: 需要翻译的文件名称
        :param new_language_list: 需要翻译的语种list，默认使用中文翻译
        :param language_list_cn:中英对应表
        """
        if old_data == "en_英语":
            old_language = "en"
        elif old_data == "zh-CN_中文":
            old_language = "zh-CN"
        else:
            old_language = "zh-CN"

        # 将 en_list 与 cn_list 从 csv 文件中读取出来
        pd_result_data = get_data_from_csv(data_path, raw_data_name)

        # 将原始数据进行修正，去掉前后空格，中文符号变为英文符号
        pd_result_data['en_英语'] = self.zh_symbols_to_en_symbols(pd_result_data['en_英语'])
        pd_result_data['zh-CN_中文'] = self.zh_symbols_to_en_symbols(pd_result_data['zh-CN_中文'])

        # 如果是给 web 端进行翻译，则在开始就对源内容进行占位符替换
        if client == "web" or client == "ios":
            pd_result_data = self.placeholder_general_replace(pd_result_data)
        # 先进行名词保护性替换，这是要专门给翻译模型的数据
        noun_pd_result_data = self.input_noun_protection(pd_result_data)

        # 从这里开始翻译
        # 翻译出来的新语言，按格式整理到结果列表中, 数据源是：进行了名词保护替换后的数据
        for new_language in new_language_list:

            # ------------------ 这里是为了适配不同的语言类型，使用不同的源语言进行翻译 --------------------------------------------
            # 如果源语言使用英语，则翻译中文繁体时，也需要使用中文简体进行翻译
            if old_language == "en" and new_language == "zh-TW":
                special_old_language = "zh-CN"
                special_old_data = 'zh-CN_中文'
                new_data_list = self.google_translate_texts(old_data_list=noun_pd_result_data[special_old_data],
                                                            old_language=special_old_language,
                                                            new_language=new_language,
                                                            english_language=noun_pd_result_data['en_英语'])
            elif new_language == "zh-CN1":
                new_data_list = pd_result_data['zh-CN_中文']
            elif new_language == "en1":
                new_data_list = pd_result_data['en_英语']
            # key 写入
            elif new_language == "key":
                new_data_list = self.en_to_key(pd_result_data['en_英语'])
            # 其他情况则翻译顺序不变
            else:
                new_data_list = self.google_translate_texts(old_data_list=noun_pd_result_data[old_data],
                                                            old_language=old_language,
                                                            new_language=new_language,
                                                            english_language=noun_pd_result_data['en_英语'])
            # 将名词保护进行还原
            new_data_list = self.output_noun_protection(new_data_list)

            # 将需翻译的语种添加进入表头
            pd_result_data[f"{new_language}_{language_list_cn[new_language]}"] = new_data_list

        # 将变量进行还原
        if client == "ios":
            pd_result_data = self.placeholder_replace(pd_result_data)
        # 将数据集合写入到目标 csv 文件中
        write_pd_data_to_csv_file(data_path, raw_data_name, pd_result_data)
        print(pd_result_data)
        print("-" * 58)
        print("翻译接结束")


def if_product(client, num2):
    # 判断用哪个翻译顺序
    if client[num2] == "artguru_web":
        _new_language_list = 'new_language_list_artguru_web'
    elif client[num2] == "pica_web":
        _new_language_list = 'new_language_list_pica_web'
    else:
        _new_language_list = 'new_language_list_ios_app'

    # 判断用哪个变量替换
    if client[num2] == "artguru_web":
        _client_product = 'web'
    elif client[num2] == "pica_web":
        _client_product = 'web'
    else:
        _client_product = 'ios'
    return _new_language_list, _client_product


if __name__ == '__main__':
    # 这一行是翻译到原csv文件里
    old_data_list = ["en_英语", "zh-CN_中文"]
    num = 1
    client = ["ios", "pica_web", "artguru_web", "be"]
    num2 = 1
    print(f"{client[num2]}端翻译开始：")

    # 通过产品判断用什么翻译语言列表
    new_language_list, client_product = if_product(client, num2)

    ge = GoogleTranslator_EXCEPTION()
    data = ge.data
    ge.csv_translation_write_to_csv(data_path=data['data_path'],
                                    raw_data_name=data['raw_data_name'],
                                    new_language_list=data[new_language_list],
                                    language_list_cn=data['language_list_cn'],
                                    old_data=old_data_list[num],
                                    client=client_product)
