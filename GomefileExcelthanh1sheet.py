import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Mở cửa sổ chọn thư mục
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính

folder_path = filedialog.askdirectory(title="Chọn thư mục chứa file Excel")  # Hộp thoại chọn thư mục

if not folder_path:
    print("Không có thư mục nào được chọn. Thoát chương trình.")
    exit()

# Đặt tên file output
output_file = os.path.join(folder_path, "Merged.xlsx")

# Tạo file Excel mới
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for file in os.listdir(folder_path):
        if file.endswith(".xlsx") and not file.startswith("~$"):  # Bỏ qua file tạm của Excel
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path, sheet_name=None)  # Đọc tất cả sheet trong file

            # Nếu file có nhiều sheet, lấy từng sheet
            for sheet_name, sheet_data in df.items():
                new_sheet_name = f"{os.path.splitext(file)[0]}"  # Dùng tên file làm tên sheet
                sheet_data.to_excel(writer, sheet_name=new_sheet_name, index=False)

print(f"Gộp file thành công! File đã lưu tại: {output_file}")
