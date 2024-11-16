import tkinter as tk
from tkinter import ttk

class DashCamVideoJoinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dash Cam Video Joiner")

        # Create a frame for layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a button to select directory
        self.select_directory_button = ttk.Button(main_frame, text="Select Directory")
        self.select_directory_button.grid(row=0, column=0, padx=5, pady=5)

def main():
    root = tk.Tk()
    app = DashCamVideoJoinerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()