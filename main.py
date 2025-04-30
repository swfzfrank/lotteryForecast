import lotteryData
import dataProcess
from blueNumberForecast import SequencePredictor
from blueTrendForecast import SequenceClassifier
import redNumberForecast
import wxPusher
import pandas as pd
from datetime import datetime
import os

def get_weekday():
    """
    返回今天是星期几，若是星期一则返回0，星期三返回1，星期六返回2。
    
    :return: 星期几对应的数字
    """
    from datetime import datetime
    
    # 获取今天的星期几，0表示星期一，6表示星期日
    today = datetime.today().weekday()
    
    # 根据星期几返回相应的数字
    if today == 1:  # 星期二
        return 0
    elif today == 3:  # 星期四
        return 1
    elif today == 6:  # 星期日
        return 2
    else:
        return None  # 其他情况返回None

day = get_weekday()
length = 20
blueTrendModel = SequenceClassifier(window_size=length)
blueNumberModel = SequencePredictor(input_length=length)
def predictBlueNumber():
    blue = dataProcess.sort_and_extract_blue(lotteryData.get_history_ssq_data())
    data = blue[day::3]

#----------------------------------
    trendData = dataProcess.compare_sequence(data)
    split_idx = int(len(trendData)*0.8)
    train_data = trendData[:split_idx]
    test_data = trendData[split_idx:]

    blueTrendModel.train(train_data)
    blueTrendModel.evaluate(test_data)

#----------------------------------
    split_idx = int(len(data)*0.8)
    train_data = data[:split_idx]
    test_data = data[split_idx:]

    blueNumberModel.train(train_data)
    blueNumberModel.evaluate(test_data)

#----------------------------------
    testNumber = data[-length:]  # 获取最后length个元素
    number = blueNumberModel.predict(testNumber)
    testTrend = trendData[-length:]
    trend = blueTrendModel.predict(testTrend)

    number = round(number)
    possibleNumbers = []
    trend_mapping = {
        0: [number-2, number-1, number, number+1, number+2],
        1: [number-1, number, number+1, number+2, number+3],
        -1: [number-3, number-2, number-1, number, number+1]
    }
    possibleNumbers.extend(trend_mapping.get(trend, number))

    return possibleNumbers

def predictRedNumber():
    red = dataProcess.sort_and_extract_red(lotteryData.get_history_ssq_data())
    data = red[day::3]
    redNumberForecast.trainRedNumberModel(data, length)

    testNumber = data[-length:]  # 获取最后length个元素
    return redNumberForecast.predictNextRedNumbers(testNumber)

if __name__ == "__main__":
    if lotteryData.get_history_ssq_data().empty:
        lotteryData.fetch_ssq_all_data()
    else:
        lotteryData.update_ssq_data()
    
    blueBalls = predictBlueNumber()
    redBalls = predictRedNumber()
    
    # 将 blueBalls 和 redBalls 拼接成一个字符串
    combined_balls = f"Blue Balls: {blueBalls} \n Red Balls: {redBalls}"
    print(combined_balls)
    
    wxPusher.send_wxpusher_message(combined_balls, [39909], "今日预测")
    
    # 新增：将预测结果保存到 DataFrame 中
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "Date": [today],
        "Blue Balls": [blueBalls],
        "Red Balls": [redBalls],
        "Prize": "",
    }
    df = pd.DataFrame(data)
    
    csv_file_path = "lottery_predictions.csv"
    if os.path.exists(csv_file_path):
        # 读取现有数据并合并
        existing_df = pd.read_csv(csv_file_path, index_col=0)
        combined_df = pd.concat([df, existing_df])  # 新数据在前
    else:
        combined_df = df

    # 覆盖写入完整数据
    combined_df.to_csv(csv_file_path, mode='w', header=True, index=True)
