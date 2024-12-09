import os  # Import os module to handle file paths
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import messagebox for dialog boxes
from tkinter import filedialog  # Import filedialog for directory selection
from PIL import Image, ImageTk  # Import PIL modules to handle images
from watchdog.observers import Observer  # Used to monitor file system events
from watchdog.events import FileSystemEventHandler  # Base class for handling events
import threading  # Used for running the observer in a separate thread
import time
import pystray  # Import pystray for system tray icon handling
from pystray import MenuItem as item  # Import MenuItem for creating menu items in the tray icon

class DashCamVideoJoinerApp:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("Dash Cam Video Joiner")
        self.root.resizable(False, False)  # Prevent window resizing

        # Handle the window protocol to catch the minimize event
        self.root.protocol('WM_ICONIFY', self.hide_window)
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)  # Handle close window event

        # Configure grid to center widgets
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Load the logo image
        try:
            # Determine the path to the logo image
            logo_filename = "logo-tranparentBG.png"  # Use your actual logo file name
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo_filename)
            # Open the logo image file
            logo_image = Image.open(logo_path)
            # Resize the image while maintaining aspect ratio
            logo_image.thumbnail((300, 300), Image.LANCZOS)
            # Convert the image to a Tkinter-compatible photo image
            logo_photo = ImageTk.PhotoImage(logo_image)
            # Create a label to display the logo image
            self.logo_label = ttk.Label(self.root, image=logo_photo)
            self.logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            self.logo_label.grid(row=0, column=0, pady=(20, 10), sticky=tk.N)
        except Exception as e:
            print(f"Error loading logo image: {e}")

        # Create a frame to organize the main controls
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=tk.NSEW)

        # Center the main frame
        self.root.columnconfigure(0, weight=1)
        main_frame.columnconfigure((0, 1, 2), weight=1)

        # Create a toggle button for monitoring
        self.monitor_button = ttk.Button(
            main_frame, text="Start Monitoring", command=self.toggle_monitoring
        )
        self.monitor_button.grid(row=0, column=0, padx=5, pady=5)

        # Create a button to open the Configuration window
        self.config_button = ttk.Button(
            main_frame, text="Configure", command=self.open_configuration
        )
        self.config_button.grid(row=0, column=1, padx=5, pady=5)

        # Create a button to open the Log window
        self.log_button = ttk.Button(
            main_frame, text="View Log", command=self.open_log_window
        )
        self.log_button.grid(row=0, column=2, padx=5, pady=5)

        # Create a label to display the status
        self.status_label = ttk.Label(main_frame, text="Status: Idle")
        self.status_label.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

        # Variable to store the selected directory path
        self.selected_directory = None

        # Variable to store the time threshold value
        self.time_threshold = 90  # Default time threshold in seconds

        # Flag to indicate if monitoring is active
        self.is_monitoring = False

        # Initialize the observer object for directory monitoring
        self.observer = None

        # System tray icon setup
        self.tray_icon = None  # Placeholder for the tray icon object

    def hide_window(self):
        """Hide the main window and show the tray icon."""
        self.root.withdraw()  # Hide the main window
        self.show_tray_icon()  # Display the system tray icon

    def show_window(self, icon, item):
        """Show the main window and stop the tray icon."""
        icon.stop()           # Stop the tray icon
        self.root.deiconify()  # Show the main window

    def quit_window(self, icon, item):
        """Exit the application from the tray icon."""
        icon.stop()           # Stop the tray icon
        self.exit_app()       # Call the exit_app method to clean up and exit

    def show_tray_icon(self):
        """Create and display the system tray icon."""
        # Load an icon image for the system tray (ensure 'icon.png' exists)
        icon_image = Image.open("icon.png")  # Provide an icon image for the tray
        # Create a menu for the tray icon
        menu = pystray.Menu(
            item('Restore', self.show_window),
            item('Exit', self.quit_window)
        )
        # Create the tray icon with the image and menu
        self.tray_icon = pystray.Icon("DashCamVideoJoiner", icon_image, "Dash Cam Video Joiner", menu)
        # Run the icon in a separate thread to prevent blocking the main thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def exit_app(self):
        """Exit the application gracefully."""
        # Stop monitoring if it is active
        if self.is_monitoring:
            self.stop_monitoring()
        # Destroy the main window to exit the application
        self.root.destroy()

    def on_closing(self):
        """Handle the window closing event."""
        # Confirm with the user before exiting
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.exit_app()  # Call the exit_app method to exit the application

    def open_configuration(self):
        """Open the Configuration window to set directory and time threshold."""
        # Create a new Toplevel window
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration")
        config_window.resizable(False, False)

        # Create a frame within the Configuration window
        config_frame = ttk.Frame(config_window, padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a label and button for directory selection
        dir_label = ttk.Label(config_frame, text="Selected Directory:")
        dir_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.dir_var = tk.StringVar()
        if self.selected_directory:
            self.dir_var.set(self.selected_directory)
        else:
            self.dir_var.set("No directory selected")

        dir_display = ttk.Label(config_frame, textvariable=self.dir_var)
        dir_display.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        select_dir_button = ttk.Button(
            config_frame, text="Select Directory", command=self.select_directory
        )
        select_dir_button.grid(row=0, column=2, padx=5, pady=5)

        # Create a label for the time threshold input
        threshold_label = ttk.Label(config_frame, text="Time Threshold (seconds):")
        threshold_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Create an entry widget for the time threshold
        self.threshold_var = tk.StringVar()
        self.threshold_var.set(str(self.time_threshold))  # Set to current time threshold
        threshold_entry = ttk.Entry(config_frame, textvariable=self.threshold_var)
        threshold_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Create a Save button to apply the configurations
        save_button = ttk.Button(
            config_frame, text="Save", command=config_window.destroy
        )
        save_button.grid(row=2, column=1, padx=5, pady=10)

    def select_directory(self):
        """Open a dialog to select a directory and store the selected path."""
        try:
            # Open a directory selection dialog and get the selected path
            self.selected_directory = filedialog.askdirectory()
            if self.selected_directory:
                print(f"Selected directory: {self.selected_directory}")
                # Update the directory display variable
                self.dir_var.set(self.selected_directory)
        except Exception as e:
            print(f"Error selecting directory: {e}")

    def toggle_monitoring(self):
        """Toggle monitoring on or off."""
        if not self.is_monitoring:
            # Start monitoring if not already active
            started = self.start_monitoring()
            if started:
                # Change button text to indicate the new action only if monitoring started
                self.monitor_button.config(text="Stop Monitoring")
        else:
            # Stop monitoring if currently active
            self.stop_monitoring()
            # Change button text back to the initial state
            self.monitor_button.config(text="Start Monitoring")

    def start_monitoring(self):
        """Start monitoring the selected directory."""
        if self.selected_directory:
            if not self.is_monitoring:
                # Get and validate the time threshold value
                try:
                    # Attempt to convert the input to an integer
                    self.time_threshold = int(self.threshold_var.get())
                    if self.time_threshold <= 0:
                        # Time threshold must be a positive integer
                        raise ValueError("Time threshold must be a positive integer.")
                except ValueError as e:
                    # Handle invalid input by displaying an error message
                    print(f"Invalid time threshold: {e}")
                    messagebox.showerror("Invalid Threshold", f"Invalid time threshold: {e}")
                    return False  # Indicate that monitoring did not start

                # Set the monitoring flag to True to indicate that monitoring is active
                self.is_monitoring = True

                # Update the status label to indicate that monitoring has started
                self.status_label.config(text="Status: Monitoring")
                print("Monitoring started...")

                # Create an event handler to respond to filesystem events
                event_handler = VideoFileHandler(time_threshold=self.time_threshold)

                # Create an observer to monitor filesystem events
                self.observer = Observer()

                # Schedule the observer to watch the selected directory
                # The observer will use the event handler to handle events
                self.observer.schedule(event_handler, self.selected_directory, recursive=False)

                # Start the observer in a separate thread to keep the GUI responsive
                monitoring_thread = threading.Thread(target=self.observer.start)
                monitoring_thread.daemon = True  # Ensure thread exits when the program closes
                monitoring_thread.start()

                return True  # Indicate that monitoring started successfully
            else:
                print("Monitoring is already active.")
                return False  # Monitoring was already active
        else:
            # No directory has been selected; inform the user
            print("Please select a directory first.")
            messagebox.showwarning("No Directory Selected", "Please select a directory before starting monitoring.")
            return False  # Indicate that monitoring did not start

    def stop_monitoring(self):
        """Stop monitoring the directory."""
        if self.is_monitoring:
            # Set the monitoring flag to False to indicate that monitoring has stopped
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

    def open_log_window(self):
        """Open a window to display logged output."""
        # Create a new Toplevel window for the log
        log_window = tk.Toplevel(self.root)
        log_window.title("Log Output")
        log_window.geometry("600x400")

        # Create a Text widget to display the logs
        log_text = tk.Text(log_window, wrap='word', height=15, width=60)
        log_text.pack(expand=True, fill='both', padx=10, pady=10)

        # For now, display placeholder text in the log window
        log_content = "Log output will be displayed here.\n"
        log_text.insert('end', log_content)

        # TODO: Redirect print statements or use a logging framework to display real logs

class VideoFileHandler(FileSystemEventHandler):
    """Handles events related to video files in the monitored directory."""

    def __init__(self, time_threshold):
        super().__init__()
        # Store the time threshold value for use in processing
        self.time_threshold = time_threshold
        # Initialize a list to keep track of video files
        self.video_files = []

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