# Visualize Mixture

## 定位

`visualize mixture` 负责展示 `MixtureLogic`。  
这一层的关注重点是多个 `Matter` 组分在宏观层面的组合关系、比例关系、空间分布与接触关系。

与 `visualize molecule` 和 `visualize matter` 相比，`visualize mixture` 更像一个体系视图，而不是键级结构图。

## 输入

输入对象：

```python
MixtureLogic
```

最低关注字段：

```text
_id
bMixtureType
bMixtureTypeProperty
bMixtureComponentList
```

## 模式

第一版同样采用：

- `teaching`
- `structural`

其中：

- `teaching` 用于快速看懂组分与比例
- `structural` 用于看空间分布、接触关系与宏观组织方式

## `teaching` 模式

推荐优先展示：

- mixture 类型
- component 列表
- 各 component 对应的 matter
- 数量、比例或浓度摘要

目标是让用户一眼看出：

- 这是什么类型的混合体系
- 由哪些组分构成
- 各组分大致占多少

## `structural` 模式

`structural` 模式用于进一步展示：

- 组分的空间分布方式
- 接触关系
- 局部分层、悬浮、颗粒随机分布等宏观结构特征

这一层的重点仍然是“体系结构理解”，而不是一开始就做复杂仿真画面。

## 交互建议

推荐行为：

- 点击 component：显示其 `Matter`、amount、fraction、concentration 等摘要
- 点击分布区域：显示 `bSpatialDistribution` 的解释
- 点击接触关系：显示 `bContactRelation` 摘要
- 支持从 component 下钻到 `visualize matter`

## 输出

建议统一输出：

1. `scene`
2. `panel`

## 第一版建议范围

第一版建议做到：

- 输入 `MixtureLogic`
- `teaching` 模式下的组分与比例摘要图
- `structural` 模式下的空间分布与接触关系摘要
- 支持从 mixture 下钻到 matter

第一版可暂不要求：

- 高精度流体动画
- 全连续介质场渲染
- 复杂时间演化与扩散过程展示

## TODO

- TODO: 后续讨论不同 `bMixtureType` 是否需要各自的专用视图模板，例如 solution、granular、suspension、powder 等。
