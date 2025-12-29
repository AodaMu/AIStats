# AIStats

🌐 **English** | [中文](README_CN.md) | [Монгол](README_MN.md)

---

AI-powered online statistical analysis platform with natural language interface, 16 statistical methods, and 7 interactive charts. Built with Streamlit.

## ✨ Features

### 📁 Data View
- Import CSV, Excel (.xlsx, .xls) files
- Data preview with basic statistics
- Export to multiple formats
- Data cleaning and management

### 📈 Plot View
- **Line Chart**: Multi-variable support, data point markers, spline curves
- **Scatter Plot**: Group coloring, size mapping, trend lines with regression equations
- **Bar Chart**: Grouped bars, multiple aggregation functions
- **Box Plot**: Multi-variable, group comparison
- **Pie Chart**: Percentage labels
- **Histogram**: Adjustable bin count
- **3D Scatter**: Three-dimensional data visualization

### 📊 Statistics View
- **Descriptive Statistics**: Mean, SD, median, quartiles, skewness, kurtosis
- **T-Tests**: One-sample, paired-sample, independent-sample
- **ANOVA**: One-way ANOVA with Levene's test for homogeneity
- **Correlation**: Pearson correlation matrix with significance testing
- **Regression**: Simple and multiple linear regression
- **Reliability**: Cronbach's Alpha coefficient
- **Mediation**: Simple mediation model (a, b, c, c' paths)

### 🤖 AI Assistant
- Natural language interaction
- Automatic statistical method selection
- Plain language result interpretation
- Supports DeepSeek API (recommended) and OpenAI-compatible APIs
- Three-layer Prompt architecture for controlled AI output

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | Streamlit |
| Data Processing | Pandas, NumPy |
| Statistics | SciPy, Statsmodels |
| Visualization | Plotly |
| AI Service | DeepSeek API (OpenAI compatible) |

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/AodaMu/AIStats.git
cd AIStats
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📂 Project Structure

```
AIStats/
├── app.py                    # Main application entry
├── requirements.txt          # Dependencies
├── README.md                 # English documentation
├── README_CN.md              # Chinese documentation
├── README_MN.md              # Mongolian documentation
└── src/
    ├── components/           # Feature modules
    │   ├── data_view.py      # Data view module
    │   ├── plot_view.py      # Plot view module
    │   ├── stat_view.py      # Statistics view module
    │   └── ai_view_v2.py     # AI assistant module
    └── lib/                  # Utility libraries
        └── stat_functions.py # Statistical functions for AI
```

## ⚙️ AI Configuration

1. Get API Key from [DeepSeek Platform](https://platform.deepseek.com)
2. Enter in the AI settings panel:
   - **API Key**: Your DeepSeek API key
   - **Base URL**: `https://api.deepseek.com`
   - **Model**: `deepseek-chat`

## 📝 License

MIT License

## 🙏 Acknowledgments

- Inspired by [PsychPen](https://github.com/LeafYeeXYZ/PsychPen)
- Built with Streamlit, Plotly, SciPy, Statsmodels
