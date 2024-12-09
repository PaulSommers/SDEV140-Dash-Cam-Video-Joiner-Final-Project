import tkinter as tk
from gui import DashCamVideoJoinerApp  # Import the GUI application class

def main():
    """Entry point for the application."""
    # Create the main application window
    root = tk.Tk()
    # Instantiate the application class
    app = DashCamVideoJoinerApp(root)
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()