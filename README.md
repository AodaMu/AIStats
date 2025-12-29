# AIStats
Graduation Project（毕业设计）
# AIStats - AI 加持的在线统计分析应用

> 使用 Python + Streamlit 实现，模仿 PsychPen 的架构设计

## 项目简介

AIStats 是一个基于 Python 的在线统计分析工具，包含数据处理、可视化、统计分析和 AI 辅助分析四大核心模块。

### 技术栈

- **Web 框架**：Streamlit
- **数据处理**：pandas、numpy
- **统计分析**：scipy、statsmodels
- **数据可视化**：plotly
- **AI 集成**：deepseek

## 功能模块

### 📁 数据视图

- 支持导入 CSV、Excel 格式
- 数据预览与基本信息展示
- 多格式数据导出（CSV/Excel）
- 数据删除与管理

### 📈 绘图视图

- **折线图**：支持多变量、数据点标记、样条曲线
- **散点图**：支持分组着色、大小映射、趋势线与回归方程
- **柱状图**：支持分组、多种聚合函数
- **箱线图**：支持多变量、分组对比
- **饼图**：支持百分比标签
- **直方图**：可调分组数的分布展示
- **3D 散点图**：三维数据可视化

### 📊 统计视图

- **描述统计**：均值、标准差、分位数、偏度、峰度等
- **t 检验**：单样本、配对样本、独立样本
- **方差分析**：单因素 ANOVA + Levene 方差齐性检验
- **相关分析**：Pearson 相关矩阵与显著性检验
- **回归分析**：一元与多元线性回归
- **信度分析**：Cronbach's Alpha 信度系数
- **中介效应**：简单中介模型分析（a、b、c、c' 路径）

### 🤖 AI 辅助分析

- **推荐使用 DeepSeek**（性价比高，支持 Function Calling）
- 也兼容其他 OpenAI API 格式服务（GPT-4、Qwen 等）
- **AI 可调用的统计函数**：
  - `independent_t_test`：独立样本 t 检验
  - `descriptive_stats`：描述统计
  - `pearson_correlation`：相关分析
- **智能化结果展示**：自动生成统计表格和可视化建议
- 自然语言交互，AI 自动调用工具函数辅助分析

## 安装与运行

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd AIStats
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器自动打开，默认地址：`http://localhost:8501`

## 使用说明

### 数据导入

1. 进入"📁 数据视图"
2. 点击"选择数据文件"上传 CSV/Excel
3. 查看数据预览与基本信息

### 绘图与统计

1. 导入数据后，切换到"📈 绘图视图"或"📊 统计视图"
2. 选择对应的图表类型或统计方法
3. 配置变量与参数
4. 点击"生成"或"执行"按钮

### AI 辅助分析

1. 进入"🤖 AI 辅助分析"
2. 在配置区域填写：
   - **API Key**：在 [DeepSeek 平台](https://platform.deepseek.com) 获取
   - **Base URL**：`https://api.deepseek.com`（默认已填写）
   - **模型名称**：`deepseek-chat`（默认已填写）
3. 勾选"开启 AI 辅助分析"并保存
4. 在对话框输入问题，AI 会自动调用工具查询数据并回答

示例对话：
- "当前数据集有多少行？"
- "帮我看看变量 age 的描述统计"
- "解释一下最新的统计结果"

<<<<<<< HEAD
=======
> 💡 也可使用其他 OpenAI 兼容服务，修改 Base URL 和模型名称即可
>>>>>>> dab22a1f7bbf8e216747125e37c5f7e4dcf2b634

## 项目结构

```
AIStats/
├── app.py                    # 主应用入口
├── requirements.txt          # 依赖列表
├── README.md                 # 本文档
├── 项目介绍.md                # 详细中文文档
└── src/
    ├── __init__.py
    ├── components/           # 功能模块
    │   ├── __init__.py
    │   ├── data_view.py     # 数据视图模块
    │   ├── plot_view.py     # 绘图视图模块
    │   ├── stat_view.py     # 统计视图模块
    │   └── ai_view_v2.py    # AI 辅助分析模块
    └── lib/                 # 工具函数库
        ├── __init__.py
        └── stat_functions.py # 统计函数封装（供 AI 调用）
```

## 依赖说明

- `streamlit>=1.32.0`：Web 应用框架
- `pandas>=2.2.0`：数据处理
- `numpy>=1.26.0`：数值计算
- `plotly>=5.20.0`：交互式图表
- `scipy>=1.12.0`：科学计算与统计检验
- `statsmodels>=0.14.0`：高级统计模型
- `openai>=1.12.0`：OpenAI API 客户端
- `openpyxl>=3.1.0`：Excel 文件读写

## 注意事项

1. **AI 配置**：本应用不提供 AI 算力，需自行申请 DeepSeek 或其他兼容服务商的 API Key
   - DeepSeek 申请地址：https://platform.deepseek.com
   - 价格实惠，推荐个人使用
2. **数据隐私**：所有数据处理均在本地进行，仅在使用 AI 功能时会将数据摘要发送到配置的 API 服务
3. **统计方法**：部分高级统计方法需要数据满足特定假设（如正态性、方差齐性），请结合专业知识使用

## 许可证

本项目采用 MIT 许可证。

## 致谢

- 本项目模仿 [PsychPen](https://github.com/LeafYeeXYZ/PsychPen) 的设计理念
- 感谢 Streamlit、Plotly、SciPy、Statsmodels 等开源项目

