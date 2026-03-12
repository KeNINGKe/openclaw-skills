"""
手机信令数据可视化和统计脚本
生成热力图、统计表
"""
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
import os
import sys
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def load_gdf(path):
    """加载 GeoDataFrame 并转换为 WGS84"""
    return gpd.read_file(path).to_crs("EPSG:4326")


def draw_heatmap(df, title, filename, lon_col, lat_col, color, region, city, lines, stations, output_folder):
    """绘制热力图"""
    if df.empty:
        print(f"⚠️ 警告：{filename} 数据为空，跳过绘图。")
        return

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326").to_crs(epsg=3857)
    x, y = gdf.geometry.x.values, gdf.geometry.y.values

    city_plot = city.to_crs(epsg=3857)
    region_plot = region.to_crs(epsg=3857)
    lines_plot = lines.to_crs(epsg=3857)
    stations_plot = stations.to_crs(epsg=3857)

    x_min, y_min, x_max, y_max = city_plot.total_bounds
    grid_size = 300
    x_edges = np.arange(x_min, x_max + grid_size, grid_size)
    y_edges = np.arange(y_min, y_max + grid_size, grid_size)
    heatmap, _, _ = np.histogram2d(x, y, bins=[x_edges, y_edges])
    heatmap_smooth = gaussian_filter(heatmap, sigma=1.0)
    log_heatmap = np.log1p(heatmap_smooth)
    cmap = LinearSegmentedColormap.from_list("cmap", ["white", color])

    fig, ax = plt.subplots(figsize=(30, 30), facecolor="white")
    im = ax.imshow(log_heatmap.T, extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                   origin="lower", cmap=cmap, alpha=1.0, vmin=0, vmax=log_heatmap.max(), interpolation="nearest", zorder=1)
    city_plot.boundary.plot(ax=ax, edgecolor="black", linewidth=0.8, zorder=2)
    region_plot.boundary.plot(ax=ax, edgecolor="red", linewidth=2.0, zorder=3)
    lines_plot.plot(ax=ax, color="black", linewidth=1.5, alpha=0.8, zorder=4)
    stations_plot.plot(ax=ax, markersize=20, color="white", edgecolor="black", linewidth=1.2, zorder=5)
    ax.set_title(title, fontsize=30)
    ax.set_axis_off()
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Log-scaled density", fontsize=20)
    plt.savefig(f"{output_folder}/{filename}", dpi=300, bbox_inches="tight")
    plt.close()


def spatial_count(df, lon_col, lat_col, time_label, type_label, streets, city, region_name, output_folder):
    """空间统计：按街道、区统计出行量"""
    if df.empty:
        print(f"⚠️ 警告：{type_label}_{time_label} 数据为空，跳过统计。")
        return

    gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326")

    # 街道统计
    gdf_street_join = gpd.sjoin(gdf_points, streets, how="inner", predicate="within")
    street_name_fields = ["NAME", "街道名称", "name"]
    street_field = next((f for f in street_name_fields if f in gdf_street_join.columns), None)
    if street_field:
        street_counts = gdf_street_join.groupby(street_field).size().reset_index(name="count").sort_values("count", ascending=False)
        street_counts.to_excel(f"{output_folder}/{region_name}{time_label}{type_label}_街道.xlsx", index=False)

    # 区统计
    gdf_region_join = gpd.sjoin(gdf_points, city, how="inner", predicate="within")
    region_name_fields = ["NAME", "name", "区域名", "区名称"]
    region_field = next((f for f in region_name_fields if f in gdf_region_join.columns), None)
    if region_field:
        region_counts = gdf_region_join.groupby(region_field).size().reset_index(name="count").sort_values("count", ascending=False)
        region_counts.to_excel(f"{output_folder}/{region_name}{time_label}{type_label}_区.xlsx", index=False)
    else:
        summary = pd.DataFrame({"统计对象": ["总计"], "数量": [len(gdf_region_join)]})
        summary.to_excel(f"{output_folder}/{region_name}{time_label}{type_label}_区.xlsx", index=False)


def process_od_data(csv_file, point_type, region_name, region, city, streets, lines, stations, output_folder):
    """处理单个 OD 数据文件"""
    df = pd.read_csv(csv_file, parse_dates=["O_time"])
    is_O = point_type == "O"
    type_label = "客流目的" if is_O else "客流来源"
    heat_color = "blue" if is_O else "red"

    df_morning = df[df["O_time"].dt.hour.between(7, 9)]

    if is_O:
        gdf_d = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["D_lon"], df["D_lat"]), crs="EPSG:4326")
        gdf_d_morning = gpd.GeoDataFrame(df_morning, geometry=gpd.points_from_xy(df_morning["D_lon"], df_morning["D_lat"]), crs="EPSG:4326")
        df_all_out = df[~gdf_d.within(region.unary_union)]
        df_morning_out = df_morning[~gdf_d_morning.within(region.unary_union)]
        heat_lon_col, heat_lat_col = "D_lon", "D_lat"

        # 绘制出发地热力图（红色）
        draw_heatmap(df, f"{region_name}全日出发地热力图", f"{point_type}点在区域_全日原始热力图.png", 
                     "O_lon", "O_lat", "red", region, city, lines, stations, output_folder)

    else:
        gdf_o = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["O_lon"], df["O_lat"]), crs="EPSG:4326")
        gdf_o_morning = gpd.GeoDataFrame(df_morning, geometry=gpd.points_from_xy(df_morning["O_lon"], df_morning["O_lat"]), crs="EPSG:4326")
        df_all_out = df[~gdf_o.within(region.unary_union)]
        df_morning_out = df_morning[~gdf_o_morning.within(region.unary_union)]
        heat_lon_col, heat_lat_col = "O_lon", "O_lat"

        # 绘制目的地热力图（蓝色）
        draw_heatmap(df, f"{region_name}全日目的地热力图", f"{point_type}点在区域_全日原始热力图.png", 
                     "D_lon", "D_lat", "blue", region, city, lines, stations, output_folder)

    # 保存 CSV
    df.to_csv(f"{output_folder}/{point_type}点在区域_全日.csv", index=False)
    df_morning.to_csv(f"{output_folder}/{point_type}点在区域_早高峰.csv", index=False)
    df_all_out.to_csv(f"{output_folder}/{point_type}点在区域_全日_对外.csv", index=False)
    df_morning_out.to_csv(f"{output_folder}/{point_type}点在区域_早高峰_对外.csv", index=False)

    title_all = f"{region_name}全日{type_label}地"
    title_morning = f"{region_name}早高峰{type_label}地"
    draw_heatmap(df_all_out, title_all, f"{point_type}点在区域_全日_对外_heatmap.png", 
                 heat_lon_col, heat_lat_col, heat_color, region, city, lines, stations, output_folder)
    draw_heatmap(df_morning_out, title_morning, f"{point_type}点在区域_早高峰_对外_heatmap.png", 
                 heat_lon_col, heat_lat_col, heat_color, region, city, lines, stations, output_folder)

    # 空间统计
    spatial_count(df_all_out, heat_lon_col, heat_lat_col, time_label="全日", type_label=type_label, 
                  streets=streets, city=city, region_name=region_name, output_folder=output_folder)
    spatial_count(df_morning_out, heat_lon_col, heat_lat_col, time_label="早高峰", type_label=type_label, 
                  streets=streets, city=city, region_name=region_name, output_folder=output_folder)

    return {
        "类型": f"{point_type}点在区域",
        "全日出行量": len(df),
        "全日对外出行量": len(df_all_out),
        "早高峰出行量": len(df_morning),
        "早高峰对外出行量": len(df_morning_out)
    }


def visualize_region(region_name, project_folder):
    """可视化单个区域"""
    project_path = Path(project_folder)
    
    # 加载基础地理数据
    region_shp = project_path / f"{region_name}.shp"
    city_shp = project_path / "beijing.shp"
    street_shp = project_path / "北京街道.shp"
    rail_shp = project_path / "既有线.shp"
    station_shp = project_path / "站点2025.shp"
    
    if not all([region_shp.exists(), city_shp.exists(), street_shp.exists(), rail_shp.exists(), station_shp.exists()]):
        print(f"⚠️ 缺少必要的 shp 文件，跳过区域 {region_name}")
        return
    
    region = load_gdf(region_shp)
    streets = load_gdf(street_shp)
    city = load_gdf(city_shp)
    lines = load_gdf(rail_shp)
    stations = load_gdf(station_shp)
    
    # 创建输出文件夹
    output_folder = project_path / region_name
    os.makedirs(output_folder, exist_ok=True)
    
    # 处理 O 点和 D 点数据
    summary_list = []
    
    csv_o = project_path / f"df_o_{region_name}.csv"
    csv_d = project_path / f"df_d_{region_name}.csv"
    
    if csv_o.exists():
        print(f"\n处理 {region_name} - O 点数据")
        summary_list.append(process_od_data(csv_o, "O", region_name, region, city, streets, lines, stations, output_folder))
    
    if csv_d.exists():
        print(f"\n处理 {region_name} - D 点数据")
        summary_list.append(process_od_data(csv_d, "D", region_name, region, city, streets, lines, stations, output_folder))
    
    # 保存汇总统计
    if summary_list:
        summary_df = pd.DataFrame(summary_list)
        summary_df.to_excel(f"{output_folder}/汇总统计_{region_name}.xlsx", index=False)
    
    print(f"✅ {region_name} 处理完成，结果已保存到：{output_folder}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python visualize.py <region_name> <project_folder>")
        sys.exit(1)
    
    region_name = sys.argv[1]
    project_folder = sys.argv[2]
    visualize_region(region_name, project_folder)
