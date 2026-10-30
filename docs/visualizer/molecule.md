# Visualize Molecule

## 定位

`visualize molecule` 是 `visualizer` 模块中负责展示 `MoleculeLogic` 的 visualizer。  
它的目标是让用户快速理解一个分子的组成、键连接关系与局部结构。

与 `visualize atom` 相比，`visualize molecule` 的重点从单原子内部结构转为：

- 原子节点之间的连接关系
- 化学键的类型与局部结构
- 分子的整体轮廓与局部可下钻能力

## 输入

输入对象：

```python
MoleculeLogic
```

最低关注字段：

```text
_id
bAtomList
bBondList
```

## 模式

第一版也保留两种模式：

- `teaching`
- `structural`

其中：

- `teaching` 偏 2D/直观结构图，强调一眼读懂分子骨架
- `structural` 偏真实空间关系、局部结构细节与更深入的键相关展示

## `teaching` 模式

推荐采用直观的结构图表达：

- 原子作为节点
- 化学键作为边
- 不强制要求复杂 3D 相机交互
- 优先显示骨架、官能团和局部连接关系

推荐用户一眼能看出：

- 有哪些 atom
- atom 如何连接
- 哪些是单键、双键、三键或其他类型键

## `structural` 模式

`structural` 模式可引入更强的空间感和局部高亮能力，用于展示：

- 分子几何近似布局
- 键长、键级、极性等结构属性
- 被选 atom 的局部环境
- 被选 bond 的成键信息

是否在这一层展示更深入的成键电子信息，后续可继续讨论；第一版不强制。

## 交互建议

建议交互保持和 `visualize atom` 一致的哲学：默认看摘要，点击看细节，下钻看局部。

推荐行为：

- 点击 atom：显示该 atom 摘要，并允许下钻到 `visualize atom`
- 点击 bond：显示 bond 类型、bond order、bond length、bond polarity 等信息
- 点击空白：返回整体视图

## 输出

建议输出仍然分为：

1. `scene`
2. `panel`

其中：

- `scene` 负责节点、边、布局与高亮
- `panel` 负责当前 atom、bond 或 molecule 的解释文字

## 第一版建议范围

第一版建议做到：

- 输入 `MoleculeLogic`
- `teaching` 模式下的直观结构图
- `structural` 模式下的局部结构高亮
- atom 点击下钻到 `visualize atom`
- bond 点击显示键属性

第一版可暂不要求：

- 高精度构象优化可视化
- 严格量化成键轨道图
- 动态反应路径动画

## TODO

- TODO: 后续讨论 `visualize molecule` 是否需要直接展示局部成键轨道、离域电子与反应活性热点。
