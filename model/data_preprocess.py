import os
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from verify_processed_data import verify_processed_data
import ast


def load_and_merge_data(base_path):
    """加载并合并数据，按时间排序"""
    print("\n[1/5] 开始加载数据...")
    start_time = time.time()

    categories = ['web', 'ftp', 'im']
    dfs = []
    total_files = 0
    total_records = 0

    for cat in categories:
        cat_path = os.path.join(base_path, cat)
        if not os.path.exists(cat_path):
            print(f" 警告：跳过不存在的目录 {cat_path}")
            continue

        files = [f for f in os.listdir(cat_path) if f.endswith('.csv')]
        if not files:
            print(f" 警告：目录 {cat_path} 中没有CSV文件")
            continue

        print(f" 正在处理类别 {cat.upper()}，发现 {len(files)} 个文件")

        for fname in files:
            try:
                file_path = os.path.join(cat_path, fname)
                df = pd.read_csv(
                    file_path,
                    sep='|',
                    quotechar='"',
                    engine='python'
                )
                dfs.append(df)
                total_files += 1
                total_records += len(df)
            except Exception as e:
                print(f"\n 错误：加载 {fname} 失败 - {str(e)}")
                continue
    # 合并多个dateframe
    merged_df = pd.concat(dfs, ignore_index=True).drop_duplicates()
    # 按时间戳排序并重置索引
    merged_df = merged_df.sort_values('timestamp').reset_index(drop=True)
    time_cost = time.time() - start_time
    print(f"\n 加载完成！共处理 {total_files} 个文件，总记录数：{total_records}")
    print(f" 数据加载耗时: {time_cost:.2f} 秒")
    return merged_df

def process_binary_features(df):
    """二进制特征处理"""
    # 定义字节解析函数
    def safe_parse(byte_str, expected_len):
        try:
            bytes_obj = ast.literal_eval(byte_str.decode('unicode_escape') if isinstance(byte_str, bytes) else byte_str)
            return list(bytes_obj.ljust(expected_len, b'\x00')[:expected_len])
        except:
            return [0] * expected_len

    # 并行处理IV特征
    iv_matrix = np.array(df['initialization_vector'].apply(lambda x: safe_parse(x, 16)).tolist(), dtype=np.uint8)
    for i in range(16):
        df[f'iv_byte_{i}'] = iv_matrix[:, i]

    # 并行处理ICV特征
    icv_matrix = np.array(df['integrity_check_value'].apply(lambda x: safe_parse(x, 12)).tolist(), dtype=np.uint8)
    for i in range(12):
        df[f'icv_byte_{i}'] = icv_matrix[:, i]

    # 移除原始列
    df = df.drop(['initialization_vector', 'integrity_check_value'], axis=1)
    return df


def enhance_time_features(df):
    """增强型时间特征工程"""
    # 转换为时间序列对象
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # 生成复合时间特征
    df['hour_sin'] = np.sin(2 * np.pi * df.timestamp.dt.hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df.timestamp.dt.hour / 24)
    df['week_sin'] = np.sin(2 * np.pi * df.timestamp.dt.isocalendar().week / 52)
    df['week_cos'] = np.cos(2 * np.pi * df.timestamp.dt.isocalendar().week / 52)
    # 清理中间列
    df = df.drop(['timestamp'], axis=1)
    return df

def create_time_series(X, y, seq_length):
    """将数据分割为时间序列窗口"""
    X_sequences = []
    y_sequences = []
    for i in range(len(X) - seq_length + 1):
        X_sequences.append(X[i:i + seq_length])
        y_sequences.append(y[i + seq_length - 1])  # 预测最后一个时间步的标签
    return np.array(X_sequences), np.array(y_sequences)

def standardize_data(df, output_path):
    """数据标准化"""
    print("\n[4/5] 数据标准化、持久化...")
    # 定义特征集和目标
    input_features = [
                         'spi', 'sequence_number', 'encrypted_head_length',
                         'encrypted_data_length', 'hour_sin', 'hour_cos',
                         'week_sin', 'week_cos'
                     ] + [f'iv_byte_{i}' for i in range(16)] + [f'icv_byte_{i}' for i in range(12)]
    output_features = [
        'plaintext_header_length',
        'padding_length'
    ]
    # 先分割后标准化
    X_raw = df[input_features].values
    y_raw = df[output_features].values

    # 保持时间顺序的分割（前80%训练，后20%测试）
    split_idx = int(len(X_raw) * 0.8)
    X_train_raw, X_test_raw = X_raw[:split_idx], X_raw[split_idx:]
    y_train_raw, y_test_raw = y_raw[:split_idx], y_raw[split_idx:]

    # 标准化处理（仅用训练数据拟合）
    x_scaler = StandardScaler()
    X_train = x_scaler.fit_transform(X_train_raw)
    X_test = x_scaler.transform(X_test_raw)  # 使用训练集的参数

    y_scaler = StandardScaler()
    y_train = y_scaler.fit_transform(y_train_raw)
    y_test = y_scaler.transform(y_test_raw)

    # 构造时间序列
    seq_length = 5
    X_train_seq, y_train_seq = create_time_series(X_train, y_train, seq_length)
    X_test_seq, y_test_seq = create_time_series(X_test, y_test, seq_length)

    # 持久化处理
    np.savez_compressed(
        os.path.join(output_path, 'processed_data.npz'),
        X_train=X_train_seq, X_test=X_test_seq,
        y_train=y_train_seq, y_test=y_test_seq,
        x_mean=x_scaler.mean_,
        x_scale=x_scaler.scale_,
        y_mean=y_scaler.mean_,
        y_scale=y_scaler.scale_,
        feature_names=input_features,
        target_names=output_features
    )
    print(f"处理完成，最终特征维度: {X_train_seq.shape[-1]} 输入特征")
    print(f"数据集分布: 训练集 {len(X_train_seq)} 条 | 测试集 {len(X_test_seq)} 条")

def main():
    input_path = './features'
    output_path = './'
    os.makedirs(output_path, exist_ok=True)

    # 加载并合并数据
    df = load_and_merge_data(input_path)

    # 特征处理流水线
    print("\n[2/5] 处理二进制特征...")
    start_time = time.time()
    df = process_binary_features(df)
    print(f"新增28个iv、icv字节级特征 | 耗时: {time.time() - start_time:.2f}s")
    print("\n[3/5] 时间特征增强...")
    start_time2 = time.time()
    df = enhance_time_features(df)
    print(f"新增4个时间特征 | 耗时: {time.time() - start_time2:.2f}s")
    standardize_data(df, output_path)
    print("\n[5/5] 验证数据完整性...")
    verify_processed_data("processed_data.npz")

if __name__ == "__main__":
    main()