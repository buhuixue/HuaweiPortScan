
import re
import os
import time
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()
data_file_name = filedialog.askopenfilename()
new_data_file_name = os.path.basename(data_file_name)
last_log_file_name = "new_"+new_data_file_name
#data_file_name = 'SW01.log'


def read(file_name: str = data_file_name) -> str:
    try:

        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            return str(data)
    except FileNotFoundError:
        print("文件路径或名称错误")
        print("文件名称:", data_file_name)


def assembled_data():
    log_data: str = read(data_file_name)
    first_data: list = ['/'.join((i[0].replace(" ", ""), i[1], i[-1])) for i in
                        re.findall("(.*?)/(\d+)/(\d+)", log_data)]
    need_data = []
    remove_data = []
    remove_data = list(set(first_data))
    remove_data.sort(key=first_data.index)
    # print(remove_data)
    # print(first_data)

    for data in remove_data:

        first_raw_data = re.findall(
            f"{data} .* ", log_data
        )
        # print(first_raw_data)
        status = first_raw_data[0].split(" ")
        status = [item for item in status if item]
        # print(status[0],status[1])

        end_raw_data = re.findall(
            f"{data} transceiver .*? Ordering Name", log_data, re.S
        )

        # print(end_raw_data)
        if end_raw_data:
            end_raw_data = end_raw_data[0].replace(
                "\n", "   "
            ).split("   ")
            end_raw_data = [item for item in end_raw_data if item]
            # print(end_raw_data)
            model = end_raw_data[0].split(" ")[0]
            # print(model)
            if status[0] == model:
                need_data.append(
                    (model, status[0], status[1], end_raw_data[4], end_raw_data[8]))
                # print(need_data)
            else:
                print("error")

    print("------读取完成，开始写入文本----")
    if not os.path.exists(last_log_file_name):  # 输出文件不存在时执行
        for data in need_data:
            last_data = "%-25s%-25s%-10s%-20s%-10s" % (
                data[0], data[1], data[2], data[3], data[4])
            print(last_data)
            with open("new_"+new_data_file_name, "a+", encoding="utf-8") as f:
                f.write(last_data + "\n")
    else:
        os.remove(last_log_file_name)
        for data in need_data:
            last_data = "%-25s%-25s%-10s%-20s%-10s" % (
                data[0], data[1], data[2], data[3], data[4])
            print(last_data)
            with open(last_log_file_name, "a+", encoding="utf-8") as f:
                f.write(last_data + "\n")

    time.sleep(1)
    print("-----------写入完成-----------")


if __name__ == '__main__':
    assembled_data()
