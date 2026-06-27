# AtomPresetDatabase

## 定义

`AtomPresetDatabase` 是 Atom / ion 能级的预制属性数据库。它用于辅助构造 Atom 实例，也用于未来可能对 Atom 类进行扩展。

这些预制原子属性数据不一定都要成为 Atom 的实例属性，但需要属于 `AtomPresetDatabase`，用于辅助构造或提供后续扩展所需的参考数据。

## CSV 结构

数据库格式暂定为 CSV：

```text
一行 = 一个元素
一列 = 一个属性
```

推荐数据文件路径：

```text
data/presets/atom_preset_database.csv
```

推荐加载器位置：

```text
src/matter_core/preset/atom_preset_database_loader.py
```

上述路径是文档设计约定，当前阶段不要求立即创建代码结构。

## CSV 字段

| 字段名 | 含义 | 格式 | Example |
| --- | --- | --- | --- |
| `symbol` | 元素符号，用于 `fromElementSymbol()` 检索元素 | string | `O` |
| `englishName` | 元素英文名，用于展示、搜索和调试 | string | `Oxygen` |
| `chineseName` | 元素中文名，用于展示、搜索和调试 | string | `氧` |
| `atomicNumber` | 原子序数，等于质子数 | int | `8` |
| `standardAtomicMass` | 标准原子量，作为相对原子质量使用 | decimal string | `15.999` |
| `defaultMassNumber` | 默认质量数，通常取最常见同位素 | int | `16` |
| `defaultElectronConfig` | 默认基态电子排布，用于自动填充 `bElectronConfig` | stringify JSON object | `"{\"1s\":[2],\"2s\":[2],\"2p\":[2,1,1]}"` |
| `commonMassNumbers` | 常见质量数，用于同位素 preset | stringify JSON list | `"[16,17,18]"` |
| `commonCharges` | 常见离子电荷，用于快速构造常见离子 | stringify JSON list | `"[-2,-1,0]"` |
| `commonOxidationStates` | 常见氧化态，用于反应推断和价态判断 | stringify JSON list | `"[-2,-1,0,1,2]"` |
| `ionizationEnergyList` | 多级电离能，用于判断失电子倾向；第 0 项为第一电离能，第 1 项为第二电离能，以此类推 | stringify JSON list，标准单位为 `J/mol` | `"[1313900,3388300]"` |
| `electronAffinityList` | 多级电子亲和能或得电子能量，用于判断得电子倾向；第 0 项为第一次得电子，第 1 项为第二次得电子，以此类推 | stringify JSON list，标准单位为 `J/mol` | `"[-141000,744000]"` |
| `isMetal` | 是否为金属元素，用于金属键、材料性质和反应推断 | bool string | `false` |
| `period` | 元素周期 | int | `2` |
| `family` | 元素族，用于周期律和同族性质推断 | string | `VIA` |
| `block` | 元素分区，用于电子排布和周期律推断 | string，`s`、`p`、`d`、`f` | `p` |

## JSON 字段

建议使用 stringify JSON 的 CSV 字段：

- `defaultElectronConfig`
- `commonMassNumbers`
- `commonCharges`
- `commonOxidationStates`
- `ionizationEnergyList`
- `electronAffinityList`

这些字段本质上是列表或字典。使用 stringify JSON 可以减少自定义解析规则，并方便加载器做格式校验。

## Energy Convention

`ionizationEnergyList` 和 `electronAffinityList` 的项目内部标准单位都是 `J/mol`。

`electronAffinityList` 的符号约定采用能量变化方向：

- 吸收能量为正。
- 释放能量为负。

如果外部数据库使用“释放能量记为正值”的约定，加载器需要在导入时转换为 MatterCraft 的内部标准。

如果某些元素或某些级数的数据不完整，可以只写一项或两项。项目中暂时只规定字段格式，不强行要求每个元素都完整填写多级数据。

## CSV Example Rows

以下示例用于说明 stringify JSON 在 CSV 中的写法。为简洁起见，这里只展示部分核心字段：

```csv
symbol,englishName,chineseName,atomicNumber,standardAtomicMass,defaultMassNumber,defaultElectronConfig,commonMassNumbers,commonCharges,commonOxidationStates,ionizationEnergyList,electronAffinityList,isMetal,period,family,block
H,Hydrogen,氢,1,1.008,1,"{""1s"":[1]}","[1,2,3]","[-1,0,1]","[-1,0,1]","[1312000]","[-72800]",false,1,IA,s
O,Oxygen,氧,8,15.999,16,"{""1s"":[2],""2s"":[2],""2p"":[2,1,1]}","[16,17,18]","[-2,-1,0]","[-2,-1,0,1,2]","[1313900,3388300]","[-141000,744000]",false,2,VIA,p
Na,Sodium,钠,11,22.98976928,23,"{""1s"":[2],""2s"":[2],""2p"":[2,2,2],""3s"":[1]}","[23]","[0,1]","[0,1]","[495800,4562000]","[52800]",true,3,IA,s
```

## Extension Strategy

关于“是否需要通过量子化学近似模型推断特定电子排布下的失电子或得电子能量”，第一版建议采用分阶段策略：

1. 第一阶段：完全依赖 `AtomPresetDatabase` 和外部可查表数据。
2. 第二阶段：当数据库缺项时，允许在 `Logic` 或 `Calculus` 层引入近似模型补值。
3. 第三阶段：如有需要，再引入环境相关修正，例如局域结构、电荷环境或激发态修正。

第一阶段不把量子化学近似模型作为核心依赖，这样可以让项目先建立稳定的数据基础和构造流程。
