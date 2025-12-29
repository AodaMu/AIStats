# AIStats

🌐 [English](README.md) | **中文** | [Монгол](README_MN.md)

---

基于大语言模型的在线统计分析平台，支持自然语言交互、16种统计方法、7种交互式图表。

## ✨ 功能特性

### 📁 数据视图
- 支持导入 CSV、Excel（.xlsx、.xls）格式
- 数据预览与基本信息展示
- 多格式数据导出
- 数据清洗与管理

### 📈 绘图视图
- **折线图**：支持多变量、数据点标记、样条曲线
- **散点图**：支持分组着色、大小映射、趋势线与回归方程
- **柱状图**：支持分组、多种聚合函数
- **箱线图**：支持多变量、分组对比
- **饼图**：支持百分比标签
- **直方图**：可调分组数的分布展示
- **3D散点图**：三维数据可视化

### 📊 统计视图
- **描述统计**：均值、标准差、中位数、分位数、偏度、峰度等
- **t检验**：单样本、配对样本、独立样本
- **方差分析**：单因素 ANOVA + Levene 方差齐性检验
- **相关分析**：Pearson 相关矩阵与显著性检验
- **回归分析**：一元与多元线性回归
- **信度分析**：Cronbach's Alpha 信度系数
- **中介效应**：简单中介模型分析（a、b、c、c' 路径）

### 🤖 AI 助手
- 自然语言交互
- 自动选择统计方法
- 通俗易懂的结果解释
- 支持 DeepSeek API（推荐）及 OpenAI 兼容 API
- 三层 Prompt 架构，保证 AI 输出可控

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | Streamlit |
| 数据处理 | Pandas、NumPy |
| 统计计算 | SciPy、Statsmodels |
| 可视化 | Plotly |
| AI 服务 | DeepSeek API（兼容 OpenAI 格式）|

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/AodaMu/AIStats.git
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

## 📂 项目结构

```
AIStats/
├── app.py                    # 主应用入口
├── requirements.txt          # 依赖列表
├── README.md                 # 英文文档
├── README_CN.md              # 中文文档
├── README_MN.md              # 蒙古语文档
└── src/
    ├── components/           # 功能模块
    │   ├── data_view.py      # 数据视图模块
    │   ├── plot_view.py      # 绘图视图模块
    │   ├── stat_view.py      # 统计视图模块
    │   └── ai_view_v2.py     # AI 助手模块
    └── lib/                  # 工具函数库
        └── stat_functions.py # 统计函数（供 AI 调用）
```

## ⚙️ AI 配置说明

1. 在 [DeepSeek 平台](https://platform.deepseek.com) 获取 API Key
2. 在 AI 设置面板填写：
   - **API Key**：你的 DeepSeek API 密钥
   - **Base URL**：`https://api.deepseek.com`
   - **模型名称**：`deepseek-chat`

## 📝 许可证

MIT 许可证


