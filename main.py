from tendo import singleton
me = singleton.SingleInstance() # exits if another instance is already running

import pystray
from PIL import Image, ImageDraw
import pyautogui

import os
import platform
import threading
import time

current_thread = None
stop_event = threading.Event()

NAGGING_INTERVAL_SEC = 10

def shake_mouse():
    s = 2 # number of pixels to move
    for _ in range(3):
        for d in [s, -s,]:
            pyautogui.move(d, 0, duration=0)
            pyautogui.move(0, d, duration=0)

def beep():
    if platform.system() == 'Windows':
        import winsound
        winsound.MessageBeep()
    else:
        os.system('\a')

def nag():
    beep()
    shake_mouse()

def create_icon_image(number, color):
    size = 33
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font_size = size - 2 if number <= 99 else 20
    d.text((size // 2, size // 2 - 1), str(number), fill=color, anchor='mm', font_size=font_size)
    return img

def set_icon(icon, value, color='cyan'):
    icon.icon = create_icon_image(value, color)
    icon.title = f"Time left: {value} min" if value > 0 else "Time's up!"

def cancellable_sleep(stop_event, total_seconds, check_interval=0.1):
    """
    Sleeps for total_seconds, checking stop_event every check_interval.
    Returns True if completed, False if cancelled.
    """
    end_time = time.monotonic() + total_seconds
    while True:
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            return True # completed
        if stop_event.is_set():
            return False # cancelled
        time.sleep(min(check_interval, remaining))

def update_icon(icon, countdown, stop_event):
    for i in range(countdown, 0, -1):
        if stop_event.is_set():
            break
        set_icon(icon, i)
        if not cancellable_sleep(stop_event, 60):
            break
    else:
        if countdown != 0:
            set_icon(icon, 0, 'red')
            nag()
            while cancellable_sleep(stop_event, NAGGING_INTERVAL_SEC):
                nag()
        else:
            set_icon(icon, 0, 'white')

def start_countdown(countdown):
    global current_thread, stop_event
    if current_thread and current_thread.is_alive():
        stop_event.set()
        current_thread.join()
    stop_event.clear()
    current_thread = threading.Thread(target=update_icon, args=(icon, countdown, stop_event), daemon=True)
    current_thread.start()

def on_select(icon, item):
    global current_thread, stop_event
    countdown = int(item.text)
    start_countdown(countdown)

def on_reset(icon, item):
    start_countdown(0)

def on_exit(icon, item):
    icon.stop()

exit_submenu = pystray.Menu(
    pystray.MenuItem('Confirm', on_exit)
)

last_click_time = 0
DOUBLE_CLICK_INTERVAL = 0.5  # seconds

def on_left_click(icon, item):
    global last_click_time, current_thread, stop_event
    now = time.time()
    if now - last_click_time < DOUBLE_CLICK_INTERVAL:
        # Double click detected
        print("Resetting countdown")
        if current_thread and current_thread.is_alive():
            stop_event.set()
            current_thread.join()
        update_icon(icon, 0, stop_event)
        last_click_time = 0  # Reset to avoid triple-clicks
    else:
        # Single click (but wait to see if another comes)
        last_click_time = now


options = [pystray.MenuItem(str(i), on_select) for i in
            list(range(240, 60, -30))
            + list(range(60, 10, -5))
            + list(range(10, 0, -1))]
menu = pystray.Menu(
    pystray.MenuItem('', on_left_click, default=True, visible=False),  # Invisible item to catch left clicks
    *options,
    pystray.Menu.SEPARATOR,
    pystray.MenuItem('Reset', on_reset),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem('Exit', exit_submenu),
)

if __name__ == "__main__":
    icon = pystray.Icon("Timebox", icon=create_icon_image(0, 'white'), title="Timebox", menu=menu)
    icon.run()