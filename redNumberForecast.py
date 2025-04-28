import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Masking
from tensorflow.keras.optimizers import Adam
import dataProcess
import lotteryData

SEQUENCE_LENGTH = 20
VECTOR_DIM = 6
NUM_CLASSES = 33
NUM_PREDICT = 6
RED_MODEL = None
allRedData = dataProcess.sort_and_extract_red(lotteryData.get_history_ssq_data())

def create_dataset(redData):
    """创建训练数据集"""
    X = []
    y = []
    
    for i in range(len(redData) - SEQUENCE_LENGTH):
        sequence = [redData[i+j] for j in range(SEQUENCE_LENGTH)]
        target = redData[i+SEQUENCE_LENGTH]
        
        X.append(sequence)
        y.append(target)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)
def preprocess_data(y, num_classes=33):
    """将输出转换为多标签格式"""
    multi_label = np.zeros((len(y), num_classes), dtype=np.float32)
    for i, sample in enumerate(y):
        indices = sample - 1  # 将1-33转换为0-32
        multi_label[i, indices] = 1.0
    return multi_label

# 自定义评估函数
def custom_accuracy(y_true, y_pred):
    """至少匹配3个数字的准确率"""
    correct = 0
    for true_vec, pred_vec in zip(y_true, y_pred):
        # 取预测概率最高的6个不重复数字
        pred_numbers = np.argsort(pred_vec)[-NUM_PREDICT:] + 1
        true_numbers = np.where(true_vec == 1)[0] + 1
        matches = len(set(pred_numbers) & set(true_numbers))
        if matches >= 3:
            correct += 1
    return correct / len(y_true)

def trainRedNumberModel(redData, length):
    global RED_MODEL  # 声明 RED_MODEL 为全局变量
    SEQUENCE_LENGTH = length
    # 生成数据
    X, y = create_dataset(redData)
    y_multi = preprocess_data(y)

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X/33.0, y_multi, test_size=0.2)

    # 构建模型
    RED_MODEL = Sequential([
        Masking(mask_value=0.0, input_shape=(SEQUENCE_LENGTH, VECTOR_DIM)),
        LSTM(128, return_sequences=True),
        LSTM(64),
        Dense(64, activation='relu'),
        Dense(NUM_CLASSES, activation='sigmoid')
    ])

    RED_MODEL.compile(optimizer=Adam(0.001),
                loss='binary_crossentropy',
                metrics=['accuracy'])

    # 训练模型
    history = RED_MODEL.fit(X_train, y_train,
                        epochs=30,
                        batch_size=64,
                        validation_split=0.2)
    
    # 测试评估
    y_pred = RED_MODEL.predict(X_test)
    print(f"Custom Accuracy: {custom_accuracy(y_test, y_pred):.2%}")

def predictNextRedNumbers(redData):
    global RED_MODEL  # 声明 RED_MODEL 为全局变量
    new_sequence = np.array(redData)/33.0
    prediction = RED_MODEL.predict(np.array([new_sequence]))
    predicted_numbers = np.argsort(prediction[0])[-6:] + 1

    return predicted_numbers

if __name__ == '__main__':
    print("RedNumberForecast")