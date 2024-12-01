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
        self.select_directory_button = ttk.Button(
            main_frame, text="Select Directory", command=self.select_directory
        )
        self.select_directory_button.grid(row=0, column=0, padx=5, pady=5)

        # Create a button to start monitoring
        self.start_button = ttk.Button(
            main_frame, text="Start Monitoring", command=self.start_monitoring
        )
        self.start_button.grid(row=1, column=0, padx=5, pady=5)

        # Create a button to stop monitoring
        self.stop_button = ttk.Button(
            main_frame, text="Stop Monitoring", command=self.stop_monitoring
        )
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        # Create a label to display the status
        self.status_label = ttk.Label(main_frame, text="Status: Idle")
        self.status_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.selected_directory = None  # Variable to store the selected directory path
        self.is_monitoring = False      # Flag to indicate if monitoring is active

    def select_directory(self):
        """Open a dialog to select a directory and store the selected path."""
        try:
            self.selected_directory = filedialog.askdirectory()
            if self.selected_directory:
                print(f"Selected directory: {self.selected_directory}")
        except Exception as e:
            print(f"Error selecting directory: {e}")

    def start_monitoring(self):
        """Start monitoring the selected directory."""
        if self.selected_directory:
            # Set the monitoring flag to True
            self.is_monitoring = True
            # Update the status label to indicate monitoring has started
            self.status_label.config(text="Status: Monitoring")
            print("Monitoring started...")
            # TODO: Implement the monitoring logic here
        else:
            print("Please select a directory first.")

    def stop_monitoring(self):
        """Stop monitoring the directory."""
        if self.is_monitoring:
            # Set the monitoring flag to False
            self.is_monitoring = False
            # Update the status label to indicate monitoring has stopped
            self.status_label.config(text="Status: Stopped")
            print("Monitoring stopped.")
            # TODO: Implement logic to stop monitoring
        else:
            print("Monitoring is not active.")

def main():
    root = tk.Tk()
    app = DashCamVideoJoinerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()