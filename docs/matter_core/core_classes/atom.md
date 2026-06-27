# Atom

## 定义

`Atom` 表示原子或离子。它是 MatterCraft 中最基础的化学对象层级。

## 基础属性

```text
_id
bAtomicNumber
bMassNumber
bCharge
bElectronConfig
```

## 自动计算属性

```text
aProtonCount
aNeutronCount
aElectronCount
aValenceElectronCount
```

## 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | Atom object instance 的唯一 id，前缀为 `ATOM_` |
| `bAtomicNumber` | 原子序数，等于质子数 |
| `bMassNumber` | 质量数，等于质子数加中子数 |
| `bCharge` | 电荷，中性为 0，阳离子为正，阴离子为负 |
| `bElectronConfig` | 当前原子或离子的电子排布 |
| `aProtonCount` | 自动等于 `bAtomicNumber` |
| `aNeutronCount` | 自动等于 `bMassNumber - bAtomicNumber` |
| `aElectronCount` | 自动等于 `bAtomicNumber - bCharge` |
| `aValenceElectronCount` | 根据 `bElectronConfig` 自动计算价电子数 |

## Electron Config

`bElectronConfig` 是 basic property。它可以由构造方法自动填入，也可以在特殊情况下手动指定。

推荐结构：

```python
{
    "3p": [2, 1, 1],
    "3s": [2],
}
```

规则：

1. key 表示能级或轨道类型，例如 `"3p"`。
2. value 是轨道电子占据列表。
3. 列表长度由轨道类型决定：`s` 为 1，`p` 为 3，`d` 为 5，`f` 为 7。
4. 列表中的数字表示该轨道中的电子数，通常为 `0`、`1` 或 `2`。
5. 不存在的能级不写入字典。
6. 常规状态下的电子排布应遵循构造原理、洪特规则和泡利不相容原理。

构造方法可以自动设置 `bElectronConfig`：

```text
fromElementSymbol("Na")
fromElementSymbol("Cl", charge=-1)
fromPreset("O16")
```

特殊状态也可以手动指定 `bElectronConfig`，例如激发态、反应中间态或非默认离子电子排布。

## AtomPresetDatabase

项目需要一套 Atom / ion 能级的预制属性数据，指定名称为 `AtomPresetDatabase`。它用于辅助构造 Atom 实例，也用于未来可能对 Atom 类进行扩展。

`AtomPresetDatabase` 的路径、CSV 字段、字段示例和加载规则见 [atompresetdatabase.md](../preset_database/atompresetdatabase.md)。

## 构造方法

`fromElementSymbol()` 用于从元素符号快速构造 Atom：

```python
fromElementSymbol(
    symbol: str,
    massNumber: int | None = None,
    charge: int = 0,
    electronConfig: dict[str, list[int]] | None = None,
) -> AtomLogic
```

参数说明：

| 参数 | 含义 |
| --- | --- |
| `symbol` | 元素符号 |
| `massNumber` | 可选质量数，不填时使用 `defaultMassNumber` |
| `charge` | 电荷，默认值为 `0` |
| `electronConfig` | 可选电子排布，不填时根据 preset 和 charge 自动生成 |

`fromPreset()` 用于从具体 preset 构造 Atom：

```python
fromPreset(
    presetId: str,
    charge: int | None = None,
    electronConfig: dict[str, list[int]] | None = None,
) -> AtomLogic
```

参数说明：

| 参数 | 含义 |
| --- | --- |
| `presetId` | 预设 id，例如同位素、常见离子或特殊激发态模板 |
| `charge` | 可选电荷。填入时覆盖 preset 默认电荷 |
| `electronConfig` | 可选电子排布。填入时覆盖 preset 默认电子排布 |

## TODO

- TODO: 讨论是否需要通过量子化学近似模型推断特定电子排布下的失电子或得电子能量。
