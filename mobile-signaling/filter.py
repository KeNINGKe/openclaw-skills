"""
手机信令数据筛选脚本
根据多个 shp 区域文件，筛选 O 点或 D 点在区域内的记录
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path
import sys

def filter_od_data(csv_path, project_folder):
    """
    筛选 OD 数据
    
    Args:
        csv_path: 原始 CSV 文件路径
        project_folder: 项目文件夹路径（包含 shp 文件）
    """
    # 1. 读取原始数据
    df = pd.read_csv(csv_path)
    print(f"原始数据条数: {len(df)}")
    
    # 2. 查找所有区域 shp 文件（排除辅助文件）
    project_path = Path(project_folder)
    exclude_files = {"beijing.shp", "北京街道.shp", "既有线.shp", "站点2025.shp"}
    region_files = [f for f in project_path.glob("*.shp") if f.name not in exclude_files]
    
    if not region_files:
        print("⚠️ 未找到区域 shp 文件")
        return
    
    print(f"找到 {len(region_files)} 个区域文件")
    
    # 3. 遍历每个区域
    for shp_file in region_files:
        region_name = shp_file.stem  # 文件名（不含后缀）
        print(f"\n处理区域：{region_name}")
        
        # 3.1 读取区域 shp 并投影
        region = gpd.read_file(shp_file)
        if region.crs != "EPSG:4326":
            region = region.to_crs(epsg=4326)
        
        # -----------------------
        # O 点处理（spatial join）
        # -----------------------
        print("  → 正在处理 O 点（spatial join）...")
        gdf_o = gpd.GeoDataFrame(
            df.copy(), 
            geometry=gpd.points_from_xy(df["O_lon"], df["O_lat"]),
            crs="EPSG:4326"
        )
        joined_o = gpd.sjoin(gdf_o, region, predicate="within", how="inner")
        joined_o.drop(columns=["index_right"], inplace=True, errors='ignore')
        out_path_o = project_path / f"df_o_{region_name}.csv"
        joined_o.to_csv(out_path_o, index=False)
        print(f"  ✓ 已保存 O 点：{out_path_o}，共 {len(joined_o)} 条")
        
        # -----------------------
        # D 点处理（spatial join）
        # -----------------------
        print("  → 正在处理 D 点（spatial join）...")
        gdf_d = gpd.GeoDataFrame(
            df.copy(), 
            geometry=gpd.points_from_xy(df["D_lon"], df["D_lat"]),
            crs="EPSG:4326"
        )
        joined_d = gpd.sjoin(gdf_d, region, predicate="within", how="inner")
        joined_d.drop(columns=["index_right"], inplace=True, errors='ignore')
        out_path_d = project_path / f"df_d_{region_name}.csv"
        joined_d.to_csv(out_path_d, index=False)
        print(f"  ✓ 已保存 D 点：{out_path_d}，共 {len(joined_d)} 条")
    
    print("\n✅ 所有区域筛选完成！")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python filter.py <csv_path> <project_folder>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    project_folder = sys.argv[2]
    filter_od_data(csv_path, project_folder)
