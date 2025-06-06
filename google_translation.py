from pygtrans import Translate


class GoogleTranslation:
    def __init__(self):
        self.noun_list = ['Pica AI', 'Artguru', 'App Store', 'stripe', "Google", "Facebook", "Apple"]
        self.noun_dict = {'Pica AI': '{{1}}', 'Artguru': '{{2}}', 'App Store': '{{3}}', 'stripe': '{{4}}',
                          "Google": '{{5}}', "Facebook": '{{6}}', "Apple": '{{7}}'}

    def google_translate_texts(self, old_data_list, old_language, new_language, english_language):
        """
         选用谷歌翻译将 old_language 语种，翻译为 new_language 目标语种
        :param old_data_list: list[]，需要翻译的数据列表
        :param old_language: 需要翻译的源语言
        :param new_language: 翻译后的目标语言
        :param english_language: 原英语，用来做首字母有没有大写的判断，如果有大写，其他多语言首字母也大写
        :return: list 返回翻译后的目标语言数据列表
        """
        # 创建谷歌翻译对象
        client = Translate()
        # 将源数据按照格式进行翻译
        new_datas = client.translate(old_data_list, source=old_language, fmt='text', target=new_language)
        new_data_list = []
        for i in new_datas:
            new_data_list.append(i.translatedText)

        capitalize_new_data_list = []  # 这个是用来首字母替换的语言

        # 根据 english 源语言是否进行了首字母大写，判断是否要对其他语种的首字母进行大写
        for a, b in zip(english_language, new_data_list):
            # 判断字符串长度为非 0
            if len(a) > 0:
                # 首字母大写则进行大写替换
                if a[0].isupper() is True:
                    b = b.capitalize()
                # 首字母非大写则进行小写替换
                else:
                    b = b[:1].lower() + b[1:]
            capitalize_new_data_list.append(b)
        return capitalize_new_data_list

    def input_noun_protection(self, pd_result_data):
        """
        谷歌翻译进行名词保护，即在翻译前将需要保护的名词加上 {{}}，例如 Pica AI，替换成{{Pica AI}}
        :param pd_result_data: 输入原始的数据 dict 类型
        :return:输出替换后的数据 dict 类型，结构不动
        """
        en_list = pd_result_data['en_英语']
        cn_list = pd_result_data['zh-CN_中文']
        new_en_list = []
        new_cn_list = []

        # 英语来一遍
        for i in en_list:
            new_i = ''
            for j in self.noun_list:
                new_i = i.replace(f'{j}', f'{self.noun_dict[j]}')
                i = new_i
            new_en_list.append(new_i)

        # 中文来一遍
        for n in cn_list:
            new_n = ''
            for k in self.noun_list:
                new_n = n.replace(f'{k}', f'{self.noun_dict[k]}')
                n = new_n
            new_cn_list.append(new_n)
        new_pd_result_data = {'en_英语': new_en_list, 'zh-CN_中文': new_cn_list}
        return new_pd_result_data

    def output_noun_protection(self, old_data_list):
        """
        名词保护，将翻译过后的数据进行名词保护的还原，替换好的 {{Pica AI}} 还原成 Pica AI
        :param old_data_list:
        :return:
        """
        new_data_list = []
        for i in old_data_list:
            new_i = ''
            for j in self.noun_list:
                new_i = i.replace(f'{self.noun_dict[j]}', f'{j}')
                i = new_i
            new_data_list.append(new_i)
        return new_data_list

    def english_point_replace(self, old_data_list):
        """
        将翻译结果中的英文' 替换成 \‘
        :param old_data_list:
        :return:
        """
        new_data_list = []
        for i in old_data_list:
            new_i = i.replace("'", "\\'")
            new_data_list.append(new_i)
        return new_data_list

    def placeholder_general_replace(self, pd_result_data):
        """
        给 web 和 ios app 用的把占位符替换成 web 前端和ios app 需要的占位符 {{a}}
        :param pd_result_data:
        :return:
        """

        # 产品可能提供的占位符号
        placeholder_replace_list = ["%Y-%m-%d", "%d", "XXXX"]
        placeholder_replace_dict = {"%Y-%m-%d": "{{z}}", "%d": "{{x}}", "XXXX": "{{x}}"}
        random_letter = ["{{a}}", "{{b}}", "{{c}}"]

        # 将原始字典键值对拆分为 a 和 b
        for a, b in pd_result_data.items():
            new_list = []
            # 将原需翻译数据进行遍历
            for i in b:
                # 进行替换
                for j in placeholder_replace_list:
                    i = i.replace(j, placeholder_replace_dict[j])
                    # 如果出现多个，进行不同的替换
                    if i.count("{{x}}") >= 2:
                        for k in range(i.count("{{x}}")):
                            i = i.replace("{{x}}", random_letter[k], 1)
                    # 替换后重组数据
                new_list.append(i)
            # 字典相同的键只会更新值
            pd_result_data[a] = new_list
        return pd_result_data

    # 占位符替换，同时兼容一个翻译中有多个变量的处理
    def placeholder_replace(self, pd_result_data):
        """
        给 web 和 ios app 用的把占位符替换成 web 前端和ios app 需要的占位符 {{a}}
        :param pd_result_data:
        :return:
        """

        placeholder_replace_list = ["{{z}}", "{{x}}", "{{a}}", "{{b}}", "{{c}}", "{{A}}", "{{B}}", "{{C}}"]
        placeholder_replace_dict = {"{{z}}": "%@", "{{x}}": "%d", '{{a}}': "%1$d", "{{b}}": "%2$d", "{{c}}": "%3$d",
                                    '{{A}}': "%1$d", "{{B}}": "%2$d", "{{C}}": "%3$d"}

        # 将全部原数据拆解出来
        for a, b in pd_result_data.items():
            new_list = []
            # 将翻译后的数据进行替换
            for i in b:
                # 将翻译后的数据进行逐个检查和替换
                for j in placeholder_replace_list:
                    i = i.replace(j, placeholder_replace_dict[j])
                new_list.append(i)
            # 将原数据进行更新
            pd_result_data[a] = new_list
        return pd_result_data

    def en_to_key(self, en_list):
        """
        将英语转为key，规则见代码详情
        :param en_list: 英语原文输入
        :return: key的list
        """
        new_key_list = []
        for i in en_list:
            i = i.strip()  # 去除头尾空格
            i = i.replace(" ", "_")  # 将空格转为_
            i = i.lower()  # 全部字母小写
            i = i.replace(".", "")  # .全部去掉
            i = i.replace("{", '')
            i = i.replace("}", '')
            new_key_list.append(i)
        return new_key_list

    def zh_symbols_to_en_symbols(self, _list):
        _new_list = []
        for i in _list:
            # 去掉前后空格
            i = i.strip()
            i = i.replace("？", "?")
            i = i.replace("。", ".")
            _new_list.append(i)
        return _new_list
