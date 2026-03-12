# mobile-signaling skill

手机信令 OD 数据处理：空间筛选、热力图可视化、统计导出。

## 触发条件
- 用户提到"手机信令"、"OD 数据"、"出行数据"、"信令处理"
- 用户提供 CSV 数据文件路径并要求处理

## 功能
1. **数据筛选**：根据多个 shp 区域文件，筛选 O 点或 D 点在区域内的记录
2. **热力图生成**：全日/早高峰的出行热力图（对数尺度 + 高斯平滑）
3. **统计导出**：按街道、区统计出行量，输出 Excel
4. **对外出行分析**：识别跨区域出行（O 在区域内但 D 在区域外，或反过来）

## 使用方式
用户提供：
- 原始 CSV 文件路径（包含 O_lon, O_lat, D_lon, D_lat, O_time 列）
- 项目文件夹路径（包含所有 shp 文件）

Skill 会：
1. 运行数据筛选脚本（filter.py）
2. 对每个区域运行可视化脚本（visualize.py）
3. 输出结果到项目文件夹

## 依赖
- pandas, geopandas, shapely, scipy, matplotlib
- 用户需自行确保环境已安装

## 文件结构
```
mobile-signaling/
  SKILL.md          # 本文件
  filter.py         # 数据筛选脚本
  visualize.py      # 可视化和统计脚本
```

## 执行流程
1. 读取用户提供的 CSV 路径和项目文件夹路径
2. 在项目文件夹中查找所有 .shp 文件（排除 beijing.shp, 北京街道.shp, 既有线.shp, 站点2025.shp）
3. 运行 filter.py 生成 df_o_*.csv 和 df_d_*.csv
4. 对每个区域运行 visualize.py 生成热力图和统计表
5. 汇总结果并告知用户

## 注意事项
- shp 文件命名即为区域名称（不含 .shp 后缀）
- 项目文件夹必须包含：beijing.shp, 北京街道.shp, 既有线.shp, 站点2025.shp
- 早高峰时段固定为 7:00-9:00
- 热力图颜色：O 点热力图用红色，D 点热力图用蓝色
