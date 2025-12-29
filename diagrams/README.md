# AIStats UML图表说明

本文件夹包含AIStats系统的UML设计图，采用PlantUML格式编写。

## 📁 文件清单

| 文件名 | 图表类型 | 说明 | 论文引用位置 |
|--------|---------|------|------------|
| `sequence_diagram.puml` | 时序图 | AI辅助分析Function Calling流程 | 第4.1.4节 |
| `bidirectional_binding_minimal.puml` | 流程图⭐⭐ | 双向绑定极简版（横向流程） | 推荐PPT/演讲 |
| `bidirectional_binding_basic.puml` | 关系图⭐ | 双向绑定基础版（4步流程） | 推荐论文 |
| `bidirectional_binding_simple.puml` | 序列图 | 双向绑定简化版（时序细节） | 第4.1.4节 |
| `bidirectional_binding_flow.puml` | 活动图 | 双向绑定详细版（完整步骤） | 技术文档 |
| `entity_relationship.puml` | 实体关系图 | Session State数据模型 | 第3.3节 |
| `system_architecture.puml` | 系统架构图 | 四层架构设计 | 第3.2.1节 |
| `use_case_diagram.puml` | 用例图（简化版）⭐ | 系统功能与用户交互概览 | 第3.1.1节 |
| `use_case_detailed.puml` | 用例图（详细版1） | 数据管理与可视化模块详细用例 | 附录 |
| `use_case_ai.puml` | 用例图（详细版2） | 统计分析与AI辅助模块详细用例 | 附录 |

## 🔧 如何查看UML图

### 方法1：使用在线工具（推荐）

1. 访问 [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. 复制`.puml`文件内容到编辑器
3. 自动生成可视化图表

### 方法2：使用VS Code插件

1. 安装插件：[PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)
2. 打开`.puml`文件
3. 按 `Alt+D` 预览图表

### 方法3：本地命令行生成

```bash
# 安装PlantUML（需要Java环境）
# Windows
choco install plantuml

# macOS
brew install plantuml

# 生成PNG图片
plantuml sequence_diagram.puml

# 生成SVG矢量图
plantuml -tsvg sequence_diagram.puml

# 批量生成所有图
plantuml *.puml
```

## 📊 图表详细说明

### 1. 时序图 (sequence_diagram.puml)

**目的**: 展示AI辅助分析的完整交互流程

**参与者**:
- 用户
- Streamlit界面
- AI辅助模块
- DeepSeek API (LLM)
- 统计函数库
- Session State

**流程阶段**:
1. 用户发起查询
2. LLM意图识别
3. 执行统计分析
4. 生成智能解读
5. 返回结果

**关键技术**: Function Calling机制

---

### 1.5. 双向绑定流程图（4个版本）

#### 1.5.1 极简版流程图 (bidirectional_binding_minimal.puml) ⭐⭐最推荐

**目的**: 用最简单的方式展示双向绑定核心流程

**特点**:
- **横向流程**，清晰易懂
- **5个关键步骤**：用户输入 → AI调用1 → 函数执行 → AI调用2 → 用户输出
- 每个步骤用不同颜色区分
- 适合PPT演示、快速理解

**适用场景**:
- ⭐⭐ PPT演讲（首选）
- ⭐⭐ 论文插图（推荐）
- ⭐ 技术介绍

---

#### 1.5.2 基础版关系图 (bidirectional_binding_basic.puml) ⭐推荐论文

**目的**: 展示双向绑定的4步核心流程和双向关系

**特点**:
- **纵向结构**，强调"双向"
- 标注了①②③④四个步骤
- 明确标注"正向绑定"和"反向绑定"
- 包含关键数据示例

**适用场景**:
- ⭐⭐ 论文正文（推荐）
- ⭐ 技术博客
- ⭐ 教学演示

---

#### 1.5.3 简化版序列图 (bidirectional_binding_simple.puml)

**目的**: 清晰展示双向绑定的完整闭环

**特点**:
- 简洁明了，适合论文排版
- 突出"双向"概念：正向绑定 + 反向绑定
- 展示两次AI调用 + 一次函数执行

**参与者**:
- 用户
- AI绑定层（DeepSeek LLM）
- 统计引擎（Python函数）

**关键流程**:
1. **正向绑定**：AI理解意图 → 生成函数调用 → 统计引擎执行
2. **反向绑定**：执行结果回传 → AI基于真实数据解读

**应用场景**: 
- 论文正文引用
- 会议报告演示
- 技术讲解

---

#### 1.5.4 详细版活动图 (bidirectional_binding_flow.puml)

**目的**: 详细展示双向绑定的所有技术细节

**特点**:
- 完整的活动流程
- 详细的数据流转
- 包含所有判断分支和异常处理

**包含内容**:
1. **第一次AI调用阶段**：
   - 消息上下文构建
   - LLM推理过程（意图识别、方法匹配、参数提取）
   - Function Call JSON生成

2. **函数执行阶段**：
   - 参数验证
   - 数据处理
   - 统计计算
   - 结果返回

3. **第二次AI调用阶段**：
   - 包含结果的上下文构建
   - LLM基于真实数据解读
   - 自然语言生成

**应用场景**:
- 技术文档
- 系统设计说明
- 开发人员参考

---

### 2. 实体关系图 (entity_relationship.puml)

**目的**: 展示数据模型和实体关系

**核心实体** (8个):
- SessionState: 会话状态管理
- Data: 数据集
- VariableLabels: 变量标签
- StatisticalResults: 统计结果
- Visualization: 可视化图表
- AIConfig: AI配置
- ChatHistory: 对话历史
- FunctionDefinition: 函数定义

**关系类型**:
- 一对一: SessionState ↔ Data, AIConfig
- 一对多: SessionState → Labels, Results, Viz, Chat
- 多对一: Results, Viz → Data
- 引用: Chat → Results, Func

---

### 3. 系统架构图 (system_architecture.puml)

**目的**: 展示系统四层架构设计

**架构层次**:

1. **表示层** (Presentation Layer)
   - 5个视图模块
   - 代码量：2,741行 (91.2%)

2. **业务逻辑层** (Business Logic Layer)
   - 数据管理器 (DataManager)
   - 统计分析器 (StatAnalyzer)
   - AI助手 (AIAssistant)
   - 可视化引擎 (VisualizationEngine)

3. **工具函数层** (Utility Layer)
   - 统计函数库 (141行)
   - 变量标签库 (120行)

4. **数据访问层** (Data Access Layer)
   - Session State管理

5. **技术支撑层** (Infrastructure Layer)
   - pandas, NumPy, SciPy, statsmodels, Plotly, OpenAI

---

### 4. 用例图

#### 4.1 简化版 (use_case_diagram.puml) ⭐推荐用于论文

**目的**: 展示系统功能和用户交互的整体概览

**特点**:
- 简洁清晰，避免PlantUML渲染问题
- 展示4大功能模块的核心用例
- 适合论文排版

**用户角色** (2类):
- 统计学初学者
- 科研人员

**功能模块** (4大模块):
1. 数据管理模块 (4个用例)
2. 可视化模块 (3个用例)
3. 统计分析模块 (5个用例)
4. AI辅助分析模块 (3个用例)

**用例数量**: 15个核心用例

---

#### 4.2 详细版1 - 数据管理与可视化 (use_case_detailed.puml)

**目的**: 展示数据管理和可视化模块的详细用例

**包含功能**:
1. **数据管理模块**
   - 导入数据 (CSV/Excel)
   - 预览数据
   - 管理变量标签 (手动/VLOOKUP)
   - 导出数据

2. **可视化模块**
   - 7种图表类型 (折线图、散点图、柱状图、箱线图、饼图、直方图、3D散点图)
   - 交互式探索 (缩放、悬停、导出)

**用例数量**: 6个主要用例，20个子用例

---

#### 4.3 详细版2 - 统计分析与AI辅助 (use_case_ai.puml)

**目的**: 展示统计分析和AI辅助模块的详细用例

**包含功能**:
1. **统计分析模块**
   - 描述统计
   - 假设检验 (t检验系列、ANOVA、LSD)
   - 相关与回归 (Pearson、Spearman、线性、逻辑)
   - 高级分析 (信度、中介)
   - AI结果解读

2. **AI辅助分析模块**
   - 自然语言查询
   - 智能统计分析 (Function Calling)
   - 对话式学习

**用例数量**: 8个主要用例，20个子用例

---

## 🎯 设计原则

1. **分层解耦**: 各层职责清晰，便于维护
2. **模块化**: 功能模块独立，易于扩展
3. **标准化**: 统一接口规范，降低复杂度
4. **可测试**: 各层可独立测试

## 📖 论文引用说明

在论文中，这些UML图分布在以下章节：

- **第3.1.1节**: 用例图 → 功能需求分析
- **第3.2.1节**: 系统架构图 → 总体架构设计
- **第3.3节**: 实体关系图 → 数据模型设计
- **第4.1.4节**: 时序图 → AI辅助分析模块实现

## 📝 修改建议

如需修改图表，请遵循以下规范：

1. **代码风格**: 保持一致的缩进和命名
2. **注释完整**: 关键部分添加note说明
3. **颜色使用**: 使用主题色区分模块
4. **箭头方向**: 明确依赖关系和调用顺序
5. **文字简洁**: 中英文混合，专业术语用英文

## 🔗 相关资源

- [PlantUML官方文档](https://plantuml.com/zh/)
- [PlantUML语法速查](https://plantuml.com/zh/guide)
- [UML建模规范](https://www.omg.org/spec/UML/)
- [系统架构设计最佳实践](https://c4model.com/)

## ⚖️ 版权声明

本UML图表为AIStats项目的一部分，遵循项目的开源协议。

---

**最后更新**: 2025年11月3日  
**维护者**: AIStats开发团队

