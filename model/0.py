import logging
import tensorflow as tf
from tensorflow.keras.callbacks import Callback
import math
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, Dropout, \
    GlobalAveragePooling1D, GaussianNoise
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger

class ProtocolPositionEncoding(tf.keras.layers.Layer):
    """位置编码层"""
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        self.pos_encoding = self.positional_encoding(300, d_model)  # 缩短最大序列长度
    def positional_encoding(self, max_len, d_model):
        position = np.arange(max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = np.zeros((max_len, d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        return tf.cast(pe[np.newaxis, ...], tf.float32)

    def call(self, x):
        seq_len = tf.shape(x)[1]
        return x + self.pos_encoding[:, :seq_len, :]

class DynamicCosineAnnealing(tf.keras.callbacks.Callback):
    def __init__(self, initial_lr, first_decay_steps, t_mul=2.0, m_mul=0.75,
                 min_lr=1e-7, patience=3, factor=0.8, metric_name='val_rmse'):
        super().__init__()
        # 基础参数配置
        self.base_lr = initial_lr
        self.first_decay_steps = first_decay_steps
        self.t_mul = t_mul
        self.m_mul = m_mul
        self.min_lr = min_lr

        # 平台检测参数
        self.best_metric = float('inf')
        self.patience = patience
        self.patience_counter = 0
        self.factor = factor
        self.metric_name = metric_name

        # 训练状态跟踪
        self.current_step = 0

    def on_train_begin(self, logs=None):
        self._reset_training_state()
        # 显式将学习率转换为tf.Variable
        if not hasattr(self.model.optimizer, 'built') or not self.model.optimizer.built:
            self.model.optimizer.build(self.model.trainable_variables)

    def _reset_training_state(self):
        """重置训练状态参数"""
        self.current_step = 0
        self.best_metric = float('inf')
        self.patience_counter = 0

    def on_train_batch_begin(self, batch, logs=None):
        """执行余弦退火学习率更新"""
        # 计算当前周期
        cycle, progress = self._compute_cycle_progress()

        # 计算衰减系数
        decay_coeff = (self.m_mul ** cycle) * 0.5 * (1 + math.cos(math.pi * progress))

        # 计算当前学习率
        current_lr = self.base_lr * decay_coeff
        current_lr = max(current_lr, self.min_lr)

        # 更新优化器学习率
        self.model.optimizer.learning_rate.assign(current_lr)
        self.current_step += 1

    def _compute_cycle_progress(self):
        """计算当前周期和进度"""
        cumulative_steps = 0
        cycle = 0
        current_step_size = self.first_decay_steps

        while cumulative_steps + current_step_size <= self.current_step:
            cumulative_steps += current_step_size
            cycle += 1
            current_step_size = int(current_step_size * self.t_mul)

        # 计算当前周期内的进度
        progress = (self.current_step - cumulative_steps) / current_step_size
        return cycle, max(0.0, min(1.0, progress))  # 确保进度在0-1之间

    def on_epoch_end(self, epoch, logs=None):
        """执行平台检测学习率调整"""
        current_metric = logs.get(self.metric_name)
        if current_metric is None:
            return

        if current_metric < self.best_metric:
            self.best_metric = current_metric
            self.patience_counter = 0
        else:
            self.patience_counter += 1
            if self.patience_counter >= self.patience:
                new_lr = max(self.base_lr * self.factor, self.min_lr)
                if new_lr < self.base_lr:
                    print(f"\nEpoch {epoch + 1}: 检测到平台期，调整基础学习率 {self.base_lr:.2e} -> {new_lr:.2e}")
                    self.base_lr = new_lr
                    self.patience_counter = 0

class LoggingCallback(Callback):
    """日志记录回调"""
    def __init__(self, log_path='training.log'):
        super().__init__()
        self.log_path = log_path
        self._setup_logger()
        self.safe_float = lambda x: float(x) if x is not None else 0.0

    def _setup_logger(self):
        self.logger = logging.getLogger('TrainingLogger')
        self.logger.setLevel(logging.INFO)

        # 防止重复添加handler
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        train_loss = self.safe_float(logs.get('loss', 0.0))
        train_mae = self.safe_float(logs.get('mae', 0.0))
        train_rmse = self.safe_float(logs.get('rmse', 0.0))
        val_loss = self.safe_float(logs.get('val_loss', 0.0))
        val_mae = self.safe_float(logs.get('val_mae', 0.0))
        val_rmse = self.safe_float(logs.get('val_rmse', 0.0))
        try:
            log_msg = (
                f"Epoch {epoch + 1:03d} | "
                f"Train: loss={train_loss:.4f}, mae={train_mae:.4f}, rmse={train_rmse:.4f} | "
                f"Val: loss={val_loss:.4f}, mae={val_mae:.4f}, rmse={val_rmse:.4f}"
            )
        except Exception as e:
            log_msg = f"Epoch {epoch + 1:03d} | 日志格式错误: {str(e)}"
        self.logger.info(log_msg)

def visualize_training(history, save_path=None):
    plt.figure(figsize=(18, 12))
    metrics = ['loss', 'mae', 'rmse']

    # 样式配置
    style_config = {
        'train_color': '#2A5CAA',  # 深蓝
        'val_color': '#D43A2F',  # 红色
        'smooth_color': '#FF9800',  # 橙色
        'best_marker': 'D',  # 菱形标记
        'annotation_size': 10,
        'grid_alpha': 0.2,
        'line_styles': ['--', '-']  # 原始/平滑线型
    }
    ax_main = [plt.subplot2grid((3, 3), (0, i), rowspan=2) for i in range(3)]
    # 动态平滑窗口算法
    def adaptive_smoothing(data, window=3):
        return [
            np.average(
                data[max(0, i - window):min(len(data), i + window + 1)],
                weights=np.hamming(  # 动态生成对应窗口长度的权重
                    min(i + window + 1, len(data)) - max(0, i - window)
                ),
                axis=0  # 显式指定计算轴
            )
            for i in range(len(data))
        ]

    for i, metric in enumerate(metrics):
        ax = ax_main[i]

        # 获取数据（兼容不同记录方式）
        train_vals = history.history.get(metric, [])
        val_vals = history.history.get(f'val_{metric}', [])
        epochs = range(1, len(train_vals) + 1)

        if not train_vals:
            print(f"[Warning] Missing {metric} data in history")
            continue

        # 智能平滑处理
        window_size = max(3, int(len(epochs) * 0.15))
        train_smooth = adaptive_smoothing(train_vals, window=window_size)
        val_smooth = adaptive_smoothing(val_vals, window=window_size)

        # 绘制轨迹
        ax.plot(epochs, train_vals, style_config['train_color'],
                alpha=0.2, linestyle=style_config['line_styles'][0])
        ax.plot(epochs, val_vals, style_config['val_color'],
                alpha=0.2, linestyle=style_config['line_styles'][0])
        ax.plot(epochs, train_smooth, style_config['train_color'],
                linewidth=2, label='Train')
        ax.plot(epochs, val_smooth, style_config['val_color'],
                linewidth=2, label='Validation')

        # 最佳点标注
        if val_vals:
            best_epoch = np.argmin(val_vals) + 1
            best_value = np.min(val_vals)
            ax.scatter(best_epoch, best_value, s=100,
                       marker=style_config['best_marker'],
                       edgecolors='black', facecolors=style_config['val_color'])
            ax.annotate(f'Epoch {best_epoch}\n{best_value:.4f}',
                        (best_epoch, best_value),
                        textcoords="offset points",
                        xytext=(10, -10),
                        fontsize=style_config['annotation_size'])

        # 动态刻度调整
        data_min = min(np.min(train_vals), np.min(val_vals)) * 0.98
        data_max = max(np.max(train_vals), np.max(val_vals)) * 1.02
        ax.set_ylim(data_min, data_max)

        if (data_max - data_min) < 0.1:
            ax.yaxis.set_major_locator(plt.MultipleLocator(0.01))
        else:
            ax.yaxis.set_major_locator(plt.AutoLocator())

        ax.set_title(metric.upper() + ' Evolution', fontsize=12)
        ax.grid(alpha=style_config['grid_alpha'])
        ax.legend()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"可视化结果已保存至：{save_path}")

    plt.show()

def build_transformer_model(input_shape):
    """Transformer模型"""
    inputs = Input(shape=input_shape)

    # 输入增强
    x = GaussianNoise(0.01)(inputs)
    # 特征嵌入
    x = Dense(48, kernel_initializer='he_normal',
              kernel_regularizer=tf.keras.regularizers.l1_l2(2e-5, 5e-4))(x)
    x = LayerNormalization(epsilon=1e-6)(x)
    x = ProtocolPositionEncoding(d_model=48)(x)
    x = Dropout(0.3)(x)

    # Transformer架构
    for _ in range(3):
        # 注意力机制
        attn = MultiHeadAttention(
            num_heads=4,  # 多头注意力
            key_dim=16,
            dropout=0.3  # 增加注意力层Dropout
        )(x, x)
        x = LayerNormalization(epsilon=1e-6)(x + attn)
        x = Dropout(0.3)(x)  # 增加后置Dropout

        # 前馈神经网络
        ffn = Dense(128, activation='gelu',
                    kernel_regularizer=tf.keras.regularizers.l2(2e-4))(x)
        ffn = Dropout(0.3)(ffn)
        ffn = Dense(48)(ffn)
        x = LayerNormalization(epsilon=1e-6)(x + ffn)
        x = Dropout(0.3)(x)

    # 输出层（增强正则化）
    x = GlobalAveragePooling1D()(x)
    x = Dense(96, activation='gelu',
              kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    x = Dropout(0.3)(x)
    outputs = Dense(2, activation='linear')(x)
    return Model(inputs=inputs, outputs=outputs)

def main():
    # 加载预处理数据
    data = np.load('./processed_data.npz')
    X_train, X_test = data['X_train'].astype(np.float32), data['X_test'].astype(np.float32)
    y_train, y_test = data['y_train'].astype(np.float32), data['y_test'].astype(np.float32)
    # 动态获取输入形状
    input_shape = (X_train.shape[1], X_train.shape[2])
    model = build_transformer_model(input_shape=input_shape)

    # 保守学习率调度
    initial_lr = 3e-5
    batch_size = 1024
    total_epochs = 80

    # 定义优化器（强正则化）
    optimizer = tf.keras.optimizers.Nadam(
        learning_rate=initial_lr,
        weight_decay=5e-5,  # 适度降低权重衰减
        global_clipnorm=1.0,
        ema_momentum=0.99  # 添加EMA平滑
    )

    # 加权组合损失函数
    def adaptive_huber(y_true, y_pred):
        delta = 0.8  # 固定delta参数
        residual = tf.abs(y_true - y_pred)
        loss = tf.where(
            residual < delta,
            0.5 * tf.square(residual),
            delta * (residual - 0.5 * delta)
        )
        return 0.5 * tf.reduce_mean(loss) + 0.5 * tf.reduce_mean(residual)  # 结合MAE

    model.compile(
        optimizer=optimizer,
        loss=adaptive_huber,
        metrics=['mae', tf.keras.metrics.RootMeanSquaredError(name='rmse')]
    )

    # 修复后的数据增强函数（类型一致性处理）
    def time_series_augment(inputs, labels, mask_prob=0.2, noise_std=0.08):
        # 显式转换输入类型
        inputs = tf.cast(inputs, tf.float32)

        # 随机遮蔽部分时间步（使用参数 mask_prob）
        mask = tf.random.uniform(tf.shape(inputs), dtype=tf.float32) < mask_prob
        inputs = tf.where(mask,
                          tf.zeros_like(inputs),  # 使用zeros_like确保类型一致
                          inputs)
        # 添加抖动（使用参数 noise_std）
        noise = tf.random.normal(
            tf.shape(inputs),
            mean=0.0,
            stddev=noise_std,
            dtype=tf.float32
        )
        return inputs + noise, labels

    # 构建数据管道
    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    train_dataset = train_dataset.shuffle(100000)
    train_dataset = train_dataset.batch(batch_size)
    train_dataset = train_dataset.map(lambda x, y: time_series_augment(x, y, mask_prob=0.2, noise_std=0.05),num_parallel_calls=tf.data.AUTOTUNE)
    train_dataset = train_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    # 修改验证数据管道
    val_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))
    val_dataset = val_dataset.batch(batch_size)

    # 回调策略
    callbacks = [
        DynamicCosineAnnealing(
            initial_lr=initial_lr,
            first_decay_steps=3000,
            t_mul=1.5,
            m_mul=0.85,
            min_lr=1e-6,
         ),
        CSVLogger('./training_logs/training.csv'),
        LoggingCallback('./training_logs/training.log'),
        EarlyStopping(
            monitor='val_rmse',
            patience=8,
            min_delta=0.001,
            mode='min',
            restore_best_weights=True,
        ),
        ModelCheckpoint(
            'length_prediction.keras',
            monitor='val_rmse',
            save_best_only=True,
            mode='min'
        ),
    ]

    # 执行训练
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    history = model.fit(
        train_dataset,  # 使用增强后的数据集
        epochs=total_epochs,
        validation_data=val_dataset,
        callbacks=callbacks,
        verbose=1
    )

    # 生成可视化报告
    visualize_training(
        history,
        save_path='./training_logs/metrics_visualization.png'
    )

if __name__ == "__main__":
    main()