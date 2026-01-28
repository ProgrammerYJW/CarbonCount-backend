import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
from rasterio.sample import sample_gen
import os
import json
import sys
import numpy as np

# --- 服务器路径配置 ---
FLUX_FILE_PATH = "/var/www/carbon_count/scripts/30N_110E.tif"
# FLUX_FILE_PATH = "C:\\Users\\HP\\Desktop\\30N_110E.tif"


def parse_location_to_geojson(location_str: str) -> dict:
    """
    将 "lng,lat;lng,lat;..." 字符串转为 GeoJSON Polygon
    """
    if not location_str:
        raise ValueError("location 字符串为空")

    coords_list = []
    for point in location_str.strip().split(";"):
        if not point.strip():
            continue
        lng, lat = map(float, point.split(","))
        coords_list.append([lng, lat])

    # 闭合多边形（首尾相同）
    if coords_list and coords_list[0] != coords_list[-1]:
        coords_list.append(coords_list[0])

    return {
        "type": "Polygon",
        "coordinates": [coords_list]
    }


class extract_net_carbon_emission:

    def get_net_carbon_emission_from_polygon(self,user_geojson):
        """
        生产模式：根据多边形区域提取净碳排放量
        """
        if not os.path.exists(FLUX_FILE_PATH):
            return {"error": "净碳排放量数据文件不存在"}

        try:
            with rasterio.open(FLUX_FILE_PATH) as src:
                # 坐标对齐：将WGS84经纬度转为影像原生的投影坐标
                projected_geom = transform_geom('EPSG:4326', src.crs, user_geojson)

                # 执行裁剪
                out_image, out_transform = mask(src, [projected_geom], crop=True, all_touched=True)
                data = out_image[0]  # 第一波段包含净碳排放量数据

                # 更严格的无效值过滤
                # 1. 排除明确的nodata值
                if src.nodata is not None:
                    valid_mask = data != src.nodata
                else:
                    valid_mask = np.ones(data.shape, dtype=bool)

                # 2. 排除NaN值
                valid_mask = valid_mask & ~np.isnan(data)

                # 3. 排除其他可能的无效值
                valid_mask = valid_mask & (data > -9999) & (data != 0)

                # 提取有效像元
                valid_pixels = data[valid_mask]

                print(f"DEBUG: 严格过滤后的有效像素数量: {valid_pixels.size}", file=sys.stderr)

                if valid_pixels.size == 0:
                    # 尝试使用自检模式的点采样方法作为备选方案
                    print("DEBUG: 没有找到有效像素，尝试点采样备选方案", file=sys.stderr)
                    return extract_net_carbon_emission.self_test_for_production(user_geojson)

                # 计算区域内的平均值
                mean_flux = valid_pixels.mean()

                # 应用原始换算逻辑
                annual_net_flux = mean_flux / 24
                annual_absorption = -annual_net_flux if annual_net_flux < 0 else 0

                result = {
                    "cumulative_24yr": round(float(mean_flux), 2),
                    "annual_absorption": round(float(annual_absorption), 4)
                }

                print(f"DEBUG: 最终结果: {result}", file=sys.stderr)
                return result

        except Exception as e:
            print(f"DEBUG: 异常信息: {str(e)}", file=sys.stderr)
            return {"error": f"数据处理错误: {str(e)}"}


    def self_test_for_production(user_geojson):
        """
        生产模式下的备选方案：使用点采样方法
        """
        try:
            # 提取多边形中心点进行采样
            coordinates = user_geojson["coordinates"][0]

            # 计算多边形中心点
            lons = [coord[0] for coord in coordinates]
            lats = [coord[1] for coord in coordinates]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)

            with rasterio.open(FLUX_FILE_PATH) as src:
                # 使用点采样
                sample_values = list(sample_gen(src, [(center_lon, center_lat)], 1))
                if not sample_values:
                    return {"error": "点采样也无有效数据"}

                raw_value = sample_values[0][0]
                raw_value1 = raw_value*(-1)
                # 数据清洗
                if np.isnan(raw_value) or raw_value == src.nodata or raw_value < -9999:
                    return {"error": "点采样数据无效"}

                # 应用原始换算逻辑
                annual_net_flux = raw_value / 24
                annual_absorption = -annual_net_flux if annual_net_flux < 0 else 0

                result = {
                    "cumulative_24yr": round(float(raw_value1), 2),
                    "annual_absorption": round(float(annual_absorption), 4)
                }

                print(f"DEBUG: 点采样备选方案结果: {result}", file=sys.stderr)
                return result

        except Exception as e:
            print(f"DEBUG: 点采样备选方案异常: {str(e)}", file=sys.stderr)
            return {"error": f"点采样备选方案失败: {str(e)}"}


    def self_test(self):
        """
        自检模式：完全按照原始程序的输出格式
        """
        print("--- 正在启动净碳排放量提取程序自检 ---")
        if not os.path.exists(FLUX_FILE_PATH):
            print("❌ 错误：未找到净碳排放量数据文件")
            return

        # 使用原始程序的固定坐标点
        points_to_check = [
            ("肇庆鼎湖山森林", 112.511, 23.169),
            ("韶关南岭林区", 112.952, 24.851)
        ]

        print(f"统计时间跨度: 2001-2024 (共24年)")
        print("--------------------------------------------------")

        try:
            with rasterio.open(FLUX_FILE_PATH) as src:
                for location_name, lon, lat in points_to_check:
                    # 使用原始程序的点采样方法
                    sample_value = list(sample_gen(src, [(lon, lat)], 1))
                    if not sample_value:
                        print(f"📍 {location_name}: 该坐标无有效数据")
                        print("------------------------------")
                        continue

                    raw_value = sample_value[0][0]
                    raw_value1 = raw_value * (-1)

                    # 数据清洗：排除无效值
                    if np.isnan(raw_value) or raw_value == src.nodata or raw_value < -9999:
                        print(f"📍 {location_name}: 该坐标无有效数据 (可能在海里或超出范围)")
                        print("------------------------------")
                        continue

                    # 核心换算逻辑（与原始程序完全一致）
                    annual_net_flux = raw_value / 24
                    annual_absorption = -annual_net_flux if annual_net_flux < 0 else 0

                    # 完全按照原始程序的输出格式
                    print(f"📍 地点: {location_name}")
                    print(f"   二十四年累积净碳吸收量: {raw_value1:.2f} Mg CO2e/ha")
                    print(f"   平均每年净碳吸收量: {annual_absorption:.4f} tCO2e/ha/yr")
                    print("------------------------------")

        except Exception as e:
            print(f"读取失败: {e}")

    # --- 程序入口 ---
    def extract(self,arg):
        try:
            print(f"DEBUG: 接收参数: {arg}", file=sys.stderr)

            input_geojson = None

            # ✅ 修复：不再强行 json.loads，而是智能判断
            if isinstance(arg, str):
                # 如果是 location 字符串（含逗号分隔的坐标对）
                if "," in arg and ";" in arg:
                    print("DEBUG: 检测到 location 字符串格式，转为 GeoJSON", file=sys.stderr)
                    input_geojson = parse_location_to_geojson(arg)
                else:
                    # 尝试作为 JSON 解析（兼容旧逻辑）
                    try:
                        print("DEBUG: 尝试解析为 JSON", file=sys.stderr)
                        input_geojson = json.loads(arg)
                    except json.JSONDecodeError:
                        raise ValueError(f"无法解析输入参数 '{arg}'：既不是 location 字符串，也不是有效 JSON")
            else:
                input_geojson = arg

            if input_geojson is None:
                raise ValueError("无法解析输入参数")

            final_output = self.get_net_carbon_emission_from_polygon(input_geojson)
            # ✅ 关键：返回 Python 对象，不要 json.dumps！
            return final_output

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            print(f"DEBUG: {error_msg}", file=sys.stderr)
            print(json.dumps({"error": error_msg}, ensure_ascii=False))
        except Exception as e:
            error_msg = f"输入处理错误: {str(e)}"
            print(f"DEBUG: {error_msg}", file=sys.stderr)
            print(json.dumps({"error": error_msg}, ensure_ascii=False))

# 自检模式
if __name__ == "__main__":
    extract = extract_net_carbon_emission()
    extract_net_carbon_emission.self_test(extract)