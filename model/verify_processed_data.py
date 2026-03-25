import numpy as np

def verify_processed_data(file_path):
    print("正在验证数据集完整性...")
    data = np.load(file_path)

    # 验证数据完整性
    required_keys = ['X_train', 'X_test', 'y_train', 'y_test',
                    'x_mean', 'x_scale', 'y_mean', 'y_scale',
                    'feature_names', 'target_names']
    for key in required_keys:
        assert key in data, f"数据文件缺少关键字段 {key}！"

    # 验证特征维度
    feature_names = data['feature_names'].tolist()
    target_names = data['target_names'].tolist()

    # 验证输入特征数
    X_train = data['X_train']
    X_test = data['X_test']
    assert len(X_train.shape) == 3, "X_train 必须是三维数组！"
    assert len(X_test.shape) == 3, "X_test 必须是三维数组！"
    feat_dim = X_train.shape[2]  # 特征数在第三个维度
    assert feat_dim == len(feature_names), (
        f"特征列数 ({feat_dim}) 与 feature_names 长度 ({len(feature_names)}) 不匹配！"
    )

    # 验证目标维度
    y_train = data['y_train']
    y_test = data['y_test']
    assert y_train.shape[1] == len(target_names), (
        f"目标列数 ({y_train.shape[1]}) 与 target_names 长度 ({len(target_names)}) 不匹配！"
    )

    # 验证训练/测试集样本数一致性
    assert X_train.shape[0] == len(y_train), (
        f"训练集样本数不一致: X_train={X_train.shape[0]}, y_train={len(y_train)}"
    )
    assert X_test.shape[0] == len(y_test), (
        f"测试集样本数不一致: X_test={X_test.shape[0]}, y_test={len(y_test)}"
    )

    print("数据验证通过！")


# 使用示例
# verify_processed_data("processed_data.npz")