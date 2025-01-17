import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
import io
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import win32process
import cv2
from enum import Enum
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor


class KEYS(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    ENTER = 3


class GameState(Enum):
    LOADING = "loading"
    READY = "ready"
    MIDGAME = "in-progress"


class GameMode(Enum):
    Normal = "normal"
    FrameMode = "frame-mode"


class GameController:
    def __init__(self, id: str, url: str, debug: bool = False):
        self.id = str(
            uuid.uuid5(uuid.NAMESPACE_DNS, id)
        )  # should've never trusted y'all MFs to give an unique id. It's supposed to be different from the whole OS
        self.url = url
        self.debugging = debug

        # Defaults (DON'T CHANGE!)
        self.currentGameMode = GameMode.Normal
        self.currentGameState = GameState.LOADING
        self.currentTick = 0
        self.deathTime = 0

        # Other params
        self.windowSize = (512, 512)
        self.captureScale = 1.22  # i have no idea where this comes from :/

        self.browserStartTime = time.time()
        self.driver = self.__start_browser(self.url)
        time.sleep(2)
        self.actionChain = ActionChains(self.driver)
        self.gameContainer = self.driver.find_element(value="gameContainer")
        self.actionChain.click(self.gameContainer).perform()
        if debug:
            print(f"[{str(self.id)}] Browser started")

        time.sleep(0.25)

        self.hwnd = None
        while self.hwnd == None:
            self.hwnd = self.__getHWID()
            time.sleep(0.25)  # retry every second
        if debug:
            print(f"Found hwid: {self.hwnd}")

        self.__setupScreenCapture()

        while self.browserStartTime + 3 > time.time():
            time.sleep(0.001)  # Delay until 3 secs after browser started
        self.currentGameState = GameState.READY
        self.__setGameMode(GameMode.FrameMode)

    def __start_browser(self, tab_url):
        options = webdriver.ChromeOptions()
        options.add_argument("--enable-temporary-unexpire-flags-m130")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--app={tab_url}")
        options.add_argument("--disable-calculate-native-win-occlusion")
        options.add_argument(f"--window-size={self.windowSize[0]},{self.windowSize[1]}")
        options.add_argument("log-level=0")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-site-isolation-trials")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

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

        rect = win32gui.GetWindowRect(self.hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y

        self.dataBitMap = win32ui.CreateBitmap()
        self.dataBitMap.CreateCompatibleBitmap(
            self.dcObj, int(w * self.captureScale), int(h * self.captureScale)
        )
        self.cDC.SelectObject(self.dataBitMap)

        self.paddings = {
            "caption_height": win32api.GetSystemMetrics(
                win32con.SM_CYCAPTION
            ),  # Title bar height
            "border_width": win32api.GetSystemMetrics(
                win32con.SM_CXBORDER
            ),  # Vertical border width
            "border_height": win32api.GetSystemMetrics(
                win32con.SM_CYBORDER
            ),  # Horizontal border height
            "frame_width": win32api.GetSystemMetrics(
                win32con.SM_CXFRAME
            ),  # Resizable frame border width
            "frame_height": win32api.GetSystemMetrics(
                win32con.SM_CYFRAME
            ),  # Resizable frame border height
        }

    def getFrame(self):
        # print(self.hwnd)
        rect = win32gui.GetWindowRect(self.hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y

        # Copy the client area from the screen
        self.cDC.BitBlt(
            (0, 0),
            (int(w * self.captureScale), int(h * self.captureScale)),
            self.dcObj,
            (self.paddings["frame_width"] * 2 + self.paddings["border_width"], 0),
            win32con.SRCCOPY,
        )

        bmpinfo = self.dataBitMap.GetInfo()
        bmpstr = self.dataBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )
        img = img.resize(self.windowSize)

        self.__updateGameState(img)

        return img

    def getTimeAlive(self):
        if self.currentGameState != GameState.READY:
            return None
        return self.deathTime - self.currentTick - 3

    ### Returns enum of the current game state
    def __updateGameState(self, img=None):
        if self.currentGameState == GameState.MIDGAME:
            currentFrame = img if img is not None else self.getFrame()
            #rightBottomPixel = currentFrame.getpixel((500, 500))
            rightBottomPixel = currentFrame.getpixel((430,430))

            # print(self.id, rightBottomPixel)

            if rightBottomPixel == (245, 245, 245) or rightBottomPixel == (
                255,
                255,
                255,
            ):
                self.deathTime = time.time()
                self.currentGameState = GameState.READY

                if self.debugging:
                    print(
                        f"[{str(self.id)}] Survived {self.currentTick} Ticks"
                    )

    def startGame(self):
        if self.debugging:
            print(f"[{str(self.id)}] Started game")

        self.keydown(KEYS.ENTER)
        self.currentTick = 0
        self.currentGameState = GameState.MIDGAME

        time.sleep(0.1 * 10)
        # time.sleep(0.1)
        self.keyup(KEYS.ENTER)

        if self.currentGameMode is GameMode.FrameMode:
            for i in range(3):
                self.getNextFrame()

    def __setGameMode(self, mode: GameMode) -> None:
        if mode is GameMode.Normal:
            self.driver.execute_script('setMode("normal")')
        else:
            self.driver.execute_script('setMode("frame")')

        self.currentGameMode = mode

    def getNextFrame(self):
        # print(f"[{str(self.id)}] {self.hwnd}")

        if self.currentGameMode is not GameMode.FrameMode:
            print(
                f"[{str(self.id)}] [ERROR] Current gamemode set to FrameMode. Current mode: "
                + str(self.currentGameMode)
            )
            return None

        self.driver.execute_script("requestOneFrame();")
        self.currentTick += 1
        return self.getFrame()

    def forceResetGame(self):
        self.driver.refresh()
        self.currentGameMode = GameMode.Normal
        self.currentGameState = GameState.LOADING
        self.currentTick = 0
        self.deathTime = 0

    def __getVirtualKey(self, key):
        key_map = {
            KEYS.LEFT: 0x41,  # 'A' key
            KEYS.RIGHT: 0x44,  # 'D' key
            KEYS.ENTER: 0x0D,  # Enter key
        }
        return key_map.get(key, None)  # Return None if the key is not found

    def __getSeleniumVirtualKey(self, key):
        key_map = {
            KEYS.LEFT: "a",  # 'A' key
            KEYS.RIGHT: "d",  # 'D' key
            KEYS.ENTER: Keys.ENTER,  # Enter key
        }
        return key_map.get(key, None)  # Return None if the key is not found

    def keydown(self, key: KEYS) -> None:
        seleniumKey = self.__getSeleniumVirtualKey(key)
        if seleniumKey is not None:
            # print("PRESSED", seleniumKey)
            self.actionChain.key_down(seleniumKey).perform()

    def keyup(self, key):
        seleniumKey = self.__getSeleniumVirtualKey(key)
        if seleniumKey is not None:
            self.actionChain.key_up(seleniumKey).perform()

    def __del__(self):
        self.driver.quit()


def CreateGameInstace(instanceIndex):
    return GameController(str(instanceIndex), "http://localhost:53486/", True)


if __name__ == "__main__":

    num = 10
    games = []

    def run_game_instance(index):
        game = CreateGameInstace(index)  # Initialize game
        game.startGame()
        game.keydown(KEYS.LEFT)
        while True:
            time.sleep(0.25)
            frame: Image = game.getNextFrame()

            # frame.putpixel((430,430), (0, 0, 255))
            # frame.save(f"output_image_{index}.png", "PNG")

            if game.currentGameState == GameState.READY:
                return

    # Use ThreadPoolExecutor to create and run instances
    with ThreadPoolExecutor(max_workers=num) as executor:
        futures = []
        for i in range(num):
            futures.append(executor.submit(run_game_instance, i))

        for future in futures:
            future.result()

    print("Games are done")
