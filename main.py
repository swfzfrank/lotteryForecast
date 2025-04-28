import lotteryData
import dataProcess
from blueNumberForecast import SequencePredictor
from blueTrendForecast import SequenceClassifier
import redNumberForecast
import wxPusher

APP_TOKEN = "AT_PWwDFvgL1pymLhqCtuZfmLoPzKZgPOf1"  # 双色球专用 APP_TOKEN
USER_UIDS = ["UID_wKraNNh5OPgSq2kP0neChHsNC3Sd"]
def get_weekday():
    """
    返回今天是星期几，若是星期一则返回0，星期三返回1，星期六返回2。
    
    :return: 星期几对应的数字
    """
    from datetime import datetime
    
    # 获取今天的星期几，0表示星期一，6表示星期日
    today = datetime.today().weekday()
    
    # 根据星期几返回相应的数字
    if today == 0:  # 星期一
        return 0
    elif today == 2:  # 星期三
        return 1
    elif today == 4:  # 星期五
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
    
    wxPusher.send_wxpusher_message(combined_balls, USER_UIDS, APP_TOKEN, [39909], "今日预测")