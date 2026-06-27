# Molecule

## 定义

`Molecule` 表示由 Atom 和 Bond 组成的分子或结构单元。

## 基础属性

```text
_id
bAtomList
bBondList
```

## 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | Molecule object instance 的唯一 id，前缀为 `MOL_` |
| `bAtomList` | 当前 Molecule 包含的 Atom 集合 |
| `bBondList` | 当前 Molecule 包含的 Bond 集合 |

类型建议：

```python
bAtomList: dict[str, AtomLogic]
bBondList: dict[str, BondLogic]
```

## `List` 命名说明

`bAtomList` 和 `bBondList` 虽然命名中包含 `List`，但实际实现可以使用 `list`、`set` 或 `dict`。这里的 `List` 表示对象集合，不表示 Python `list` 类型。

如果需要通过 `_id` 稳定索引具体 Atom 或 Bond，可以使用 `dict[str, object]`。如果只需要表达无序成员集合，可以使用 `set`。

进入 hash canonical payload 时，`bAtomList` 和 `bBondList` 这类无序集合需要先转换为子对象 hash list，并按 hash 的 ASCII 升序排列。若存在重复对象，例如 H-H 键中的两个 H atom hash 相同，则保留两个相同 hash。

## 推荐操作

```text
addBond()
removeBond()
breakBond()
createBond()
findBondsByAtom()
findNeighborAtoms()
findReactiveBonds()
```

这些方法位于 `MoleculeLogic` 时，不需要额外添加 `Logic` 前缀。
