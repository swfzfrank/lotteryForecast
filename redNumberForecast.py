import dataProcess
import pandas as pd  # 新增导入 pandas 库
import random

def sort_dict(dataDict, by='key', reverse=False):
    """
    对输入的字典进行排序，默认按照键进行升序排序。
    
    :param dataDict: 输入的字典
    :param by: 排序依据，'key' 或 'value'，默认为 'key'
    :param reverse: 是否降序排序，默认为 False
    :return: 排序后的字典
    """
    if by == 'key':
        sorted_dict = dict(sorted(dataDict.items(), key=lambda item: item[0], reverse=reverse))
    elif by == 'value':
        sorted_dict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=reverse))
    else:
        raise ValueError("参数 'by' 必须为 'key' 或 'value'")
    
    return sorted_dict

def getFutureRedNumbers(red):
    dataDict = dataProcess.count_number_occurrences(red)
    dataDict = sort_dict(dataDict, by='value', reverse=False)
    #获取0到4之间的随机数
    random_number = random.randint(0, 4)

    # 将字典转换为 DataFrame 并打印
    df = pd.DataFrame(list(dataDict.items()), columns=['Number', 'Count'])

    # 将df的key值，从random_number开始每隔5个数，放到result中，返回result
    result = df['Number'].iloc[random_number::5].tolist()
    return result[:6]  # 只返回前6个数

if __name__ == '__main__':
    import lotteryData
    red = dataProcess.sort_and_extract_red(lotteryData.get_history_ssq_data())
    data = red[::3]
    print(getFutureRedNumbers(data))