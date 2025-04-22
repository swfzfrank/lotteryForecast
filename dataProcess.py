def sort_and_extract_red(df):
    """
    将DataFrame按照code列的值由小到大排序，然后提取red列的数据并返回为list类型。
    
    :param df: 输入的DataFrame
    :return: 排序后的red列数据，类型为list
    """
    # 按照code列的值由小到大排序
    df_sorted = df.sort_values(by='code')
    # 提取red列的数据并转换为list
    red_list = df_sorted['red'].tolist()
    # 将字符串转换为队列形式
    red_list = [list(map(int, red.split(','))) for red in red_list]
    return red_list

def sort_and_extract_blue(df):
    """
    将DataFrame按照code列的值由小到大排序，然后提取blue列的数据并返回为list类型。
    
    :param df: 输入的DataFrame
    :return: 排序后的blue列数据，类型为list
    """
    # 按照code列的值由小到大排序
    df_sorted = df.sort_values(by='code')
    # 提取blue列的数据并转换为list
    blue_list = df_sorted['blue'].tolist()
    return blue_list

def count_blue_by_week(df):
    """
    统计每种week值下blue数据出现的次数
    :param df: DataFrame类型，包含blue和week列
    :return: 统计结果表格
    """
    # 提取blue和week列
    df_subset = df[['blue', 'week']]
    
    # 统计每种week值下blue数据出现的次数
    result = df_subset.groupby(['week', 'blue']).size().unstack(fill_value=0)
    
    # 打印统计结果
    print(result)
    return result

def sliding_window_sum(window_size, data_list):
    """
    对输入的数据列表进行滑窗操作，计算每个窗口内的数据和，返回这些和组成的列表。
    
    :param window_size: 窗口长度
    :param data_list: 输入的数据列表
    :return: 每个窗口内的数据和组成的列表
    """
    if window_size <= 0 or window_size > len(data_list):
        raise ValueError("窗口长度必须大于0且小于等于数据列表的长度")
    
    window_sums = []
    for i in range(len(data_list) - window_size + 1):
        window = data_list[i:i + window_size]
        window_sum = sum(window)
        window_sums.append(window_sum)
    
    return window_sums

def calculate_std_dev(data_list):
    """
    计算输入数列的标准差。
    
    :param data_list: 输入的数据列表
    :return: 标准差
    """
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    mean = sum(data_list) / len(data_list)
    variance = sum((x - mean) ** 2 for x in data_list) / len(data_list)
    std_dev = variance ** 0.5
    return std_dev

def compare_sequence(data_list):
    """
    比较数列中相邻两个数的大小关系，输出一个数列。
    如果前一个数比后一个数小，则输出1；一样大则输出0，前一个比后一个大则为-1。输出的数列第一个数为0。
    
    :param data_list: 输入的数据列表
    :return: 比较结果列表
    """
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    result = [0]  # 第一个数为0
    for i in range(1, len(data_list)):
        if data_list[i-1] < data_list[i]:
            result.append(1)
        elif data_list[i-1] == data_list[i]:
            result.append(0)
        else:
            result.append(-1)
    return result

def compare_red_lists(list1, list2):
    """
    比较两个长度为6的列表，如果重复的元素个数超过3，则返回True，否则返回False。
    
    :param list1: 第一个列表，长度必须为6
    :param list2: 第二个列表，长度必须为6
    :return: 如果重复元素个数超过3，返回True，否则返回False
    """
    if len(list1) != 6 or len(list2) != 6:
        raise ValueError("两个列表的长度必须为6")
    
    # 计算两个列表的交集长度
    common_elements = set(list1).intersection(set(list2))
    return len(common_elements) > 3

def count_number_occurrences(data_list):
    """
    统计输入列表中所有数字的出现次数，并确保返回的字典包含1到33的所有键，即使某些键对应的值为0。
    
    :param data_list: 输入的列表，每个元素都是列表类型的数列
    :return: 一个字典，表示每个数字及其出现的次数
    """
    from collections import defaultdict

    # 初始化一个默认字典，用于统计数字出现次数
    number_counts = defaultdict(int)
    
    # 遍历每个子列表
    for sublist in data_list:
        # 遍历子列表中的每个数字
        for number in sublist:
            number_counts[number] += 1
    
    # 确保字典包含1到33的所有键，即使某些键对应的值为0
    for number in range(1, 34):
        if number not in number_counts:
            number_counts[number] = 0
    
    return dict(number_counts)

if __name__ == "__main__":
    import lotteryData
    print(sort_and_extract_red(lotteryData.get_history_ssq_data()))

    count_blue_by_week(lotteryData.get_history_ssq_data())
    stdDevMin = 10000
    minStdDevWindow = 0
    for i in range(5, 100):
        blueSum = sliding_window_sum(i, sort_and_extract_blue(lotteryData.get_history_ssq_data()))
        std_dev = calculate_std_dev(blueSum)
        stdDevMin = min(stdDevMin, std_dev)
        if stdDevMin == std_dev:
            minStdDevWindow = i
    
    print("最小标准差为：", stdDevMin)
    print("最小标准差对应的窗口长度为：", minStdDevWindow)
