# AIStats

🌐 [English](README.md) | **中文** | [Монгол](README_MN.md)

---

基于大语言模型的在线统计分析平台，支持自然语言交互、16种统计方法、7种交互式图表。

## 功能模块

- **数据视图**：导入 CSV/Excel，数据预览与导出
- **绘图视图**：折线图、散点图、柱状图、箱线图、饼图、直方图、3D散点图
- **统计分析**：描述统计、t检验、方差分析、相关分析、回归分析、信度分析、中介效应
- **AI助手**：自然语言交互，支持 DeepSeek/OpenAI API

## 技术栈

- Web框架：Streamlit
- 数据处理：Pandas、NumPy
- 统计计算：SciPy、Statsmodels
- 可视化：Plotly
- AI服务：DeepSeek API（兼容 OpenAI 格式）

## 快速开始

```bash
git clone https://github.com/AodaMu/AIStats.git
cd AIStats
pip install -r requirements.txt
streamlit run app.py
```

## 许可证

MIT 许可证
