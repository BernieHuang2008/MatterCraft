# MatterIntmolInteraction

## 定义

`MatterIntmolInteraction` 表示 Matter 层级的分子间作用力。它不属于 Molecule 内部的 Bond，也不进入 Bond 体系。

该 class 用于描述同一个 Matter 单元内部，Molecule、Atom site 或局部结构之间的弱相互作用，例如：

- 氢键。
- 范德华力。
- 分子间偶极作用。
- 离子-偶极作用。
- π-π stacking。

## 基础属性

```text
_id
bInteractionType
bParticipantList
bInteractionStrength
bInteractionDistance
bDirectionality
bGeometry
bInteractionModel
```

## 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | MatterIntmolInteraction object instance 的唯一 id，前缀为 `MINT_` |
| `bInteractionType` | 分子间作用力类型，例如 `hydrogenBond`、`vanDerWaals`、`dipoleDipole`、`ionDipole`、`piStacking` |
| `bParticipantList` | 参与该相互作用的对象集合，可以是 Molecule、Atom site 或其他稳定 descriptor |
| `bInteractionStrength` | 相互作用强度，标准单位见 `../units_and_precision.md` |
| `bInteractionDistance` | 相互作用距离，标准单位见 `../units_and_precision.md` |
| `bDirectionality` | 方向性描述，适用于氢键等具有明显方向性的相互作用 |
| `bGeometry` | 几何描述，例如角度、相对位置或局部构型 |
| `bInteractionModel` | 使用的作用力模型，例如 `lennardJones`、`coulombApproximation`、`custom` |

## Participant Rule

第一版 `MatterIntmolInteraction` 允许以下参与者形式：

- `Molecule` descriptor
- `Atom site` descriptor

两者可以混用，但每个参与者都必须是稳定 descriptor、稳定 hash 引用或其他可序列化稳定表示，不能直接依赖运行时内存引用。

## First Version Positioning

第一版 `MatterIntmolInteraction` 定位为描述性对象，而不是完整的数值求解对象。

它的主要职责是：

- 表达某种 Matter 内部存在哪类分子间作用力
- 表达哪些参与者之间存在该作用力
- 表达强度、距离、方向性和几何约束

第一版不要求它独立承担完整的能量求解、力场积分或动态演化职责。后续如果需要更强的计算能力，再在 `Calculus` 或专门模型层中扩展。

## `List` 命名说明

`bParticipantList` 表示参与者集合，不强制表示 Python `list`。实现时可以根据访问方式选择 `list`、`set` 或 `dict`。

进入 hash canonical payload 时，如果集合无序，需要转换成参与者 hash list，并按 hash 的 ASCII 升序排列。若存在重复参与者，需要保留重复项。

## 边界

`MatterIntmolInteraction` 描述 Matter 内部结构中的分子间作用力。Mixture 层级可以描述不同 Matter 之间的宏观接触、空间分布或界面关系，但不直接承担微观分子间作用力模型。
