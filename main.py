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
import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips  # Import MoviePy for video processing
import configparser  # For handling configuration files

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

        # Variable to store the timestamp format
        self.timestamp_format = '%Y-%m-%d %Hh %Mm %Ss'  # Updated default format to '2024-11-11 15h 49m 23s'

        # Variable to store the selected video file extension
        self.video_extension = '.mp4'  # Default extension

        # Path to the configuration file
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

        # Load configurations
        self.load_config()

        # Update GUI elements with loaded configurations
        self.dir_var = tk.StringVar(value=self.selected_directory or "No directory selected")
        self.threshold_var = tk.StringVar(value=str(self.time_threshold))
        self.format_var = tk.StringVar(value=self.timestamp_format)
        self.extension_var = tk.StringVar(value=self.video_extension)

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

        # Save configuration before exiting
        self.save_config()

        # Destroy the main window to exit the application
        self.root.destroy()

    def on_closing(self):
        """Handle the window closing event."""
        # Confirm with the user before exiting
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.exit_app()  # Call the exit_app method to exit the application

    def open_configuration(self):
        """Open the Configuration window to set directory, time threshold, timestamp format, and video extension."""
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

        # Variable to display the selected directory
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

        # Help button for directory selection
        def show_directory_help():
            message = (
                "Select the directory where your dashcam videos are stored.\n"
                "The application will monitor this directory for new video files.\n"
                "Ensure you have read/write permissions to the selected directory."
            )
            messagebox.showinfo("Directory Selection Help", message)

        dir_help_button = ttk.Button(config_frame, text="?", command=show_directory_help, width=2)
        dir_help_button.grid(row=0, column=3, padx=5, pady=5)

        # Create a label for the time threshold input
        threshold_label = ttk.Label(config_frame, text="Time Threshold (seconds):")
        threshold_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Entry widget for the time threshold
        self.threshold_var = tk.StringVar(value=str(self.time_threshold))
        threshold_entry = ttk.Entry(config_frame, textvariable=self.threshold_var)
        threshold_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Help button for time threshold
        def show_threshold_help():
            message = (
                "Set the maximum time gap (in seconds) between video files to be joined together.\n"
                "Videos with timestamps within this threshold will be merged into continuous segments.\n"
                "Adjust this value according to how your dashcam segments videos."
            )
            messagebox.showinfo("Time Threshold Help", message)

        threshold_help_button = ttk.Button(config_frame, text="?", command=show_threshold_help, width=2)
        threshold_help_button.grid(row=1, column=2, padx=5, pady=5)

        # Label for the timestamp format input
        format_label = ttk.Label(config_frame, text="Timestamp Format:")
        format_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # Entry widget for the timestamp format
        self.format_var = tk.StringVar(value=self.timestamp_format)
        format_entry = ttk.Entry(config_frame, textvariable=self.format_var, width=30)
        format_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)

        # Help button to show format guidelines
        def show_format_help():
            message = (
                "Specify the format used in your dashcam video filenames.\n"
                "Use Python's datetime format codes.\n\n"
                "Examples:\n"
                " - %Y%m%d_%H%M%S for '20231016_154923.mp4'\n"
                " - %Y-%m-%d %Hh %Mm %Ss for '2024-11-11 15h 49m 23s.mp4'\n"
                " - For full reference, visit:\n"
                "   https://strftime.org/"
            )
            messagebox.showinfo("Timestamp Format Help", message)

        help_button = ttk.Button(config_frame, text="?", command=show_format_help, width=2)
        help_button.grid(row=2, column=3, padx=5, pady=5)

        # Supported video extensions
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.ts']

        # Label for the video extension selection
        extension_label = ttk.Label(config_frame, text="Video File Extension:")
        extension_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        # Combobox for selecting the video extension
        self.extension_var = tk.StringVar(value=self.video_extension)
        extension_combobox = ttk.Combobox(
            config_frame,
            textvariable=self.extension_var,
            values=video_extensions,
            state='readonly',
            width=10
        )
        extension_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Help button for video extension
        def show_extension_help():
            message = (
                "Select the file extension used by your dashcam videos.\n"
                "The application will monitor and process files with this extension.\n"
            )
            messagebox.showinfo("Video File Extension Help", message)

        extension_help_button = ttk.Button(
            config_frame, text="?", command=show_extension_help, width=2
        )
        extension_help_button.grid(row=3, column=2, padx=5, pady=5)

        # Adjust the position of the Save button
        def save_config():
            """Save the configuration settings and close the window."""
            # Save the time threshold
            try:
                self.time_threshold = int(self.threshold_var.get())
                if self.time_threshold <= 0:
                    raise ValueError("Time threshold must be a positive integer.")
            except ValueError as e:
                messagebox.showerror("Invalid Threshold", f"Invalid time threshold: {e}")
                return

            # Save the timestamp format
            self.timestamp_format = self.format_var.get()
            if not self.validate_timestamp_format(self.timestamp_format):
                messagebox.showerror("Invalid Format", "The timestamp format is invalid.")
                return

            # Save the video file extension
            self.video_extension = self.extension_var.get()

            # Save the selected directory
            if self.dir_var.get() != "No directory selected":
                self.selected_directory = self.dir_var.get()

            # Save the configurations to file
            self.save_config()

            config_window.destroy()

        save_button = ttk.Button(
            config_frame, text="Save", command=save_config
        )
        save_button.grid(row=4, column=1, padx=5, pady=10)

        # Update the directory display variable
        self.dir_var.set(self.selected_directory or "No directory selected")

        # Update other configuration variables
        self.threshold_var.set(str(self.time_threshold))
        self.format_var.set(self.timestamp_format)
        self.extension_var.set(self.video_extension)

    def validate_timestamp_format(self, format_str):
        """
        Validate the user-provided timestamp format.

        Args:
            format_str (str): The timestamp format string.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        try:
            # Attempt to format the current time with the provided format
            datetime.datetime.now().strftime(format_str)
            return True
        except Exception as e:
            print(f"Invalid timestamp format: {e}")
            return False

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
                    self.time_threshold = int(self.threshold_var.get())
                    if self.time_threshold <= 0:
                        raise ValueError("Time threshold must be a positive integer.")
                except ValueError as e:
                    messagebox.showerror("Invalid Threshold", f"Invalid time threshold: {e}")
                    return False

                # Set the monitoring flag to True to indicate that monitoring is active
                self.is_monitoring = True

                # Update the status label to indicate that monitoring has started
                self.status_label.config(text="Status: Monitoring")
                print("Monitoring started...")

                # Create an event handler to respond to filesystem events
                event_handler = VideoFileHandler(
                    time_threshold=self.time_threshold,
                    timestamp_format=self.timestamp_format,
                    video_extension=self.video_extension
                )

                # Create an observer to monitor filesystem events
                self.observer = Observer()

                # Schedule the observer to watch the selected directory
                self.observer.schedule(event_handler, self.selected_directory, recursive=False)

                # Start the observer in a separate thread to keep the GUI responsive
                monitoring_thread = threading.Thread(target=self.observer.start)
                monitoring_thread.daemon = True  # Ensure thread exits when the program closes
                monitoring_thread.start()

                return True  # Indicate that monitoring started successfully
            else:
                print("Monitoring is already active.")
                return False
        else:
            # No directory has been selected; inform the user
            print("Please select a directory first.")
            messagebox.showwarning("No Directory Selected", "Please select a directory before starting monitoring.")
            return False

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

    def load_config(self):
        """
        Load the configuration settings from the config file.
        """
        # Create a ConfigParser instance with interpolation disabled
        config = configparser.ConfigParser(interpolation=None)

        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if 'Settings' in config:
                # Load settings if they exist
                self.selected_directory = config.get('Settings', 'selected_directory', fallback=None)
                self.time_threshold = config.getint('Settings', 'time_threshold', fallback=90)
                self.timestamp_format = config.get('Settings', 'timestamp_format', fallback='%Y%m-%d_%H%M%S')
                self.video_extension = config.get('Settings', 'video_extension', fallback='.mp4')
            else:
                # Set default values if 'Settings' section is missing
                self.set_default_config()
        else:
            # Set default values if config file doesn't exist
            self.set_default_config()

    def save_config(self):
        """
        Save the configuration settings to the config file.
        """
        # Create a ConfigParser instance with interpolation disabled
        config = configparser.ConfigParser(interpolation=None)
        config['Settings'] = {
            'selected_directory': self.selected_directory if self.selected_directory else '',
            'time_threshold': str(self.time_threshold),
            'timestamp_format': self.timestamp_format,
            'video_extension': self.video_extension
        }

        with open(self.config_file, 'w') as configfile:
            config.write(configfile)
        print("Configuration saved to config.ini")

    def set_default_config(self):
        """
        Set default configuration values.
        """
        self.selected_directory = None
        self.time_threshold = 90
        self.timestamp_format = '%Y-%m-%d %Hh %Mm %Ss'  # Updated default format
        self.video_extension = '.mp4'

class VideoFileHandler(FileSystemEventHandler):
    """Handles events related to video files in the monitored directory."""

    def __init__(self, time_threshold, timestamp_format, video_extension):
        super().__init__()
        # Store the time threshold value (in seconds) for use in processing
        self.time_threshold = time_threshold
        # Store the timestamp format for parsing
        self.timestamp_format = timestamp_format
        # Store the video file extension
        self.video_extension = video_extension.lower()
        # Initialize a list to keep track of video files and their timestamps
        self.video_files = []

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            file_path = event.src_path
            # Check if the file has the selected video extension
            if file_path.lower().endswith(self.video_extension):
                print(f"New video file detected: {file_path}")

                # Extract the timestamp from the filename using the user-specified format
                video_timestamp = self.extract_timestamp(file_path)

                if video_timestamp:
                    # Add the video file and its timestamp to the list
                    self.video_files.append((file_path, video_timestamp))
                    # Sort the list by timestamp to maintain chronological order
                    self.video_files.sort(key=lambda x: x[1])
                    print(f"Video timestamp extracted and stored: {video_timestamp}")

                    # Call process_videos to handle the new video files
                    self.process_videos()
                else:
                    print(f"Failed to extract timestamp from filename: {file_path}")
            else:
                print(f"Ignored non-video file: {file_path}")

    def extract_timestamp(self, file_path):
        """
        Extracts the timestamp from the video filename using the specified format.

        Args:
            file_path (str): The full path to the video file.

        Returns:
            datetime.datetime or None: The extracted timestamp, or None if parsing fails.
        """
        filename = os.path.basename(file_path)
        # Remove the file extension to get the base name
        base_name = os.path.splitext(filename)[0]

        try:
            # Parse the timestamp using the user-specified format
            timestamp = datetime.datetime.strptime(base_name, self.timestamp_format)
            return timestamp
        except ValueError as e:
            # Handle the case where the filename does not match the expected format
            print(f"Error parsing timestamp from filename '{filename}': {e}")
            return None

    def process_videos(self):
        """
        Processes the collected video files, groups them based on the time threshold,
        and joins the videos in each group.
        """
        # Ensure there are enough videos to process
        if len(self.video_files) < 2:
            return

        # Create a list to hold groups of videos to be joined
        video_groups = []
        current_group = [self.video_files[0]]

        # Iterate over the video files to group them
        for i in range(1, len(self.video_files)):
            previous_timestamp = self.video_files[i - 1][1]
            current_timestamp = self.video_files[i][1]
            time_difference = (current_timestamp - previous_timestamp).total_seconds()
            
            if time_difference <= self.time_threshold:
                # If the time difference is within the threshold, add to current group
                current_group.append(self.video_files[i])
            else:
                # Time difference exceeds threshold; start a new group
                video_groups.append(current_group)
                current_group = [self.video_files[i]]
        
        # Add the last group
        video_groups.append(current_group)
        
        # Process each group to join videos
        for group in video_groups:
            if len(group) > 1:
                self.join_videos(group)

    def join_videos(self, video_group):
        """
        Joins the videos in the given group into a single video file.
        """
        # Generate output file name based on timestamps
        start_time = video_group[0][1].strftime(self.timestamp_format)
        end_time = video_group[-1][1].strftime(self.timestamp_format)
        output_filename = f"joined_{start_time}_to_{end_time}{self.video_extension}"
        output_path = os.path.join(os.path.dirname(video_group[0][0]), output_filename)
        
        # Extract file paths from the group
        video_paths = [video[0] for video in video_group]
        try:
            # Load video clips
            clips = [VideoFileClip(path) for path in video_paths]
            
            # Concatenate video clips
            final_clip = concatenate_videoclips(clips)
            
            # Generate output file name based on timestamps
            start_time = video_group[0][1].strftime(self.timestamp_format)
            end_time = video_group[-1][1].strftime(self.timestamp_format)
            output_filename = f"joined_{start_time}_to_{end_time}{self.video_extension}"
            output_path = os.path.join(os.path.dirname(video_paths[0]), output_filename)
            
            # Write the final video to the output file
            final_clip.write_videofile(output_path)
            
            print(f"Videos joined successfully: {output_filename}")
            
            # Optionally, delete original files after joining
            for path in video_paths:
                os.remove(path)
                print(f"Deleted original file: {path}")
            
            # Remove the processed videos from the list
            self.video_files = [video for video in self.video_files if video[0] not in video_paths]
        
        except Exception as e:
            print(f"Error joining videos: {e}")

def main():
    # Create the main application window
    root = tk.Tk()
    # Instantiate the application class
    app = DashCamVideoJoinerApp(root)
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()