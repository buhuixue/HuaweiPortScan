import re
import csv
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


def read_file_content(file_path):
    """
    打开文件并读取文件内容。

    :param file_path: 文件路径
    :return: 文件内容字符串
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        return content
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def get_interface_status(log_data):
    """
    处理数据，提取接口名，然后去重排序。
    """

    first_data = [
        "/".join((i[0].replace(" ", ""), i[1], i[-1]))
        for i in re.findall(r"(.*?)/(\d+)/(\d+)[^\S*]", log_data)
    ]
    # 去重
    remove_data = list(set(first_data))
    # 排序
    remove_data.sort(key=first_data.index)
    status_dict = {}
    # 通过接口名匹配原始数据中带有接口状态的行
    for data in remove_data:
        if data:
            interface_status_raw_data = re.findall(rf"{data}.*", log_data)
            interface_status = [
                item for item in interface_status_raw_data[0].split(" ") if item
            ]  # ['XGigabitEthernet4/0/19', '*down', 'down', '0%', '0%', '0', '0']
            status_dict[data] = interface_status[1]
    return status_dict


def get_optical_module_info(log_data):
    """
    处理数据，得到光模块信息
    """
    optical_module_info = []
    optical_module = list(
        re.finditer(r'(([A-Za-z0-9\-_]+(?:/\d+)+)\s+transceiver\s+information:)', log_data)
    )
    for i, match in enumerate(optical_module):
        interface = match.group(1).strip().replace(" transceiver information:", "")

        # 确定光模块信息的起始位置
        content_start = match.end()
        content_end = (
            optical_module[i + 1].start()
            if i + 1 < len(optical_module)
            else len(log_data)
        )
        content = log_data[content_start:content_end].strip()

        # 提取波长
        Wavelength = re.search(r"Wavelength\(nm\)\s*:\s*(\d+)", content)
        # 提取收光范围
        Rx_low = re.search(
            r"Default Rx Power Low\s+Threshold\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )
        Rx_high = re.search(
            r"Default Rx Power High Threshold\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )
        # 提取发光范围
        Tx_low = re.search(
            r"Default Tx Power Low\s+Threshold\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )
        Tx_high = re.search(
            r"Default Tx Power High Threshold\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )
        # 提取当前收光
        current_rx_power = re.search(
            r"Current Rx Power\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )
        # 提取当前发光
        current_tx_power = re.search(
            r"Current Tx Power\(dBM\)\s*:\s*(-?\d+\.\d+)", content
        )

        optical_module_info.append(
            {
                "interface": interface,
                "wavelength": Wavelength.group(1) if Wavelength else None,
                "rx_low": Rx_low.group(1) if Rx_low else None,
                "rx_high": Rx_high.group(1) if Rx_high else None,
                "tx_low": Tx_low.group(1) if Tx_low else None,
                "tx_high": Tx_high.group(1) if Tx_high else None,
                "current_rx_power": (
                    current_rx_power.group(1) if current_rx_power else None
                ),
                "current_tx_power": (
                    current_tx_power.group(1) if current_tx_power else None
                ),
            }
        )
        # print(optical_module_info)
    return optical_module_info


def evaluate_abnormal(
    rx_low, rx_high, tx_low, tx_high, current_rx_power, current_tx_power
):
    """
    评估光模块当前光功率是否在范围内。
    """
    try:
        rx_low = float(rx_low)
        rx_high = float(rx_high)
        tx_low = float(tx_low)
        tx_high = float(tx_high)
        current_rx_power = float(current_rx_power)
        current_tx_power = float(current_tx_power)

        if not (rx_low <= current_rx_power <= rx_high):
            return "收光异常"
        if not (tx_low <= current_tx_power <= tx_high):
            return "发光异常"
        return "光模块收发光正常"
    except:
        return "处理数据出错"


def merge_data(optical_list, status_dict):
    meraged_result = []
    for item in optical_list:
        interface = item["interface"]
        status = status_dict.get(interface, {"Unknown"})

        # 判断接口是否为*DOWN状态
        if status == "*down":
            abnormal = "接口shutdown"  # 人为关闭的接口不做进一步检查
        else:
            # 进行光功率范围检查

            abnormal = evaluate_abnormal(
                item["rx_low"],
                item["rx_high"],
                item["tx_low"],
                item["tx_high"],
                item["current_rx_power"],
                item["current_tx_power"],
            )
        meraged_result.append(
            {
                "interface": interface,
                "status": status,
                "wavelength": item["wavelength"],
                "rx_low": item["rx_low"],
                "rx_high": item["rx_high"],
                "current_rx_power": item["current_rx_power"],
                "tx_low": item["tx_low"],
                "tx_high": item["tx_high"],
                "current_tx_power": item["current_tx_power"],
                "abnormal": abnormal,
            }
        )
    return meraged_result


def export_to_csv(data_list, file_name="optical_module_info.csv"):
    """
    将光模块信息导出到CSV文件。
    """
    headers = [
        "interface",
        "status",
        "wavelength",
        "rx_low",
        "rx_high",
        "current_rx_power",
        "tx_low",
        "tx_high",
        "current_tx_power",
        "abnormal",
    ]
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
        print(f"数据已导出到 {file_name}")


def choose_file_and_export():
    """
    文件对话框和导出处理后的数据
    """

    Tk().withdraw()  # 隐藏主窗口
    input_file = askopenfilename(
        title="选择日志文件", filetypes=[("Log files", "*.log"), ("All files", "*.*")]
    )

    if not input_file:
        print("未选择文件，程序退出。")
        return

    # 读取文件内容
    log_data = read_file_content(input_file)

    # 提取数据
    status_dict = get_interface_status(log_data)
    optical_list = get_optical_module_info(log_data)
    merged_data = merge_data(optical_list, status_dict)
    # 导出到CSV
    output_file = asksaveasfilename(
        title="保存 CSV 文件",
        defaultextension=".csv",
        initialfile="output.csv",
        filetypes=[("CSV files", "*.csv")],
    )

    if not output_file:
        print("未选择保存文件路径，程序退出。")
        return
    # 导出数据到csv
    export_to_csv(merged_data, output_file)


if __name__ == "__main__":
    choose_file_and_export()