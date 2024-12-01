import tkinter as tk
from tkinter import ttk
from tkinter import filedialog  # Import filedialog for directory selection
from watchdog.observers import Observer  # Used to monitor file system events
from watchdog.events import FileSystemEventHandler  # Base class for handling events
import threading  # Used for running the observer in a separate thread
import time

class DashCamVideoJoinerApp:
    def __init__(self, root):
        # Initialize the main application window
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

        # Variable to store the selected directory path
        self.selected_directory = None

        # Flag to indicate if monitoring is active
        self.is_monitoring = False

        # Initialize the observer object for directory monitoring
        self.observer = None

    def select_directory(self):
        """Open a dialog to select a directory and store the selected path."""
        try:
            # Open a directory selection dialog and get the selected path
            self.selected_directory = filedialog.askdirectory()
            if self.selected_directory:
                print(f"Selected directory: {self.selected_directory}")
        except Exception as e:
            print(f"Error selecting directory: {e}")

    def start_monitoring(self):
        """Start monitoring the selected directory."""
        if self.selected_directory:
            if not self.is_monitoring:
                # Set the monitoring flag to True
                self.is_monitoring = True
                # Update the status label to indicate that monitoring has started
                self.status_label.config(text="Status: Monitoring")
                print("Monitoring started...")

                # Create an event handler to respond to filesystem events
                event_handler = VideoFileHandler()

                # Create an observer to monitor filesystem events
                self.observer = Observer()

                # Schedule the observer to watch the selected directory
                # The observer will use the event handler to handle events
                self.observer.schedule(event_handler, self.selected_directory, recursive=False)

                # Start the observer in a separate thread to keep the GUI responsive
                monitoring_thread = threading.Thread(target=self.observer.start)
                monitoring_thread.daemon = True  # Make the thread a daemon so it exits with the program
                monitoring_thread.start()
            else:
                print("Monitoring is already active.")
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

            # Stop the observer if it is running
            if self.observer:
                self.observer.stop()   # Stop the observer thread
                self.observer.join()   # Wait for the observer thread to finish
                self.observer = None   # Reset the observer to None
        else:
            print("Monitoring is not active.")

class VideoFileHandler(FileSystemEventHandler):
    """Handles events related to video files in the monitored directory."""

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            file_path = event.src_path
            # Print a message indicating a new file has been detected
            print(f"New file detected: {file_path}")
            # TODO: Implement video processing logic here

def main():
    # Create the main application window
    root = tk.Tk()
    # Instantiate the application class
    app = DashCamVideoJoinerApp(root)
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()