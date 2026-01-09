import pyautogui
import time

print("Mové el mouse sobre el lugar que quieras medir...")
time.sleep(3)

while True:
    print(pyautogui.position())
    time.sleep(0.5)
