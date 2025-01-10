import time
from selenium import webdriver
from PIL import Image
import io
import numpy as np
import win32gui
import win32ui
import win32con
import cv2 # debugging

class GameController:
    def __init__(self, id, url):
        self.id = id
        self.url = url

        # Other params
        self.windowSize = (512, 512)

        self.driver = self.__start_browser(self.url)
        time.sleep(0.5)

    def __start_browser(self, tab_url):
        options = webdriver.ChromeOptions()
        options.add_argument("--enable-temporary-unexpire-flags-m130")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--app={tab_url}")
        options.add_argument("--disable-calculate-native-win-occlusion")
        options.add_argument(f"--window-size={self.windowSize[0]},{self.windowSize[1]}")
        options.add_argument("log-level=3")
        options.add_argument("disable-infobars")

        # Start the WebDriver and navigate to the URL
        driver = webdriver.Chrome(options=options)
        driver.get(tab_url)
        return driver

    def __list_windows(self):
        def callback(hwnd, handles):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Only include windows with a title
                    handles.append((hwnd, title))
            return True

        handles = []
        win32gui.EnumWindows(callback, handles)
        return handles

    def __getHWID(self):
        self.driver.execute_script(f'document.title = "{self.id}";')
        handles = self.__list_windows()

        

    def getFrame():
        pass

    def getNextFrame(self):
        pass

    def resetGame(self):
        pass

def main():

    # # Multiple games test
    # from concurrent.futures import ThreadPoolExecutor
    # drivers = []
    # with ThreadPoolExecutor(max_workers=len(tabs)) as executor:
    #     futures = [executor.submit(start_browser, tab) for tab in tabs]

    #     # Collect drivers as they are created
    #     for future in futures:
    #         drivers.append(future.result())

    # Single game test
    game = GameController("SingleInstance", "http://localhost:3000/")

    while True:
        # print(game.checkReady())
        time.sleep(0.5)


if __name__ == "__main__":
    main()
