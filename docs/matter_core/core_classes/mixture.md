# Mixture

## 定义

`Mixture` 表示多个不同 Matter 的组合，也存储着 Matter 的宏观组织状态。
`Matter` 侧重描述物质自身的微观单元结构（如晶胞），而 `Mixture` 描述物质的宏观状态、以及多个 `Matter` 之间的宏观混合关系。

`Mixture` 通过 `MixtureComponent` 记录每个 Matter 在当前 mixture 中的数量、比例、浓度和空间关系。

## Mixture 基础属性

```text
_id
bMixtureType
bMixtureTypeProperty
bMixtureComponentList
```

类型建议：

```python
bMixtureComponentList: set[MixtureComponentLogic]
```

## Mixture 属性说明

| 属性 | 含义 |
| --- | --- |
| `_id` | Mixture object instance 的唯一 id，前缀为 `MIXT_` |
| `bMixtureType` | Mixture 类型，例如 `solution`、`granular`、`suspension`、`emulsion`、`powder`、`melt`、`gasMixture`、`custom` |
| `bMixtureTypeProperty` | 与 `bMixtureType` 对应的类型属性集合，推荐使用可序列化 dict |
| `bMixtureComponentList` | MixtureComponent 集合，推荐使用 `set` 实现 |

## MixtureComponent

`MixtureComponent` 表示某个 Matter 在当前 Mixture 中的组成条目。

基础属性建议：

```text
_id
bMatter
bAmount
bSpatialDistribution
bContactRelation
aMass
aVolume
aMoleFraction
aMassFraction
aVolumeFraction
aAmountConcentration
aMassConcentration
```

属性说明：

| 属性 | 含义 |
| --- | --- |
| `_id` | MixtureComponent object instance 的唯一 id，前缀为 `MIXC_` |
| `bMatter` | 当前 component 对应的 Matter。在 descriptor 中应保存 Matter descriptor 或 Matter hash，在 Logic 中可以通过 runtime reference 指向 Matter object |
| `bAmount` | 当前 Matter 在 mixture 中的物质的量，标准单位为 `mol` |
| `bSpatialDistribution` | 空间分布方式，例如均匀、分层、颗粒随机分布 |
| `bContactRelation` | 与其他 Matter 的接触关系 |
| `aMass` | 根据 `bAmount` 和 `bMatter` 自动计算的质量，标准单位为 `kg` |
| `aVolume` | 根据 `bAmount`、`bMatter` 和 Matter 结构参数自动计算的体积，标准单位为 `m^3` |
| `aMoleFraction` | 根据当前 component 的 `bAmount` 与 Mixture 总物质的量自动计算的摩尔分数 |
| `aMassFraction` | 根据当前 component 的 `aMass` 与 Mixture 总质量自动计算的质量分数 |
| `aVolumeFraction` | 根据当前 component 的 `aVolume` 与 Mixture 总体积自动计算的体积分数 |
| `aAmountConcentration` | 根据 `bAmount` 和 Mixture 体积自动计算的物质的量浓度，标准单位为 `mol/m^3` |
| `aMassConcentration` | 根据 `aMass` 和 Mixture 体积自动计算的质量浓度，标准单位为 `kg/m^3` |

## 设计说明

Matter 负责描述物质单元自身的结构。MixtureComponent 负责描述该 Matter 在某个 Mixture 中出现了多少、如何分布、与其他 Matter 如何接触。

这样可以避免把同一个 Matter 因为数量不同而复制成多个不同 Matter。

`bMatter` 是 MixtureComponent 的定义属性，因为不同 Matter 会形成不同 component。实现时需要避免把 runtime object reference 直接放入 descriptor；descriptor 中可以保存 Matter 的 descriptor、Matter hash 或稳定的物质定义数据。

`bAmount` 是 MixtureComponent 的基础数量字段。`aMass`、`aVolume`、`aMoleFraction`、`aMassFraction`、`aVolumeFraction`、`aAmountConcentration` 和 `aMassConcentration` 都应由 `bAmount`、`bMatter` 和当前 Mixture 的整体状态自动计算，避免同一 component 中出现互相矛盾的数量输入。

## Mixture Type

`bMixtureType` 用于描述 Mixture 的宏观组织类型。不同类型的 Mixture 可以拥有不同的宏观属性和计算模型。

推荐类型：

| 类型 | 含义 | 典型额外属性 |
| --- | --- | --- |
| `solution` | 均一溶液 | 粘度、扩散系数、溶剂/溶质角色、浓度模型 |
| `granular` | 颗粒型混合物，例如沙子、粉末颗粒集合 | 总表面积、比表面积、粒径分布、孔隙率、颗粒接触网络 |
| `suspension` | 悬浊液 | 分散相粒径、沉降速度、分散稳定性、连续相粘度 |
| `emulsion` | 乳浊液 | 液滴尺寸分布、界面面积、乳化稳定性 |
| `powder` | 粉末体系 | 比表面积、堆积密度、粒径分布、流动性 |
| `melt` | 熔融混合物 | 粘度、扩散系数、温度依赖参数 |
| `gasMixture` | 气体混合物 | 分压、扩散系数、混合均匀性 |
| `custom` | 自定义类型 | 由具体模型定义 |

颗粒型 Mixture 不需要新增独立的宏观物质层级。以沙子为例，打散或聚集主要改变的是 Mixture 的宏观接触面积、比表面积、孔隙率和颗粒接触网络，而不是改变 Matter 的基础结构。Matter 仍描述二氧化硅晶胞或微观结构单元；Mixture 通过 `bMixtureType = "granular"` 以及类型相关属性描述沙堆的宏观状态。

`bMixtureTypeProperty` 推荐保存为可序列化 dict。不同 `bMixtureType` 对应不同 schema：

```python
{
    "specificSurfaceArea": "120.0",
    "specificSurfaceAreaUnit": "m^2/kg",
    "particleSizeDistribution": {
        "model": "range",
        "minDiameter": "0.0001",
        "maxDiameter": "0.001"
    },
    "porosity": "0.42"
}
```

进入 hash canonical payload 时，`bMixtureTypeProperty` 按 dict 的键名 ASCII 升序排列，并按 `units_and_precision.md` 的标准单位和精度规范化数值。

## Fraction Fields

比例字段描述当前 component 在整个 Mixture 中所占的份额。

- `aMoleFraction`：当前 component 的物质的量除以 Mixture 总物质的量。
- `aMassFraction`：当前 component 的质量除以 Mixture 总质量。
- `aVolumeFraction`：当前 component 的体积除以 Mixture 总体积。

这些字段用于反应推断、浓度计算、渲染表现和宏观性质估算。它们默认是 auto calculated property，不作为基础输入，避免与 `bAmount` 产生冲突。

## Concentration Fields

浓度字段用于描述 component 在当前 Mixture 中的数量密度。

- `aAmountConcentration`：物质的量浓度，标准单位为 `mol/m^3`。
- `aMassConcentration`：质量浓度，标准单位为 `kg/m^3`。

第一版文档中不再使用单一的 `aConcentration` 泛称，避免混淆“是哪一种浓度”。如果后续需要表示溶剂视角的摩尔比、质量百分浓度或其他专门浓度形式，应新增命名明确的 auto property。

## Spatial Fields

空间字段描述当前 component 在 Mixture 中如何分布，以及它如何与其他 component 接触。

- `bSpatialDistribution`：第一版限定为枚举字符串，只允许 `homogeneous`、`layered`、`suspended`、`granularRandom`、`phaseSeparated`。
- `bContactRelation`：第一版使用固定 schema 的可序列化结构，描述与其他 component 的接触关系。

空间字段会影响反应速率、界面反应、扩散、传热和渲染表现。它们不是 Matter 自身性质，而是某个 Matter 进入当前 Mixture 后形成的宏观组合关系。

推荐 `bContactRelation` schema：

```python
{
    "model": "pairwise",
    "relationList": [
        {
            "targetComponentHash": "<sha256>",
            "relationType": "interface",
            "contactArea": "1.200000000000e-06",
            "contactAreaUnit": "m^2"
        }
    ]
}
```

规范：

1. `relationList` 中的每个关系项都使用固定字段名。
2. `targetComponentHash` 使用目标 component 的 hash，而不是 `_id`。
3. `contactArea` 使用 decimal string，单位遵守 `units_and_precision.md`。
4. `relationList` 在进入 hash 前按 `targetComponentHash` 和 `relationType` 的 ASCII 升序排序。

## `List` 命名说明

`bMixtureComponentList` 中的 `List` 表示对象集合，不强制表示 Python `list`。当前推荐使用 `set[MixtureComponentLogic]` 实现，因为 Mixture 中的 component 更接近无序组成项。

进入 hash canonical payload 时，如果集合无序，需要转换成 MixtureComponent hash list，并按 hash 的 ASCII 升序排列。

## Matter And Mixture Example

以沙子为例：

- `Matter` 描述二氧化硅晶胞或统一微观结构单元。
- 沙堆可以表示为 `bMixtureType = "granular"` 的 Mixture。
- 沙砾变碎、颗粒变细或表面积增大，主要体现在 Mixture 的类型相关属性中，例如总表面积、比表面积、粒径分布和颗粒接触网络。

临时示意：

```text
Matter
└── SiO2CrystalCell

Mixture
└── sandPile
    ├── bMixtureType = "granular"
    ├── bMixtureComponentList = {componentForSiO2Matter}
    └── type properties = surface area, specific surface area, particle size distribution
```

这个例子用于区分：

```text
Matter = 最小或近似最小的统一结构单元
Mixture = 多个 Matter component 以及宏观组织类型共同构成的系统
MixtureComponent = 某个组成对象在当前 Mixture 中的条目
```

## Mapping Guide

第一版映射规则：

- 溶液：`bMixtureType = "solution"`，重点使用 `aAmountConcentration`、粘度、扩散系数和溶剂/溶质角色属性。
- 悬浊液：`bMixtureType = "suspension"`，重点使用分散相粒径、沉降速度、连续相粘度和空间分布。
- 粉末：`bMixtureType = "powder"`，重点使用比表面积、粒径分布、堆积密度和流动性。
- 沙堆：`bMixtureType = "granular"`，重点使用总表面积、比表面积、孔隙率和颗粒接触网络。
- 多相体系：根据主导宏观结构选择 `phaseSeparated` 空间分布，并结合 `solution`、`suspension`、`melt` 或 `gasMixture` 等具体 Mixture 类型。
