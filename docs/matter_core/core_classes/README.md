# Core Classes

## 导航

`matterCore` 的核心 class 拆分为以下文档：

- `atom.md`：Atom / Item 能级，表示原子或离子。
- `bond.md`：Bond，表示 Molecule 内部与共用电子对相关的化学键。
- `molecule.md`：Molecule，表示由 Atom 和 Bond 组成的分子或结构单元。
- `matter.md`：Matter，表示具有统一物理组织方式的物质单元。
- `matter_intmol_interaction.md`：MatterIntmolInteraction，表示 Matter 层级的分子间作用力。
- `mixture.md`：Mixture 和 MixtureComponent，表示多个不同 Matter 的组合关系。

## 命名说明

文档中当前使用 `Atom` 作为原子或离子的 class 名称。`AtomPresetDatabase` 表示 Atom / ion 这个能级的预制数据库，字段规范见 [atompresetdatabase.md](../preset_database/atompresetdatabase.md)。

## `xxList` 说明

`xxList` 表示对象集合，不强制表示 Python `list`。

`xxList` 在代码中可以根据访问方式实现为 `list`、`set` 或 `dict`。

当需要通过 id 索引对象时，`xxList` 推荐实现为：

```python
dict[str, object]
```

例如：

```python
bAtomList: dict[str, AtomLogic]
bBondList: dict[str, BondLogic]
```

当 `xxList` 本质上是无序集合时，也可以使用 `set` 实现。进入 hash canonical payload 时，`set` 需要先转换成子对象 hash list，并按 hash 的 ASCII 升序排列；重复对象需要保留重复项。
