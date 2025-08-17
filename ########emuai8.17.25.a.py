import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
import time  # For simulated delays if needed
import configparser  # For editing PJ64 ini

class EmuAIPro:
    def __init__(self, root):
        self.root = root
        self.root.title("EmuAI Pro – N64 Emulator (Project64 1.6 Legacy Port with Cloned EMUAI64)")
        self.root.geometry("800x600")
        
        # Assume PJ64 dir structure
        self.pj64_dir = os.path.dirname(os.path.abspath(__file__))  # Or set to your PJ64 path
        self.ini_path = os.path.join(self.pj64_dir, 'Config', 'Project64.cfg')  # Adjust if .ini
        
        # Menus mimicking Project64
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load ROM", command=self.load_rom)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        emu_menu = tk.Menu(menubar, tearoff=0)
        emu_menu.add_command(label="Start Emulation", command=self.start_emu)
        emu_menu.add_command(label="Pause Emulation", command=self.pause_emu)
        emu_menu.add_command(label="Reset Emulation", command=self.reset_emu)
        menubar.add_cascade(label="Emulation", menu=emu_menu)
        
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="Graphics Plugin", command=self.set_graphics)
        menubar.add_cascade(label="Options", menu=options_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # ROM Browser Listbox (offline hardcoded for files=off)
        self.rom_list = tk.Listbox(self.root, height=10, width=50)
        self.rom_list.pack(pady=10)
        self.populate_roms()
        
        # Status Bar
        self.status = tk.Label(self.root, text="Ready – Project64 1.6 with Cloned EMUAI64 Powered", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Log Text Widget
        self.log_text = tk.Text(self.root, height=10, state=tk.DISABLED)
        self.log_text.pack(pady=10)
        
        # Emu Process Vars
        self.emu_process = None
        self.selected_rom = None
        self.graphics_plugin = "EMUAI64.dll"  # Default to cloned one
        
        # 60 FPS Update Loop (16ms interval)
        self.update_status()
    
    def populate_roms(self):
        roms = ["Super Mario 64.z64", "The Legend of Zelda: Ocarina of Time.z64", "Mario Kart 64.z64"]
        for rom in roms:
            self.rom_list.insert(tk.END, rom)
    
    def load_rom(self):
        self.selected_rom = filedialog.askopenfilename(title="Select N64 ROM", filetypes=[("N64 ROMs", "*.z64 *.n64")])
        if self.selected_rom:
            self.status.config(text=f"ROM Loaded: {os.path.basename(self.selected_rom)}")
    
    def start_emu(self):
        if not self.selected_rom:
            messagebox.showerror("Error", "Load a ROM first!")
            return
        self.set_plugin_in_ini()  # Auto-set plugin before launch
        cmd = [os.path.join(self.pj64_dir, "Project64.exe"), self.selected_rom]
        try:
            self.emu_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            threading.Thread(target=self.monitor_emu, daemon=True).start()
            self.status.config(text="Emulation Running – 60 FPS Target with Cloned Plugin")
        except Exception as e:
            messagebox.showerror("Emu Error", f"Failed to start: {e}")
    
    def pause_emu(self):
        self.log("Pause not fully supported; press F2 in PJ64 or add ctypes suspend for rebel mode.")
    
    def reset_emu(self):
        if self.emu_process:
            self.emu_process.terminate()
            self.start_emu()
    
    def set_graphics(self):
        plugins = ["Jabo_Direct3D8 1.6.dll", "Glide64.dll", "EMUAI64.dll"]  # Added cloned
        index = plugins.index(self.graphics_plugin) + 1
        self.graphics_plugin = plugins[index % len(plugins)]
        self.set_plugin_in_ini()
        self.log(f"Set graphics to {self.graphics_plugin} - Updated in ini")
        self.status.config(text=f"Graphics Plugin: {self.graphics_plugin} (Cloned Vibes)")
    
    def set_plugin_in_ini(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.ini_path):
            config.read(self.ini_path)
        if 'Video' not in config:
            config['Video'] = {}
        config['Video']['PluginName'] = self.graphics_plugin
        with open(self.ini_path, 'w') as configfile:
            config.write(configfile)
    
    def about(self):
        messagebox.showinfo("About", "EmuAI Pro: Python 3.13 N64 Emu with Project64 1.6 & Cloned EMUAI64.dll. 60 FPS, Authentic Style! Zilmar, Jabo, & Gonetz forever.")
    
    def monitor_emu(self):
        while self.emu_process and self.emu_process.poll() is None:
            output = self.emu_process.stderr.readline()
            if output:
                self.log(output.strip())
            time.sleep(0.016)
        self.status.config(text="Emulation Stopped")
    
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def update_status(self):
        if self.emu_process and self.emu_process.poll() is None:
            self.status.config(text=f"Running – PID: {self.emu_process.pid} (Cloned EMUAI64 Boost)")
        self.root.after(16, self.update_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmuAIPro(root)
    root.mainloop()
