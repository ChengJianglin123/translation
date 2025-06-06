import pandas as pd
import csv


# 从 csv 文件中获取 cn_list 和 en_list 数据
def get_data_from_csv(data_path, raw_data_name):
    """
    :param data_path: 需要翻译的文件路径
    :param raw_data_name: 需要翻译的文件名称
    :return:  获取到的dict的结果数据
    """
    cn_list = []
    en_list = []
    data_path = f"{data_path}{raw_data_name}"
    with open(data_path, 'r') as file:
        # 读取到了全部原始数据
        reader = csv.reader(file)
        a = 0
        for row in reader:
            if a > 0:
                csv_en = row[0].strip()
                csv_cn = row[1].strip()
                en_list.append(csv_en)
                cn_list.append(csv_cn)
            a = a + 1
    # 将 中英文 也按 pandas 格式进行整理
    pd_result_data = {"en_英语": en_list, "zh-CN_中文": cn_list}
    return pd_result_data


def write_pd_data_to_csv_file(data_path, raw_data_name, pd_result_data):
    """
    :param pd_result_data: 写入的 pd 数据集
    :param data_path: 需要翻译的文件路径
    :param raw_data_name: 需要翻译的文件名称
    """
    # 创建一个包含所有翻译数据的 pandas 库的 dataframe 数据
    df = pd.DataFrame(data=pd_result_data)
    # 利用 pd 库将组装好的数据写入 csv 文件中
    df.to_csv(f"{data_path}{raw_data_name}", index=False)


