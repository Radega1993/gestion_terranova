import tkinter as tk
from app.gui.main_window import MainWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()