# Bond

## 定义

`Bond` 表示 Molecule 内部与共用电子对相关的化学键。

当前 Bond 范围包含：

- 共价键。
- 配位键。
- 离域大 π 键。
- 金属键。

当前 Bond 范围不包含：

- 氢键。
- 范德华力。
- 分子间偶极作用。
- 其他分子间作用力。

这些分子间作用力不属于当前 Bond 的范围。未来如果需要表示它们，应在 Matter 或 Mixture 层级另行设计，不纳入 Molecule 内部的 Bond 体系。

## 基础属性

```text
_id
bAtomList
bBondType
bBondOrder
bElectronCount
bIsDelocalized
bBondEnergy
bBondLength
bPolarity
bMetalBondModel
bDelocalizedElectronCount
bCoordinationNumber
bLatticeType
bMetallicBondStrength
```

## Runtime Reference

```text
rParentMolecule
```

`rParentMolecule` 表示当前 Bond 所属的 Molecule runtime reference。它是结构归属引用，不表示 Bond 的真实物质性质。

规则：

1. `rParentMolecule` 不进入 descriptor。
2. `rParentMolecule` 不参与 `hash()`。
3. 如果存档或调试展示需要 parent 信息，可以使用 parent id 或外部索引，但该信息不属于 Bond 的性质哈希。

## 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | Bond object instance 的唯一 id，前缀为 `BOND_` |
| `bAtomList` | 当前化学键连接或关联的 Atom 集合 |
| `bBondType` | 键类型 |
| `bBondOrder` | 键级 |
| `bElectronCount` | 该键关联的电子数 |
| `bIsDelocalized` | 是否离域 |
| `bBondEnergy` | 键能 |
| `bBondLength` | 键长 |
| `bPolarity` | 键极性 |
| `bMetalBondModel` | 金属键模型，例如 `electronSea`、`bandApproximation`、`custom` |
| `bDelocalizedElectronCount` | 参与离域或金属键的电子数 |
| `bCoordinationNumber` | 配位数，尤其用于金属晶体或多中心键 |
| `bLatticeType` | 金属晶格类型，例如 `bcc`、`fcc`、`hcp` |
| `bMetallicBondStrength` | 金属键强度，标准单位见 `../units_and_precision.md` |
| `rParentMolecule` | 所属 Molecule runtime reference |

## Required And Optional Fields

第一版 Bond 的实现建议：

- 必填字段：`bAtomList`、`bBondType`
- 常规化学键推荐填写：`bBondOrder`、`bElectronCount`
- 金属键专用可选字段：`bMetalBondModel`、`bCoordinationNumber`、`bLatticeType`、`bMetallicBondStrength`、`bDelocalizedElectronCount`

这样可以让第一版文档先覆盖普通共价键与金属键，而不要求所有 Bond 都填满全部高级字段。

## `bAtomList`

`bAtomList` 虽然命名中包含 `List`，但实际实现可以使用 `list`、`set` 或 `dict`。它表示参与当前 Bond 的 Atom 集合。

普通共价键通常包含两个 Atom。离域大 π 键或金属键可以包含多个 Atom。

进入 hash canonical payload 时，如果 `bAtomList` 被实现为无序集合，需要转换成 Atom hash list，并按 hash 的 ASCII 升序排列。若存在重复对象，需要保留重复项。
