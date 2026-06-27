# Units And Precision

## 目标

本文件定义 MatterCraft 中基础物理量和化学量的标准单位与标准精度。这些规则不仅用于 `hash()` 前的数值规范化，也用于整个项目中的数据存储、计算、文档和 preset database。

## 通用规则

1. 项目内部计算优先使用 SI 单位或 SI 兼容单位。
2. 所有进入 `hash()` 的浮点量必须先转换为本文件规定的标准单位。
3. 所有进入 `hash()` 的浮点量必须按本文件规定的精度量化，并转为稳定 decimal string。
4. 文档或 UI 可以展示更适合人类阅读的单位，但内部 descriptor 和 hash canonical payload 必须使用标准单位。
5. 当某个字段没有出现在本文件中时，实现前必须先补充单位与精度规范。

## 标准量表

| 量 | 标准单位 | hash 精度 | 说明 |
| --- | --- | --- | --- |
| `amount` | `mol` | `1e-12 mol` | 物质的量，例如 `bAmount` |
| `mass` | `kg` | `1e-12 kg` | 质量，例如 `aMass` |
| `volume` | `m^3` | `1e-15 m^3` | 体积，例如 `aVolume` |
| `time` | `s` | `1e-9 s` | 时间 |
| `length` | `m` | `1e-12 m` | 通用长度 |
| `position` | `m` | `1e-12 m` | 空间位置 |
| `velocity` | `m/s` | `1e-9 m/s` | 速度 |
| `acceleration` | `m/s^2` | `1e-9 m/s^2` | 加速度 |
| `force` | `N` | `1e-12 N` | 力 |
| `bondLength` | `m` | `1e-13 m` | 键长，例如 `bBondLength` |
| `moleculeGap` | `m` | `1e-12 m` | 分子间距，例如 `bPhyMoleculeGap` |
| `area` | `m^2` | `1e-18 m^2` | 接触面积、表面积 |
| `specificSurfaceArea` | `m^2/kg` | `1e-9 m^2/kg` | 比表面积 |
| `surfaceAreaVolumeRatio` | `1/m` | `1e-3 1/m` | 表面积与体积之比 |
| `energy` | `J` | `1e-21 J` | 单个对象或事件能量 |
| `molarEnergy` | `J/mol` | `1e-3 J/mol` | 键能、电离能、电子亲和能 |
| `charge` | `e` | integer | 原子或离子的形式电荷，例如 `bCharge` |
| `electricCharge` | `C` | `1e-24 C` | 真实电荷量 |
| `temperature` | `K` | `1e-6 K` | 温度 |
| `pressure` | `Pa` | `1e-3 Pa` | 压强 |
| `density` | `kg/m^3` | `1e-9 kg/m^3` | 密度 |
| `dynamicViscosity` | `Pa*s` | `1e-9 Pa*s` | 动力粘度 |
| `concentrationAmount` | `mol/m^3` | `1e-9 mol/m^3` | 物质的量浓度 |
| `massConcentration` | `kg/m^3` | `1e-9 kg/m^3` | 质量浓度 |
| `diffusionCoefficient` | `m^2/s` | `1e-18 m^2/s` | 扩散系数 |
| `reactionRate` | `mol/(m^3*s)` | `1e-12 mol/(m^3*s)` | 体积反应速率 |
| `fraction` | dimensionless | `1e-12` | 摩尔分数、质量分数、体积分数 |
| `angle` | `rad` | `1e-12 rad` | 角度 |
| `bondOrder` | dimensionless | `1e-6` | 键级，允许非整数 |
| `polarity` | dimensionless | `1e-12` | 极性描述值，具体模型后续定义 |
| `electronCount` | electron | integer | 电子数 |
| `atomicNumber` | proton | integer | 原子序数 |
| `massNumber` | nucleon | integer | 质量数 |

## Decimal String

进入 descriptor 或 hash canonical payload 的浮点值应使用 decimal string 表示。

示例：

```json
{
  "bBondLength": "1.200000000000e-10",
  "bBondEnergy": "4.130000000000e+05"
}
```

推荐实现规则：

1. 先转换为标准单位。
2. 按字段精度进行量化。
3. 使用固定格式输出 decimal string。
4. 禁止直接把二进制浮点值写入 hash canonical payload。

## Preset Database Units

AtomPresetDatabase 中的能量字段也应遵守本文件的单位规范。

- `ionizationEnergyList`：标准单位为 `J/mol`。
- `electronAffinityList`：标准单位为 `J/mol`。

如果外部数据库使用 `kJ/mol`、`eV` 或其他单位，加载器需要在进入项目内部数据结构前统一转换为标准单位。
