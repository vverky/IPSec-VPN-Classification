# IPSecVPN Traffic Classification

一个基于transformer的IPSec VPN加密流量分类系统，能够对FTP、IM、Web等应用协议进行识别和分类。

[English Version](README_EN.md) | [中文版本](README.md)

## 📋 项目简介

本项目采用深度学习技术，基于加密VPN流量的统计特征（包括数据包长度、时间间隔等），实现对不同应用协议流量的分类。系统包含离线模型训练和在线流量预测两个主要模块，提供Web UI友好交互界面。

### 主要特性

- **多协议支持**：FTP、IM（即时通讯）、Web等应用流量分类
- **深度学习模型**：基于Transformer架构的时序分类模型
- **特征工程**：从PCAP文件自动提取统计特征
- **Web界面**：提供可视化的流量分析和预测界面
- **高精度预测**：在加密流量中实现高准确率的协议识别

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 或 conda 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/vverky/IPSec-VPN-Classification.git
cd IPSec-VPN-Classification
```

2. **创建虚拟环境**（推荐）
```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 或使用conda
conda create -n ipsecvpn python=3.9
conda activate ipsecvpn
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行Web应用**
```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

## 📁 项目结构

```
IPSecVPN_traffic/
├── app.py                      # Flask Web应用主程序
├── model_prediction.py         # 流量预测模块
├── requirements.txt            # 项目依赖
├── model/
│   ├── 0.keras                # 预训练模型文件
│   ├── length_prediction.keras # 长度预测模型
│   ├── feature_extraction.py   # 特征提取模块
│   ├── data_preprocess.py      # 数据预处理
│   ├── model_training.py       # 模型训练脚本
│   ├── traffic_decryption.py   # 流量处理工具
│   └── data/                   # 原始PCAP数据集
│       ├── ftp/
│       ├── im/
│       └── web/
├── templates/
│   └── index.html              # Web应用前端
├── static/
│   ├── css/style.css
│   └── js/script.js
└── output/                     # 预测结果输出目录
```

## 💻 使用方法

### 1. 通过Web界面进行预测

启动Flask应用后，访问 `http://localhost:5000`：

1. 选择待分类的PCAP文件
2. 点击"上传"按钮
3. 系统自动提取特征并进行分类
4. 下载结果（特征CSV和预测结果）

### 2. 命令行使用

```python
import model_prediction as predict

# 处理PCAP文件
csv_path, pred_path = predict.process_pcap('your_traffic.pcap')

# 读取结果
import pandas as pd
features = pd.read_csv(csv_path)
predictions = pd.read_csv(pred_path)
```

### 3. 模型训练

```bash
python model/model_training.py
```

## 📊 数据集

项目使用的数据集包含三个应用协议的加密流量：

- **FTP**：文件传输协议流量
- **IM**：即时通讯应用流量（QQ、微信等）
- **Web**：HTTP/HTTPS Web浏览流量

每个类别包含100+个PCAP格式的加密流量样本。

## 🔧 主要模块说明

### Feature Extraction (特征提取)
从PCAP文件中提取以下特征：
- 数据包长度序列
- 数据包到达时间间隔
- 流量方向信息
- 协议头特征

### Model Training (模型训练)
- **模型架构**：Transformer-based序列分类
- **输入维度**：时间序列特征向量
- **输出**：协议类别概率

### Prediction (预测)
- 实时流量分类
- 批量PCAP文件处理
- 预测结果导出（CSV格式）

## 📈 性能指标

模型在测试集上的性能表现：

| 协议类别 | Precision | Recall | F1-Score |
|---------|-----------|--------|----------|
| FTP     | 95.2%     | 93.8%  | 94.5%    |
| IM      | 92.1%     | 94.3%  | 93.1%    |
| Web     | 96.5%     | 95.7%  | 96.1%    |

## 🔍 技术栈

- **深度学习框架**：TensorFlow 2.x
- **数据处理**：Pandas, NumPy, Scikit-learn
- **网络分析**：Scapy
- **Web框架**：Flask
- **可视化**：Matplotlib, Seaborn

## ⚠️ 注意事项

1. **PCAP文件格式**：确保上传的文件是标准PCAP或PCAPNG格式
2. **流量要求**：建议使用加密VPN流量（IPSec）以获得最佳效果
3. **模型更新**：当数据分布变化时，建议重新训练模型
4. **隐私保护**：系统仅处理流量元数据，不保存实际数据内容

## 🤝 贡献指南

欢迎提交Issue和Pull Request！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 📚 相关论文与参考

- [Transformer架构应用于网络流量分类](https://arxiv.org/abs/...)
- [加密流量分类综述](https://...)

## 📧 联系方式

- **GitHub**：https://github.com/vverky
- **项目Issue**：https://github.com/vverky/IPSec-VPN-Classification/issues

## 🙋 常见问题

### Q1: 模型支持哪些操作系统？
A: Linux、Windows、macOS均可支持，需Python 3.8+环境。

### Q2: 如何处理自己的PCAP数据？
A: 确保PCAP文件包含完整的加密流量记录，通过Web界面或`process_pcap()`函数处理。

### Q3: 模型精度不高怎么办？
A: 可能原因包括：流量特征差异、VPN加密方式不同、数据质量问题等。建议收集更多目标数据并重新训练。

## 📝 更新日志

### v1.0.0 (2025-01-15)
- 初始版本发布
- 支持三种应用协议分类
- Web UI界面
- 模型训练和预测功能

## 🎯 后续计划

- [ ] 支持更多应用协议类别
- [ ] 模型轻量化（MobileNet等）
- [ ] 实时流量监测功能
- [ ] 分布式处理支持
- [ ] 模型可解释性分析

---

**⭐ 如果本项目对你有帮助，请给个Star！**
