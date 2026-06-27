# Matter Core

## 目标

`matterCore` 是 MatterCraft 的核心物质表示层。它不只服务于反应推断，也会作为后续物理模拟、渲染、存档、计算优化和 Debug 展示的基础数据模型。

`matterCore` 当前包含五个基础层级：

```text
Atom -> Bond -> Molecule -> Matter -> Mixture
```

其中：

- `Atom`：原子或离子。
- `Bond`：分子内部与共用电子对相关的化学键。
- `Molecule`：由 Atom 和 Bond 组成的分子或结构单元。
- `Matter`：具有统一物理组织方式的物质单元。
- `Mixture`：多个不同 Matter 的组合。

## 设计原则

1. 所有核心对象都默认拥有 `_id` 字段和 `hash()` 方法。
2. `_id` 用于区分 object instance，`hash()` 用于判断对象性质是否完全相同。
3. 核心对象采用 `LDC` 三版本结构：`Logic`、`Descriptor`、`Calculus`。
4. `Logic` 版本作为主要业务入口，并负责与 `Descriptor`、`Calculus` 互相转换。
5. 命名中 `xxList` 表示对象集合，不强制表示 Python `list`。当需要通过 id 索引对象时，`xxList` 可以实现为 `dict[str, object]`。
6. 除 `Matter` 层级需要区分 `Chem` 和 `Phy` 属性之外，其他核心 class 默认不添加 `Chem` 或 `Phy` 前缀。
7. `r` 前缀表示 runtime reference。`r` 属性默认不进入 descriptor，也不参与 `hash()`。

## 文档导航

- `ldc_structure.md`：LDC 三版本结构。
- `object_identity_and_hash.md`：对象 `_id` 与 `hash()` 规则。
- `units_and_precision.md`：全项目基础量单位与精度规范。
- `core_classes/README.md`：核心 class 设计导航。
- `preset_database/atompresetdatabase.md`：AtomPresetDatabase 字段与 CSV 规范。
- `todo.md`：待讨论问题。
