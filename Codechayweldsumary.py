import pyautogui
import time

T3 = 0.2  # thời gian chờ giữa các thao tác
T4 =0.6
T5=2 # thời gian đợi tối đang khi không thấy màu
n = 99  # số lần lặp lại

for i in range(n):
    # Copy số summary report từ Excel
    pyautogui.click(115, 248)
    time.sleep(T3)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(T3)

    # Click mũi tên xuống 1 dòng trong Excel
    pyautogui.click(1907, 968)
    time.sleep(T3)

    # Click qua PMS
    pyautogui.click(953, 1049)
    time.sleep(T4)

    # Click vào filter Summary Report No
    pyautogui.click(1887, 170)
    time.sleep(T3)
    pyautogui.click(1792, 197)  # custom
    time.sleep(T3)
    pyautogui.click(1055, 495)  # ô tìm kiếm
    time.sleep(T3)

    # Chọn tất cả, paste số vào
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(T3)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(T3)
    pyautogui.click(998, 605)  # OK
    time.sleep(T3)

    # View reports
    pyautogui.click(1525, 91)
    time.sleep(T3)
    pyautogui.click(1565, 213)
    time.sleep(T3)
    # Đợi khi có màu xanh để click Yes, paste, rồi Save
    #start_time = time.time()
   # while True:
        #color3 = pyautogui.pixel(883, 589)
        #if color3 == (227, 227, 227):
           #time.sleep(T3)
            #pyautogui.click(1026, 588)  # Click Yes
            #time.sleep(T3)
           # break
        #elif time.time() - start_time > T5:
            #break
        
    # Đợi khi có màu xanh để click Yes, paste, rồi Save
    while True:
        color1 = pyautogui.pixel(1536, 248)
        if color1 == (234, 220, 231):
            time.sleep(T3)
            pyautogui.click(514, 92)  # Click export excel
            break
    while True:
        color1 = pyautogui.pixel(263, 820)
        if color1 == (240, 240, 240):
            time.sleep(T3)
            pyautogui.click(360, 713)  # Click chổ tên
            time.sleep(T3)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(T3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(T3)
            pyautogui.click(1091, 814)  # Click Save
            break       
            
           

    # Đợi khi có màu xanh để click đóng
    while True:
        color2 = pyautogui.pixel(1675, 331)
        if color2 ==  (146, 208, 80):
            time.sleep(T3)
            pyautogui.click(1893, 27)  # Click đóng
            time.sleep(T3)
            break

    # Mở PMS, đóng weldsum
    pyautogui.click(959, 1055)
    time.sleep(T3)
    pyautogui.click(785, 65)
    time.sleep(T3)

    # Quay lại Excel
    pyautogui.click(913, 1059)
    time.sleep(T3)

print(f"Hoàn tất {n} lần lặp lại.")
