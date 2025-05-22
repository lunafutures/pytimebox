import pystray
from PIL import Image, ImageDraw
import threading
import time

current_thread = None
stop_event = threading.Event()

def create_icon_image(number):
    size = 33
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((size / 2, size / 2 - 1), str(number), fill='white', anchor='mm', font_size=size - 2)
    return img

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
        icon.icon = create_icon_image(i)
        icon.title = f"Time left: {i} min"
        if not cancellable_sleep(stop_event, 60):
            break
    else:
        icon.icon = create_icon_image(0)
        icon.title = "Time's up!"

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

options = [pystray.MenuItem(str(i), on_select) for i in list(range(60, 10, -5)) + list(range(10, 0, -1))]
menu = pystray.Menu(
    *options,
    pystray.Menu.SEPARATOR,
    pystray.MenuItem('Reset', on_reset),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem('Exit', exit_submenu),
)

if __name__ == "__main__":
    icon = pystray.Icon("Timebox", icon=create_icon_image(0), title="Timebox", menu=menu)
    icon.run()