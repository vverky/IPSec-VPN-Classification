import numpy as np
import pandas as pd
import time
from scapy.all import rdpcap, IP, ESP, Ether
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import os
import tempfile
import ast

# ------------------------- 配置参数 ---------------------------
PCAP_PATH = "test.pcap"  # 输入加密报文路径
MODEL_PATH = "model/length_prediction.keras"  # 模型文件路径
NPZ_PATH = "model/processed_data.npz"  # 预处理参数文件路径
OUTPUT_DIR = "./output"  # 输出文件目录
OUTPUT_PATH = "length_predictions.csv"  # 预测结果保存路径
SEQ_LENGTH = 5  # 序列长度

class ProtocolPositionEncoding(tf.keras.layers.Layer):
    """位置编码层（修复参数传递问题）"""
    def __init__(self, d_model, **kwargs):  # 添加**kwargs接收额外参数
        super().__init__(**kwargs)  # 将kwargs传递给父类
        self.d_model = d_model
        self.pos_encoding = self.positional_encoding(300, d_model)

    def positional_encoding(self, max_len, d_model):
        # 原有实现保持不变
        position = np.arange(max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = np.zeros((max_len, d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        return tf.cast(pe[np.newaxis, ...], tf.float32)

    def call(self, x):
        seq_len = tf.shape(x)[1]
        return x + self.pos_encoding[:, :seq_len, :]

    def get_config(self):  # 可选：显式保存d_model参数
        config = super().get_config()
        config.update({"d_model": self.d_model})
        return config

def extract_encrypted_features(pcap_path, output_dir=None):
    """从加密报文中提取特征并保存CSV"""
    # 创建临时目录（如果未指定输出目录）
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix="feature")
    os.makedirs(output_dir, exist_ok=True)
    pkts = rdpcap(pcap_path)
    data = []
    for pkt in pkts:
        try:
            if not (IP in pkt and ESP in pkt):
                continue
            # 数据链路层
            eth_layer = pkt.getlayer(Ether)
            data_len = len(eth_layer) if eth_layer else 0
            # IP层
            ip = pkt[IP]
            # ESP层
            esp = pkt[ESP]
            esp_data = bytes(esp.data)
            encrypted_data_length = len(esp_data)
            # 特征计算
            encrypted_head_length = data_len - encrypted_data_length
            iv = bytes(esp_data[:16])
            icv = bytes(esp_data[-12:])
            row = {
                "timestamp": pkt.time,
                "spi": esp.spi,
                "sequence_number": esp.seq,
                "encrypted_head_length": encrypted_head_length,
                "encrypted_data_length": encrypted_data_length,
                "initialization_vector": iv,
                "integrity_check_value": icv
            }
            data.append(row)
        except Exception as e:
            print(f"处理包失败：{str(e)}，跳过此包")
    df = pd.DataFrame(data)

    # ===== 保存原始特征文件 =====
    csv_filename = f"{PCAP_PATH}_features.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    df.to_csv(csv_path, index=False)
    return csv_path  # 返回文件路径而非DataFrame

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
def preprocess_features(csv_path):
    """从CSV文件加载并进行预处理"""
    # ================== 数据加载 ==================
    df = pd.read_csv(
        csv_path,
        quotechar='"',
        engine='python'
    )
    if df.empty:
        raise ValueError("未提取到有效特征，请检查PCAP文件")
    # 按时间戳排序并重置索引
    df = df.sort_values('timestamp').reset_index(drop=True)
    # 特征处理流水线
    df = process_binary_features(df)
    df = enhance_time_features(df)
    input_features = [
                         'spi', 'sequence_number', 'encrypted_head_length',
                         'encrypted_data_length', 'hour_sin', 'hour_cos',
                         'week_sin', 'week_cos'
                     ] + [f'iv_byte_{i}' for i in range(16)] + [f'icv_byte_{i}' for i in range(12)]
    return df[input_features]

def load_scalers(npz_path):
    """加载标准化参数"""
    data = np.load(npz_path)
    x_scaler = StandardScaler()
    x_scaler.mean_ = data["x_mean"]
    x_scaler.scale_ = data["x_scale"]
    y_scaler = StandardScaler()
    y_scaler.mean_ = data["y_mean"]
    y_scaler.scale_ = data["y_scale"]
    return x_scaler, y_scaler

def predict_sequence(model, x_sequence, y_scaler):
    """执行预测并逆标准化"""
    y_pred_scaled = model.predict(x_sequence, verbose=0)
    return y_scaler.inverse_transform(y_pred_scaled)
# 填充初始值
def pad_sequences(X, seq_length):
    """填充序列以保持输入输出长度一致"""
    # 前seq_length-1个样本用第一个样本重复填充
    pad = np.tile(X[0], (seq_length-1, 1))
    padded_X = np.vstack([pad, X])
    return padded_X

def process_pcap(pcap_path):
    """处理上传的pcap文件并返回结果文件路径"""
    # 1. 特征提取
    output_dir = os.path.join('output', os.path.splitext(os.path.basename(pcap_path))[0])
    os.makedirs(output_dir, exist_ok=True)

    csv_path = extract_encrypted_features(pcap_path, output_dir)

    # 2. 特征预处理
    processed_df = preprocess_features(csv_path)

    # 3. 加载预处理参数
    x_scaler, y_scaler = load_scalers(os.path.join('model', 'processed_data.npz'))

    # 4. 构建时间序列窗口
    X = x_scaler.transform(processed_df.values)
    # 填充序列（保持原始数据量）
    X_padded = pad_sequences(X, SEQ_LENGTH)
    sequences = []
    for i in range(len(X_padded) - SEQ_LENGTH + 1):
        sequences.append(X_padded[i:i + SEQ_LENGTH])
    sequences = np.array(sequences, dtype=np.float32)

    if len(sequences) == 0:
        raise ValueError(f"至少需要 {SEQ_LENGTH} 个包构成时间窗口")

    # 5. 加载模型并预测
    model = tf.keras.models.load_model(
        os.path.join('model', 'length_prediction.keras'),
        compile=False,
        custom_objects={"ProtocolPositionEncoding": ProtocolPositionEncoding}
    )
    predictions = predict_sequence(model, sequences, y_scaler)

    # 6. 保存结果
    pred_df = pd.DataFrame(predictions, columns=[
        "plaintext_header_length",
        "padding_length"
    ])
    pred_path = os.path.join(output_dir, "length_predictions.csv")
    pred_df.to_csv(pred_path, index=False)

    return csv_path, pred_path
