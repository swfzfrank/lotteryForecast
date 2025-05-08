import lotteryData
import pandas as pd
import wxPusher

def string_to_list(s):
    """
    将字符串形式的列表转换为Python列表。
    
    :param s: 输入的字符串，例如 '[6, 7, 8, 9, 10]' 或 '[19  4 32 14  7  2]'
    :return: 转换后的列表，例如 [6, 7, 8, 9, 10] 或 [19, 4, 32, 14, 7, 2]
    """
    # 去掉字符串两端的方括号
    s = s.strip('[]')
    
    # 检查是否包含逗号，如果有逗号则按逗号分割，否则按空格分割
    if ',' in s:
        # 按逗号分割并去除空格
        items = [int(item.strip()) for item in s.split(',')]
    else:
        # 按空格分割并去除空格
        items = [int(item.strip()) for item in s.split()]
    
    return items
def getPrize(blueResult, redResult, blue, red):
    redCnt = 0
    for i in range(6):
        if red[i] == redResult[i]:
            redCnt += 1
    blueFlag = True if blueResult in blue else False

    if blueFlag :
        if redCnt < 3:
            return 6
        elif redCnt == 3:
            return 5
        elif redCnt == 4:
            return 4
        elif redCnt == 5:
            return 3
        elif redCnt == 6:
            return 1
    elif redCnt == 4:
        return 5
    elif redCnt == 5:
        return 4
    elif redCnt == 6:
        return 2

    return 0


if __name__ == '__main__':
    latestData = lotteryData.get_history_ssq_data()
    
    # 修改：通过 iloc 获取最后一行数据，并提取 red 和 blue 列的值
    latestRed = string_to_list(latestData.iloc[0]['red'])
    latestBlue = int(latestData.iloc[0]['blue'])
    
    print(latestRed)
    print(latestBlue)

    df = pd.read_csv("lottery_predictions.csv")
    predictBlue = string_to_list(df.iloc[0]['Blue Balls'])
    predictRed = string_to_list(df.iloc[0]['Red Balls'])
    prize = getPrize(latestBlue, latestRed, predictBlue, predictRed)
    df.at[df.index[0], 'Prize'] = str(prize)
    df.to_csv("lottery_predictions.csv", index=False)

    code = latestData.iloc[0]['code']
    combinedInfo = f"预测蓝球: {predictBlue}  实际蓝球: {latestBlue}  \n预测红球: {predictRed}  实际红球: {latestRed}  \n实际中奖: {prize}等奖"
    print(combinedInfo)
    titleInfo = str(code) + "预测结果"
    wxPusher.send_wxpusher_message(combinedInfo, [40179], titleInfo)
