# Visualize Matter

## 定位

`visualize matter` 负责展示 `MatterLogic`。  
这一层的重点不再是单个分子内部的化学键，而是多个 `Molecule` 如何组成一个统一的物质单元，以及这些分子在物理组织上的排列方式。

## 输入

输入对象：

```python
MatterLogic
```

最低关注字段：

```text
_id
bChemMoleculeList
bPhyMoleculeGap
bPhyMoleculeArrangement
bMatterIntmolInteractionList
```

## 模式

第一版同样保留：

- `teaching`
- `structural`

其中：

- `teaching` 用于直观展示“这是怎样一种由分子构成的物质单元”
- `structural` 用于展示更细的排列方式、间距与分子间作用

## `teaching` 模式

推荐采用简洁的层级组织图：

- molecule 作为主要展示单元
- 重点说明有几类 molecule
- 重点说明大致排列关系
- 避免一开始就把用户带进复杂三维微观结构

用户应该能快速理解：

- 这个 matter 由哪些 molecule 构成
- 它们是怎样被组织成一个统一单元的

## `structural` 模式

`structural` 模式用于展示更深的组织信息，例如：

- molecule 之间的间距
- 排列方式
- 局部堆积或晶格近似关系
- 分子间作用的摘要显示

第一版重点是“结构关系图”，不强制要求高精度晶体学渲染。

## 交互建议

推荐行为：

- 点击 molecule：查看该 molecule 摘要，并允许下钻到 `visualize molecule`
- 点击分子间作用：显示 interaction 类型与说明
- 点击 arrangement 区域：显示当前物理组织方式的解释

## 输出

建议统一输出：

1. `scene`
2. `panel`

## 第一版建议范围

第一版建议做到：

- 输入 `MatterLogic`
- `teaching` 模式下的层级组织摘要图
- `structural` 模式下的分子排列与相互作用摘要
- 支持从 matter 下钻到 molecule

第一版可暂不要求：

- 高精度晶胞或周期边界条件可视化
- 大规模真实材料渲染
- 热运动或时间演化模拟

## TODO

- TODO: 后续讨论 `visualize matter` 是否需要专门区分晶体、非晶、局部有序与其他物理组织类型的专用视图。
