import tkinter as tk
from PIL import Image, ImageTk
import cv2

class CamTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Test")

        self.label = tk.Label(root)
        self.label.pack()

        self.cap = cv2.VideoCapture(0)  # Or try 1 if needed
        self.update()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        else:
            print("❌ Failed to grab frame.")

        self.root.after(10, self.update)

    def on_close(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CamTestApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
