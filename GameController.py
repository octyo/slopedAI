import time
from selenium import webdriver
from PIL import Image
import io
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import cv2
from enum import Enum

class KEYS(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    ENTER = 3

class GameState(Enum):
    LOADING = "loading"
    READY = "ready"
    MIDGAME = "in-progress"

class GameController:
    def __init__(self, id, url, debug = False):
        self.id = id
        self.url = url
        self.debugging = debug

        # Defaults (DON'T CHANGE!)
        self.currentGameState = GameState.LOADING
        self.startTime = 0
        self.deathTime = 0

        # Other params
        self.windowSize = (512, 512)
        self.captureMultSize = 1.218

        self.driver = self.__start_browser(self.url)
        if debug: print("Browser started")

        time.sleep(0.25)

        self.hwnd = None
        while (self.hwnd == None):
            self.hwnd = self.__getHWID()
            time.sleep(0.25) # retry every second
        if debug: print(f"Found hwid: {self.hwnd}")

        self.__setupScreenCapture()

        self.currentGameState = GameState.READY

    def __start_browser(self, tab_url):
        options = webdriver.ChromeOptions()
        options.add_argument("--enable-temporary-unexpire-flags-m130")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--app={tab_url}")
        options.add_argument("--disable-calculate-native-win-occlusion")
        options.add_argument(f"--window-size={self.windowSize[0]},{self.windowSize[1]}")
        options.add_argument("log-level=0")
        options.add_argument("disable-infobars")
        options.add_experimental_option("excludeSwitches", ['enable-automation', "enable-logging"]);

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
        # print(handles)

        for hwnd, title in handles:
            if self.id in title:
                return hwnd

        return None

    def __setupScreenCapture(self):
        self.wDC = win32gui.GetWindowDC(self.hwnd)
        self.dcObj = win32ui.CreateDCFromHandle(self.wDC) 
        self.cDC = self.dcObj.CreateCompatibleDC()

        self.dataBitMap = win32ui.CreateBitmap()
        self.dataBitMap.CreateCompatibleBitmap(self.dcObj, int(self.windowSize[0]*self.captureMultSize), int(self.windowSize[1]*self.captureMultSize))
        self.cDC.SelectObject(self.dataBitMap)

        self.paddings = {
        "caption_height": win32api.GetSystemMetrics(win32con.SM_CYCAPTION),  # Title bar height
        "border_width": win32api.GetSystemMetrics(win32con.SM_CXBORDER),    # Vertical border width
        "border_height": win32api.GetSystemMetrics(win32con.SM_CYBORDER),   # Horizontal border height
        "frame_width": win32api.GetSystemMetrics(win32con.SM_CXFRAME),      # Resizable frame border width
        "frame_height": win32api.GetSystemMetrics(win32con.SM_CYFRAME),     # Resizable frame border height
    }

    def getFrame(self):

        # Copy the client area from the screen
        self.cDC.BitBlt(
            (0, 0), 
            (int(self.windowSize[0]*self.captureMultSize), int(self.windowSize[1]*self.captureMultSize)),
            self.dcObj, 
            (self.paddings["frame_width"]*2 + self.paddings["border_width"],0), 
            win32con.SRCCOPY
        )

        bmpinfo = self.dataBitMap.GetInfo()
        bmpstr = self.dataBitMap.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        img = img.resize(self.windowSize)

        self.__updateGameState(img)

        return img

    def getTimeAlive(self):
        if (self.currentGameState != GameState.READY):
            return None
        return self.deathTime - self.startTime - 3

    ### Returns enum of the current game state
    def __updateGameState(self, img = None):
        if (self.currentGameState == GameState.MIDGAME):
            currentFrame = img if img is not None else self.getFrame()
            rightBottomPixel = currentFrame.getpixel((500,500))

            # print(rightBottomPixel)

            if rightBottomPixel == (245, 245, 245):
                self.deathTime = time.time()
                self.currentGameState = GameState.READY

                if self.debugging:
                    print(f"Survived {self.deathTime - self.startTime} seconds")

    def startGame(self):
        self.keydown(KEYS.ENTER)
        self.startTime = time.time()
        self.currentGameState = GameState.MIDGAME

        time.sleep(0.01)
        self.keyup(KEYS.ENTER)

    def getNextFrame(self):
        pass

    def forceResetGame(self):
        pass

    def __getVirtualKey(self, key):
        key_map = {
            KEYS.LEFT: 0x41,  # 'A' key
            KEYS.RIGHT: 0x44, # 'D' key
            KEYS.ENTER: 0x0D, # Enter key
        }
        return key_map.get(key, None)  # Return None if the key is not found

    def keydown(self, key: KEYS) -> None:
        virtualKey = self.__getVirtualKey(key)
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, virtualKey, 0)

    def keyup(self, key):
        virtualKey = self.__getVirtualKey(key)
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, virtualKey, 0)

    def __del__(self):
        self.driver.quit()

        self.dcObj.DeleteDC()
        self.cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.wDC)
        win32gui.DeleteObject(self.dataBitMap.GetHandle())

class doubleA:
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2

def main():
    # Single game test
    game = GameController("SingleInstance", "http://localhost:3000/", True)

    time.sleep(1)
    game.startGame()
    game.keydown(KEYS.LEFT)

    a = [1,2,3,4,5]
    a2 = ["a", "b"]

    combinedA = [doubleA(1, None), doubleA(2, None)]

    for a in combinedA:
        a.a2 = a.a1 * 2   

    print(combinedA)

    while True:
        # print("Frame")
        game.updateGameState()
        frame = game.getFrame()
        frame.putpixel((500, 500), (0,0,255))
        frame.save("screenshot_debug.png")
        time.sleep(0.01)


if __name__ == "__main__":
    main()
