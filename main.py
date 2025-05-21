import pystray
from PIL import Image, ImageDraw
import threading
import time

def create_icon_image(number):
    size = 33
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((size / 2, size / 2), str(number), fill='white', anchor='mm', font_size=size - 2)
    return img

def update_icon(icon, countdown):
    for i in range(countdown, 0, -1):
        icon.icon = create_icon_image(i)
        icon.title = f"Time left: {i} min"
        time.sleep(60)
    icon.icon = create_icon_image(0)
    icon.title = "Time's up!"

def on_select(icon, item):
    countdown = int(item.text)
    threading.Thread(target=update_icon, args=(icon, countdown), daemon=True).start()

def on_exit(icon, item):
    icon.stop()

menu = pystray.Menu(
    pystray.MenuItem('5', on_select),
    pystray.MenuItem('10', on_select),
    pystray.MenuItem('15', on_select),
    pystray.MenuItem('Exit', on_exit)
)

if __name__ == "__main__":
    icon = pystray.Icon("Timebox", icon=create_icon_image(0), title="Timebox", menu=menu)
    icon.run()