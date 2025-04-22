import numpy as np
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

class SequenceClassifier:
    def __init__(self, window_size=20, verbose=True):
        self.window_size = window_size
        self.model = None
        self.classes_ = [-1, 0, 1]
        self.best_params_ = None
        self.verbose = verbose
        
        # 定义参数搜索空间
        self.param_grid = {
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [None, 10, 20],
            'classifier__min_samples_split': [2, 5],
            'classifier__class_weight': [None, 'balanced']
        }

    def _create_dataset(self, data):
        """将序列转换为监督学习格式"""
        X, y = [], []
        for i in range(len(data)-self.window_size):
            X.append(data[i:i+self.window_size])
            y.append(data[i+self.window_size])
        return np.array(X), np.array(y)

    def train(self, train_data):
        """
        训练分类模型
        :param train_data: 包含-1, 0, 1的一维序列
        """
        # 验证输入数据
        unique_values = set(train_data)
        if not unique_values.issubset({-1, 0, 1}):
            raise ValueError("输入数据只能包含-1, 0, 1")
            
        X, y = self._create_dataset(train_data)
        
        # 创建分类管道
        pipeline = Pipeline([
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        # 时间序列交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        
        # 网格搜索
        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=self.param_grid,
            cv=tscv,
            scoring='accuracy',
            n_jobs=-1,
            verbose=self.verbose
        )
        
        grid_search.fit(X, y)
        
        # 保存最佳模型
        self.model = grid_search.best_estimator_
        self.best_params_ = grid_search.best_params_
        
        if self.verbose:
            print("训练完成")
            print(f"最佳参数: {grid_search.best_params_}")
            print(f"最佳验证准确率: {grid_search.best_score_:.4f}")

    def predict(self, input_sequence):
        """
        预测下一个值
        :param input_sequence: 长度等于window_size的输入序列
        """
        if self.model is None:
            raise ValueError("请先训练模型")
            
        if len(input_sequence) != self.window_size:
            raise ValueError(f"输入序列长度必须为{self.window_size}")
            
        input_array = np.array(input_sequence).reshape(1, -1)
        return self.model.predict(input_array)[0]

    def evaluate(self, test_data):
        """
        完整评估模型性能
        :param test_data: 包含-1, 0, 1的一维测试序列
        """
        X_test, y_test = self._create_dataset(test_data)
        y_pred = self.model.predict(X_test)
        
        # 计算各项指标
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n测试集准确率: {accuracy:.4f}")
        print("\n分类报告:")
        print(classification_report(y_test, y_pred, target_names=['-1', '0', '1']))
        
        print("\n混淆矩阵:")
        print(confusion_matrix(y_test, y_pred))

    def predict_next_n(self, input_sequence, n=3):
        """
        递归预测后续多个值
        :param input_sequence: 初始输入序列
        :param n: 需要预测的后续值数量
        """
        predictions = []
        current_seq = np.array(input_sequence.copy())
        
        for _ in range(n):
            next_val = self.predict(current_seq[-self.window_size:])
            predictions.append(next_val)
            current_seq = np.append(current_seq, next_val)
            
        return predictions

# 示例用法
if __name__ == "__main__":
    # 生成数据
    import lotteryData
    import dataProcess
    blue = dataProcess.sort_and_extract_blue(lotteryData.get_history_ssq_data())
    data = dataProcess.compare_sequence(blue)
    
    # 划分训练集和测试集
    split_idx = int(len(data)*0.8)
    train_data = data[:split_idx]
    test_data = data[split_idx:]
    
    windowSize = 5
    # 初始化分类器
    classifier = SequenceClassifier(window_size=windowSize)
    
    # 训练模型
    classifier.train(train_data)
    
    # 评估模型
    classifier.evaluate(test_data)
    
    # 示例预测
    test_sequence = test_data[:windowSize]
    print("\n初始输入序列:", test_sequence)
    
    # 预测下一个值
    next_val = classifier.predict(test_sequence)
    print(f"\n下一个值预测: {next_val} | 真实值: {test_data[windowSize]}")
    
    # 预测后续三个值
    predictions = classifier.predict_next_n(test_sequence, n=3)
    print("\n后续三个值预测:")
    for i, pred in enumerate(predictions, 1):
        print(f"第{i}步预测: {pred} | 真实值: {test_data[windowSize+i]}")