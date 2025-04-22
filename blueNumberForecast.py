import numpy as np
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import dataProcess
import lotteryData

class SequencePredictor:
    def __init__(self, input_length=20, verbose=True):
        self.input_length = input_length
        self.model = None
        self.best_params_ = None
        self.scaler = StandardScaler()
        self.verbose = verbose
        
        # 定义参数搜索空间
        self.param_grid = {
            'regressor__n_estimators': [50, 100, 200],
            'regressor__max_depth': [None, 10, 20],
            'regressor__min_samples_split': [2, 5],
            'regressor__max_features': ['sqrt', 'log2']
        }

    def _create_dataset(self, data):
        """将一维时间序列转换为监督学习格式"""
        X, y = [], []
        for i in range(len(data)-self.input_length):
            X.append(data[i:i+self.input_length])
            y.append(data[i+self.input_length])
        return np.array(X), np.array(y)

    def train(self, train_data):
        """
        训练模型
        :param train_data: 一维数组格式的时序数据
        """
        # 数据预处理
        train_data = np.array(train_data).flatten()
        X, y = self._create_dataset(train_data)
        
        # 创建管道
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(random_state=42))
        ])

        # 时间序列交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        
        # 网格搜索
        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=self.param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=self.verbose
        )
        
        grid_search.fit(X, y)
        
        # 保存最佳模型和参数
        self.model = grid_search.best_estimator_
        self.best_params_ = grid_search.best_params_
        
        if self.verbose:
            print("训练完成")
            print(f"最佳参数: {grid_search.best_params_}")
            print(f"最佳验证分数(MSE): {-grid_search.best_score_:.4f}")

    def predict(self, input_sequence):
        """
        进行预测
        :param input_sequence: 长度等于input_length的输入序列
        """
        if self.model is None:
            raise ValueError("请先训练模型")
            
        if len(input_sequence) != self.input_length:
            raise ValueError(f"输入序列长度必须为{self.input_length}")
            
        # 转换为二维数组格式
        input_array = np.array(input_sequence).reshape(1, -1)
        return self.model.predict(input_array)[0]

    def evaluate(self, test_data):
        """
        评估模型性能
        :param test_data: 一维数组格式的测试数据
        """
        X_test, y_test = self._create_dataset(test_data)
        y_pred = self.model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        print(f"评估结果:")
        print(f"MAE: {mae:.4f}")
        print(f"MSE: {mse:.4f}")
        print(f"RMSE: {rmse:.4f}")

# 示例用法
if __name__ == "__main__":
    data = dataProcess.sort_and_extract_blue(lotteryData.get_history_ssq_data())
    list1 = data[::3]
    
    # 划分训练集和测试集
    split_idx = int(len(list1)*0.8)
    train_data = list1[:split_idx]
    test_data = list1[split_idx:]
    
    paramterLength = 10
    # 初始化预测器
    predictor = SequencePredictor(input_length=paramterLength)
    
    # 训练模型
    predictor.train(train_data)
    
    # 评估模型
    predictor.evaluate(test_data)
    
    # 示例预测
    successCnt = 0
    for i in range(0, len(list1) - paramterLength):
        test_sequence = list1[i:paramterLength+i]
        prediction = predictor.predict(test_sequence)
        if (abs(prediction - list1[i+paramterLength]) <= 2):
            successCnt += 1
        print(f"第{i+1}步预测: {prediction:.4f} | 真实值: {list1[i+paramterLength]:.4f}")

    print(f"预测成功率: {successCnt/len(list1)*100}%")