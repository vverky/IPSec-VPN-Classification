# 贡献指南

感谢你对IPSecVPN Traffic Classification项目的关注！本指南将帮助你了解如何为项目做出贡献。

## 📖 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交改进](#提交改进)
- [代码风格指南](#代码风格指南)
- [提交流程](#提交流程)
- [开发环境设置](#开发环境设置)

## 行为准则

### 我们的承诺

为了营造开放和欢迎的社区环境，我们承诺：

- 尊重所有社区成员
- 接受不同的观点和经验
- 给予建设性的反馈
- 关注对社区最有利的事情
- 表现出同情和尊重

### 禁止行为

不可接受的行为包括：

- 骚扰和辱骂性语言
- 人身攻击或广告宣传
- 发布他人隐私信息
- 在线骚扰或跟踪
- 其他可能在职业环境中被认为不合适的行为

## 如何贡献

### 我可以贡献什么？

#### 🐛 报告和修复Bug
- 发现并报告软件问题
- 提交包含修复的Pull Request

#### ✨ 功能建议
- 建议新功能或改进
- 帮助实现社区建议的功能

#### 📚 文档改进
- 改进README、Wiki或代码注释
- 添加使用示例或教程

#### 🧪 代码审审和测试
- 审查Pull Request
- 测试新功能并报告问题

#### 🌐 翻译
- 将文档翻译成其他语言

## 报告问题

### 提交Bug报告前

在提交Bug报告之前，请：

1. **检查问题列表**：确保该问题尚未被报告
2. **收集信息**：
   - 操作系统和Python版本
   - 详细的错误信息
   - 复现步骤
   - 预期行为与实际行为

### 提交Bug报告

使用下面的模板提交Issue：

```markdown
**描述**
清晰简洁地描述问题

**复现步骤**
1. ...
2. ...
3. ...

**预期行为**
应该发生什么

**实际行为**
实际发生了什么

**环境信息**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python: [e.g. 3.8.10]
- TensorFlow: [e.g. 2.10.0]

**错误日志**
```
粘贴完整的错误追踪信息
```

**其他上下文**
任何其他相关信息
```

## 提交改进

### 功能建议

在建议功能前，请考虑：

- 是否符合项目的范围和目标？
- 实现的复杂度如何？
- 是否对大多数用户有用？

使用下面的模板提交功能建议：

```markdown
**建议的功能**
清晰描述你想要添加的功能

**为什么需要这个功能？**
解释使用场景和好处

**可能的实现方式**
如果有想法，描述可能的实现方式

**相关Issue或PR**
链接相关的Issue或PR
```

## 代码风格指南

### Python代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南：

```python
# ✅ 好的例子
def extract_features(pcap_file, sequence_length=5):
    """提取PCAP文件的特征向量。
    
    Args:
        pcap_file (str): PCAP文件路径
        sequence_length (int): 序列长度，默认为5
        
    Returns:
        np.ndarray: 提取的特征矩阵
    """
    features = []
    # 实现代码
    return np.array(features)

# ❌ 不好的例子
def extractFeatures(pcapFile, seqLen=5):
    # 缺少文档字符串
    f = []
    # 实现代码
    return f
```

### 命名约定

- **模块名**：小写，用下划线分隔 `feature_extraction.py`
- **类名**：CapWords风格 `PacketProcessor`
- **函数/方法名**：小写，用下划线分隔 `process_pcap()`
- **常量**：全大写，用下划线分隔 `SEQ_LENGTH = 5`

### 代码注释

```python
# 添加有意义的注释
# ✅ 好的
sequence_length = 5  # 用于Transformer输入的固定序列长度

# ❌ 不好的
sl = 5  # 长度
```

### 文件头注释

```python
"""
module_name.py - 简短的模块描述

详细描述（如果需要）。
"""

import os
import sys
# ... 其他导入
```

## 提交流程

### 1. Fork项目

点击GitHub上的"Fork"按钮创建你的副本。

### 2. 创建分支

```bash
git clone https://github.com/your-username/IPSecVPN_traffic.git
cd IPSecVPN_traffic
git checkout -b feature/add-new-feature
# 或修复bug
git checkout -b fix/fix-bug-description
```

**分支命名约定**：
- 新功能：`feature/feature-name`
- Bug修复：`fix/bug-description`
- 文档：`docs/documentation-topic`
- 测试：`test/test-description`

### 3. 进行更改

- 进行有意义的提交
- 编写清晰的提交信息
- 为重要的改动编写或更新测试

### 4. 提交提交

```bash
git add .
git commit -m "添加功能描述或修复描述"
```

**提交信息格式**：

```
[类型] 简短描述（50字以内）

详细描述（如需要）
- 一个改动
- 另一个改动

完成问题 #123
```

**类型选项**：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码风格调整（不改变功能）
- `refactor`: 代码重构
- `test`: 添加或更新测试
- `chore`: 其他改动

### 5. 推送到你的Fork

```bash
git push origin feature/add-new-feature
```

### 6. 提交Pull Request

1. 去GitHub上你的Fork项目
2. 点击"New Pull Request"
3. 填写PR模板：

```markdown
## 描述
清晰描述这个PR的改动

## 相关Issue
完成 #123

## 改动类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 其他

## 改动清单
- [ ] 我的代码遵循项目风格
- [ ] 我已进行自我审查
- [ ] 我已添加/更新文档
- [ ] 我已添加新的测试
- [ ] 现有测试通过

## 截图（如适用）
添加截图帮助说明改动

## 其他说明
任何其他需要审审者知道的信息
```

### 7. 代码审审

维护者将审审你的PR：
- 检查代码质量
- 验证测试
- 提出改进建议
- 批准合并

根据审批意见进行修改，然后推送更新。

## 开发环境设置

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/your-username/IPSecVPN_traffic.git
cd IPSecVPN_traffic

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装pre-commit钩子（可选）
pre-commit install
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_feature_extraction.py

# 生成覆盖率报告
pytest --cov=model
```

### 代码格式化

```bash
# 使用Black格式化代码
black . --line-length 100

# 使用Flake8检查风格
flake8 .

# 使用isort整理导入
isort .
```

## 获得帮助

- 📖 查看[文档](README.md)
- 💬 在Issue中讨论
- 📧 联系维护者

## 许可

通过贡献，你同意你的代码将在MIT许可证下发布。
