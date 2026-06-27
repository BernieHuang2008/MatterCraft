# Matter

## 定义

`Matter` 表示一个具有统一物理组织方式的物质单元。

Matter 可以包含一种或多种 Molecule。Matter 是从化学结构过渡到物理状态的层级，因此该层级需要区分 `Chem` 和 `Phy` 属性。

`Matter` 侧重描述物质自身的微观单元结构（如晶胞），而 `Mixture` 描述物质的宏观状态、以及多个 `Matter` 之间的宏观混合关系。
比如由多种分子构成的晶体，因为是微观的混合 `Matter` ，所以其混合信息存储在 `Matter` 层级的晶胞信息中，而沙子虽然成分相同，但是并没有微观的单元结构，因此其混合信息存储在 `Mixture` 层级中（即使它并没有“混合”，只有一个`MixtureComponent`）（例如只有一个 `MixtureComponent`，但是里面记录的表面积是每一粒沙子的表面积之和，比一整块SiO2的表面积大很多）。

## 基础属性

```text
_id
bChemMoleculeList
bPhyMoleculeGap
bPhyMoleculeArrangement
bMatterIntmolInteractionList
```

## 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | Matter object instance 的唯一 id，前缀为 `MAT_` |
| `bChemMoleculeList` | molecule id 到 Molecule object 的映射 |
| `bPhyMoleculeGap` | 分子间距 |
| `bPhyMoleculeArrangement` | 分子排列方式，例如晶胞、晶格、局部排列 |
| `bMatterIntmolInteractionList` | Matter 层级的分子间作用力集合 |

## `List` 命名说明

`bChemMoleculeList` 和 `bMatterIntmolInteractionList` 中的 `List` 表示对象集合，不强制表示 Python `list`。实现时可以根据访问方式选择 `list`、`set` 或 `dict`。

进入 hash canonical payload 时，如果集合无序，需要转换成子对象 hash list，并按 hash 的 ASCII 升序排列。

## 适用范围

Matter 可以表示：

- 单一分子构成的纯物质。
- 多种 Molecule 共同组成的规则晶体。
- 一个具有统一物理排列方式的物质相。

## TODO

- TODO: 继续讨论 Matter 与宏观微粒之间是否需要新增中间层级，例如晶胞组成沙粒、金属块、粉末颗粒等。
