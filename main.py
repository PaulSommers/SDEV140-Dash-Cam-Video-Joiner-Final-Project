import tkinter as tk
from tkinter import ttk
from tkinter import filedialog  # Import filedialog for directory selection

class DashCamVideoJoinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dash Cam Video Joiner")

        # Create a frame for layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a button to select directory
        self.select_directory_button = ttk.Button(main_frame, text="Select Directory", command=self.select_directory)
        self.select_directory_button.grid(row=0, column=0, padx=5, pady=5)

        self.selected_directory = None  # Variable to store the selected directory path

    def select_directory(self):
        """Open a dialog to select a directory and store the selected path."""
        try:
            self.selected_directory = filedialog.askdirectory()
            if self.selected_directory:
                print(f"Selected directory: {self.selected_directory}")  # For now, just print the selected directory
        except Exception as e:
            print(f"Error selecting directory: {e}")

def main():
    root = tk.Tk()
    app = DashCamVideoJoinerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()