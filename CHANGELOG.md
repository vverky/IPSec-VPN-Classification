# Changelog

所有主要的项目更新都会记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/)，该项目遵循 [Semantic Versioning](https://semver.org/)。

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [1.0.0] - 2025-01-15

### Added
- 初始版本发布
- 三种应用协议分类支持（FTP、IM、Web）
- 基于Transformer的深度学习模型
- Web UI用户界面，支持PCAP文件上传
- 自动特征提取模块
- 模型训练脚本
- 流量预测功能
- CSV格式的结果导出
- 详细的API文档
- 单元测试套件

### Features

#### Feature Extraction
- 支持从PCAP和PCAPNG文件提取网络流量特征
- 自动提取统计特征（包长度、时间间隔等）
- 多种特征工程方法

#### Model Training
- 基于Keras/TensorFlow的Transformer模型
- 支持自定义训练参数
- 模型验证和评估功能
- 训练日志记录

#### Prediction
- 实时流量分类
- 批量PCAP文件处理
- 概率输出和置信度计算

#### Web Interface
- Flask应用框架
- 前端HTML/CSS/JS界面
- 文件上传处理
- 结果下载功能
- 错误处理和反馈

### Changed

### Fixed

### Security

---

## 版本号说明

主版本号.次版本号.修订号

- 主版本号：做了不兼容的API修改
- 次版本号：做了向下兼容的功能性新增
- 修订号：做了向下兼容的问题修正

## 开发计划

- [ ] v1.1.0：支持更多应用协议
- [ ] v1.2.0：模型轻量化和性能优化
- [ ] v1.3.0：实时流量监测功能
- [ ] v2.0.0：分布式处理支持
