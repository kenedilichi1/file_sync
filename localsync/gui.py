import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QFileDialog

class LocalSyncGUI:
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.root = tk.Tk()
        self.setup_gui()
        self.current_user = None
        self.online_devices = {}
        self.transfer_history = []

    def setup_gui(self) -> None:
        """Setup the main GUI window"""
        self.root.title("LocalSync - Secure File Sharing")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show login screen initially
        self.show_login_screen()
        
    def show_login_screen(self):
        """Show login/registration screen"""
        self.clear_screen()
        
        # Header
        header = ttk.Label(self.main_frame, text="🚀 LocalSync", 
                          font=('Arial', 24, 'bold'), foreground='#2c3e50')
        header.pack(pady=20)
        
        subheader = ttk.Label(self.main_frame, text="Secure File Sharing Over Local Network",
                             font=('Arial', 12), foreground='#7f8c8d')
        subheader.pack(pady=5)
        
        # Login Frame
        login_frame = ttk.LabelFrame(self.main_frame, text="Account", padding=20)
        login_frame.pack(pady=30, fill=tk.X)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30, font=('Arial', 11))
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)
        self.username_entry.focus()
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show='•', font=('Arial', 11))
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="Login", 
                  command=self.handle_login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Register", 
                  command=self.handle_register, width=15).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(self.main_frame, text="", foreground='#e74c3c')
        self.status_label.pack(pady=10)
        
    def show_main_dashboard(self):
        """Show main dashboard after login"""
        self.clear_screen()
        
        # Header with user info
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text=f"👋 Welcome, {self.current_user}!", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Logout", 
                  command=self.handle_logout).pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.setup_devices_tab()
        self.setup_file_transfer_tab()
        self.setup_settings_tab()
        self.setup_history_tab()
        
        # Start device discovery in background
        self.start_device_discovery()
        
    def setup_devices_tab(self):
        """Setup online devices tab"""
        self.devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.devices_frame, text="📱 Online Devices")
        
        # Refresh button
        refresh_frame = ttk.Frame(self.devices_frame)
        refresh_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(refresh_frame, text="🔄 Refresh", 
                  command=self.refresh_devices).pack(side=tk.LEFT)
        
        # Devices list
        devices_container = ttk.Frame(self.devices_frame)
        devices_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for devices
        columns = ('username', 'device_name', 'ip_address', 'status')
        self.devices_tree = ttk.Treeview(devices_container, columns=columns, show='headings', height=10)
        
        # Define headings
        self.devices_tree.heading('username', text='Username')
        self.devices_tree.heading('device_name', text='Device Name')
        self.devices_tree.heading('ip_address', text='IP Address')
        self.devices_tree.heading('status', text='Status')
        
        # Set column widths
        self.devices_tree.column('username', width=120)
        self.devices_tree.column('device_name', width=150)
        self.devices_tree.column('ip_address', width=120)
        self.devices_tree.column('status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(devices_container, orient=tk.VERTICAL, command=self.devices_tree.yview)
        self.devices_tree.configure(yscrollcommand=scrollbar.set)
        
        self.devices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double click to send file
        self.devices_tree.bind('<Double-1>', self.on_device_double_click)
        
    def setup_file_transfer_tab(self):
        """Setup file transfer tab"""
        self.transfer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transfer_frame, text="📤 Send Files")
        
        # File selection
        file_frame = ttk.LabelFrame(self.transfer_frame, text="Select File or Folder", padding=15)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(file_frame, text="📁 Select File", 
                  command=self.select_file, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="📂 Select Folder", 
                  command=self.select_folder, width=20).pack(side=tk.LEFT, padx=5)
        
        # Selected path display
        self.selected_path_label = ttk.Label(file_frame, text="No file selected", 
                                           foreground='#7f8c8d', wraplength=400)
        self.selected_path_label.pack(pady=10, fill=tk.X)
        
        # Recipient selection
        recipient_frame = ttk.LabelFrame(self.transfer_frame, text="Select Recipient", padding=15)
        recipient_frame.pack(fill=tk.X, pady=10)
        
        self.recipient_var = tk.StringVar()
        self.recipient_combo = ttk.Combobox(recipient_frame, textvariable=self.recipient_var, state='readonly')
        self.recipient_combo.pack(fill=tk.X, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.transfer_frame, text="Transfer Options", padding=15)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.encrypt_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🔒 Encrypt file", 
                       variable=self.encrypt_var).pack(anchor=tk.W, pady=2)
        
        self.compress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="🗜️ Compress file", 
                       variable=self.compress_var).pack(anchor=tk.W, pady=2)
        
        # Send button
        ttk.Button(self.transfer_frame, text="🚀 Send File", 
                  command=self.start_file_transfer, style='Accent.TButton').pack(pady=20)
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.transfer_frame, text="Transfer Progress", padding=15)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready to transfer")
        self.progress_label.pack()
        
    def setup_settings_tab(self):
        """Setup settings tab"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        
        # Auto-accept settings
        auto_accept_frame = ttk.LabelFrame(self.settings_frame, text="Auto-Accept Settings", padding=15)
        auto_accept_frame.pack(fill=tk.X, pady=10)
        
        self.auto_accept_var = tk.BooleanVar(value=self.cli.file_transfer.transfer_config.get_setting('auto_accept'))
        ttk.Checkbutton(auto_accept_frame, text="Auto-accept files from trusted senders",
                       variable=self.auto_accept_var, command=self.toggle_auto_accept).pack(anchor=tk.W)
        
        # Download directory
        download_frame = ttk.LabelFrame(self.settings_frame, text="Download Directory", padding=15)
        download_frame.pack(fill=tk.X, pady=10)
        
        download_path = self.cli.file_transfer.transfer_config.get_setting('default_download_dir')
        ttk.Label(download_frame, text=f"Current: {download_path}").pack(anchor=tk.W)
        
        ttk.Button(download_frame, text="Change Download Directory",
                  command=self.change_download_dir).pack(pady=10)
        
        # Trusted senders
        trusted_frame = ttk.LabelFrame(self.settings_frame, text="Trusted Senders", padding=15)
        trusted_frame.pack(fill=tk.X, pady=10)
        
        trusted_senders = self.cli.file_transfer.transfer_config.get_setting('auto_accept_senders')
        trusted_text = ", ".join(trusted_senders) if trusted_senders else "None"
        ttk.Label(trusted_frame, text=f"Trusted: {trusted_text}").pack(anchor=tk.W)
        
    def setup_history_tab(self):
        """Setup transfer history tab"""
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📋 History")
        
        # History text area
        self.history_text = scrolledtext.ScrolledText(self.history_frame, height=15, wrap=tk.WORD)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.history_text.config(state=tk.DISABLED)
        
        # Clear button
        ttk.Button(self.history_frame, text="Clear History", 
                  command=self.clear_history).pack(pady=10)
        
    def clear_screen(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    # ==================== EVENT HANDLERS ====================
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
            
        # Show loading
        self.status_label.config(text="Logging in...", foreground='#f39c12')
        self.root.update()
        
        # Perform login in thread to avoid blocking GUI
        def login_thread():
            success, message = self.cli.auth_manager.login(username, password)
            self.root.after(0, lambda: self.login_complete(success, message, username))
            
        threading.Thread(target=login_thread, daemon=True).start()
        
    def login_complete(self, success, message, username):
        """Handle login completion"""
        if success:
            self.current_user = username
            self.status_label.config(text="✅ Login successful!", foreground='#27ae60')
            self.root.after(1000, self.show_main_dashboard)
        else:
            self.status_label.config(text=f"❌ {message}", foreground='#e74c3c')
            
    def handle_register(self):
        """Handle registration"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
            
        if len(password) < 3:
            self.show_error("Password must be at least 3 characters")
            return
            
        # Show loading
        self.status_label.config(text="Registering...", foreground='#f39c12')
        self.root.update()
        
        def register_thread():
            success, message = self.cli.auth_manager.register(username, password)
            self.root.after(0, lambda: self.register_complete(success, message))
            
        threading.Thread(target=register_thread, daemon=True).start()
        
    def register_complete(self, success, message):
        """Handle registration completion"""
        if success:
            self.status_label.config(text="✅ Registration successful! Please login.", foreground='#27ae60')
            self.password_entry.delete(0, tk.END)
        else:
            self.status_label.config(text=f"❌ {message}", foreground='#e74c3c')
            
    def handle_logout(self):
        """Handle logout"""
        self.current_user = None
        if self.cli.device_discovery:
            self.cli.device_discovery.stop_discovery()
        self.show_login_screen()
        
    def select_file(self):
        """Select file to send"""
        filename = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.selected_path = filename
            self.selected_path_label.config(text=f"Selected: {os.path.basename(filename)}")
            
    def select_folder(self):
        """Select folder to send"""
        folder = filedialog.askdirectory(title="Select folder to send")
        if folder:
            self.selected_path = folder
            self.selected_path_label.config(text=f"Selected: {os.path.basename(folder)} (Folder)")
            
    def start_file_transfer(self):
        """Start file transfer"""
        if not hasattr(self, 'selected_path') or not self.selected_path:
            self.show_error("Please select a file or folder first")
            return
            
        recipient = self.recipient_var.get()
        if not recipient:
            self.show_error("Please select a recipient")
            return
            
        # Get recipient IP from devices list
        recipient_ip = None
        for username, info in self.online_devices.items():
            if username == recipient:
                recipient_ip = info['ip_address']
                break
                
        if not recipient_ip:
            self.show_error("Selected recipient is no longer online")
            return
            
        # Start transfer in thread
        def transfer_thread():
            self.update_progress(0, "Starting transfer...")
            
            if os.path.isfile(self.selected_path):
                success, message = self.cli.file_transfer.send_file(
                    self.selected_path, 
                    recipient_ip,
                    progress_callback=self.progress_callback
                )
            else:
                success, message = self.cli.file_transfer.send_folder(
                    self.selected_path,
                    recipient_ip, 
                    progress_callback=self.progress_callback
                )
                
            self.root.after(0, lambda: self.transfer_complete(success, message))
            
        threading.Thread(target=transfer_thread, daemon=True).start()
        
    def progress_callback(self, transferred, total, stage):
        """Update progress bar"""
        progress = (transferred / total) * 100 if total > 0 else 0
        self.root.after(0, lambda: self.update_progress(progress, stage))
        
    def update_progress(self, progress, message):
        """Update progress bar and label"""
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{message}: {progress:.1f}%")
        
    def transfer_complete(self, success, message):
        """Handle transfer completion"""
        if success:
            self.show_info("Transfer Complete", f"✅ {message}")
            self.add_to_history(f"✅ Sent to {self.recipient_var.get()}: {message}")
        else:
            self.show_error(f"Transfer Failed: {message}")
            self.add_to_history(f"❌ Failed: {message}")
            
        self.update_progress(0, "Ready to transfer")
        
    def on_device_double_click(self, event):
        """Handle double click on device - switch to transfer tab"""
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            username = item['values'][0]
            self.recipient_var.set(username)
            self.notebook.select(1)  # Switch to transfer tab
            
    def refresh_devices(self):
        """Refresh devices list"""
        if self.cli.device_discovery:
            self.online_devices = self.cli.device_discovery.get_online_devices()
            self.update_devices_list()
            
    def update_devices_list(self):
        """Update devices treeview"""
        # Clear existing items
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
            
        # Update combo box
        recipients = []
        
        for username, info in self.online_devices.items():
            if username != self.current_user:
                # Add to treeview
                last_seen = time.time() - info['last_seen']
                status = "🟢 Online" if last_seen < 30 else "🟡 Away"
                self.devices_tree.insert('', tk.END, values=(
                    username, info['device_name'], info['ip_address'], status
                ))
                recipients.append(username)
                
        # Update recipient combo
        self.recipient_combo['values'] = recipients
        
    def start_device_discovery(self):
        """Start device discovery service"""
        device_name = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'Unknown')
        self.cli.device_discovery = self.cli._create_discovery_manager()
        self.cli.device_discovery.start_discovery(self.current_user, device_name)
        
        # Start periodic device list updates
        self.update_devices_periodically()
        
    def update_devices_periodically(self):
        """Update devices list every 5 seconds"""
        if self.current_user:  # Only if still logged in
            self.refresh_devices()
            self.root.after(5000, self.update_devices_periodically)
            
    def toggle_auto_accept(self):
        """Toggle auto-accept setting"""
        self.cli.file_transfer.transfer_config.update_setting('auto_accept', self.auto_accept_var.get())
        
    def change_download_dir(self):
        """Change download directory"""
        directory = QFileDialog.getExistingDirectory(
        self,
        "Select Download Directory"
        )
        if directory:
            try:
                # Stop the current receiver first
                self.cli.file_transfer.stop_receiver()
            
                # Update the configuration
                self.cli.file_transfer.transfer_config.update_setting('default_download_dir', directory)
                self.cli.download_dir = directory
            
                # Start the receiver with the new directory
                self.cli.file_transfer.start_receiver(directory)
                self.show_info("Success", "Download directory updated!")
            
            except Exception as e:
                self.show_error(f"Failed to change download directory: {str(e)}")
                # Try to restart receiver with old directory as fallback
                try:
                    self.cli.file_transfer.start_receiver(self.cli.download_dir)
                except:
                    pass  # Receiver might already be running

            
    def add_to_history(self, message):
        """Add message to history"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
        
    def clear_history(self):
        """Clear history"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
    # ==================== UTILITY METHODS ====================
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        
    def show_info(self, title, message):
        """Show info message"""
        messagebox.showinfo(title, message)
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()