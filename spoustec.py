import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class FreeBASICCompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("FreeBASIC Compiler GUI")
        master.geometry("700x500")
        master.resizable(True, True)

        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill='both', expand=True)

        self.create_source_section(main_frame)
        self.create_output_section(main_frame)
        self.create_options_section(main_frame)
        self.create_compile_section(main_frame)
        self.create_log_section(main_frame)

        self.fbc_path = self.find_compiler()
        self.file_path = ""
        self.output_folder = ""

        if DND_AVAILABLE:
            master.drop_target_register(DND_FILES)
            master.dnd_bind('<<Drop>>', self.drop_file)

    def find_compiler(self):
        base_dir = r"C:\Users\Tatinek\Desktop\Basic"
        compiler_names = ["fbc.exe", "fbc32.exe", "fbc64.exe"]
        
        for name in compiler_names:
            path = os.path.join(base_dir, name)
            if os.path.isfile(path):
                return path
        
        return os.path.join(base_dir, "fbc.exe")

    def create_source_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Zdrojový soubor (.bas)", padding="5")
        frame.pack(fill='x', pady=5)

        ttk.Label(frame, text="Vyberte nebo přetáhněte .bas soubor", foreground="gray").pack(anchor='w', pady=2)

        self.file_path_label = ttk.Label(frame, text="Nevybráno", foreground="red")
        self.file_path_label.pack(anchor='w', pady=5)

        ttk.Button(frame, text="Vybrat soubor", command=self.select_file).pack(anchor='w', pady=2)

    def create_output_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Výstupní složka", padding="5")
        frame.pack(fill='x', pady=5)

        self.output_path_label = ttk.Label(frame, text="Stejná jako zdrojový soubor", foreground="gray")
        self.output_path_label.pack(anchor='w', pady=5)

        ttk.Button(frame, text="Vybrat výstupní složku", command=self.select_output_folder).pack(anchor='w', pady=2)

    def create_options_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Volby kompilátoru", padding="5")
        frame.pack(fill='x', pady=5)

        self.option_debug = tk.BooleanVar(value=False)
        self.option_console = tk.BooleanVar(value=True)
        self.option_optimize = tk.BooleanVar(value=False)
        self.option_static = tk.BooleanVar(value=False)

        options = [
            ("Debug info (-g)", self.option_debug),
            ("Konzolová aplikace (-s console)", self.option_console),
            ("Optimalizace (-O 2)", self.option_optimize),
            ("Statické linkování (-static)", self.option_static)
        ]

        for text, var in options:
            ttk.Checkbutton(frame, text=text, variable=var).pack(anchor='w', padx=5, pady=2)

    def create_compile_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=10)

        self.compile_button = ttk.Button(frame, text="▶ Kompilovat do .exe", command=self.compile_file)
        self.compile_button.pack(pady=5)

        self.status_label = ttk.Label(frame, text="Připraveno", foreground="blue")
        self.status_label.pack(pady=5)

    def create_log_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Log", padding="5")
        frame.pack(fill='both', expand=True, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(frame, height=10, state='disabled', bg="#f4f4f4", yscrollcommand=scrollbar.set)
        self.log_text.pack(fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)

    def drop_file(self, event):
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        file_path = file_path.strip()
        
        if file_path.lower().endswith(".bas") and os.path.isfile(file_path):
            self.file_path = file_path
            self.file_path_label.config(text=file_path, foreground="green")
            self.status_label.config(text="Soubor připraven ke kompilaci")
        else:
            messagebox.showerror("Chyba", "Musíte vybrat existující .bas soubor")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Vyberte .bas soubor",
            filetypes=[("FreeBASIC soubory", "*.bas"), ("Všechny soubory", "*.*")]
        )
        if file_path and os.path.isfile(file_path):
            self.file_path = file_path
            self.file_path_label.config(text=file_path, foreground="green")
            self.status_label.config(text="Soubor připraven ke kompilaci")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Vyberte výstupní složku")
        if folder_path:
            self.output_folder = folder_path
            self.output_path_label.config(text=folder_path, foreground="green")

    def log_message(self, message, clear=False):
        self.log_text.config(state='normal')
        if clear:
            self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def compile_file(self):
        if not self.file_path:
            messagebox.showwarning("Upozornění", "Nejprve vyberte .bas soubor")
            return

        if not os.path.isfile(self.fbc_path):
            messagebox.showerror("Chyba", f"Kompilátor nenalezen: {self.fbc_path}\nZkontrolujte cestu k fbc.exe")
            return

        if not os.path.isfile(self.file_path):
            messagebox.showerror("Chyba", f"Zdrojový soubor nenalezen: {self.file_path}")
            return

        exe_name = os.path.splitext(os.path.basename(self.file_path))[0] + ".exe"
        output_dir = self.output_folder if self.output_folder else os.path.dirname(self.file_path)
        exe_path = os.path.join(output_dir, exe_name)

        cmd = [self.fbc_path]
        
        if self.option_debug.get():
            cmd.append("-g")
        
        if self.option_console.get():
            cmd.extend(["-s", "console"])
        else:
            cmd.extend(["-s", "gui"])
        
        if self.option_optimize.get():
            cmd.extend(["-O", "2"])
        
        if self.option_static.get():
            cmd.append("-static")
        
        cmd.extend(["-x", exe_path, self.file_path])

        self.log_message(f"Spouštím kompilaci...\nPříkaz: {' '.join(cmd)}\n", clear=True)
        self.status_label.config(text="Kompilace probíhá...", foreground="orange")
        self.compile_button.config(state='disabled')
        self.master.update()

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=30)

            if result.stdout:
                self.log_message(f"STDOUT:\n{result.stdout}")
            
            if result.stderr:
                self.log_message(f"\nSTDERR:\n{result.stderr}")

            if result.returncode == 0:
                if os.path.isfile(exe_path):
                    self.status_label.config(text="✓ Kompilace dokončena úspěšně", foreground="green")
                    self.log_message(f"\n✓ Soubor vytvořen: {exe_path}")
                    messagebox.showinfo("Hotovo", f"Soubor {exe_name} byl úspěšně vytvořen v:\n{output_dir}")
                else:
                    self.status_label.config(text="⚠ Varování: Výstupní soubor nenalezen", foreground="orange")
                    self.log_message(f"\n⚠ Varování: Kompilátor skončil bez chyby, ale výstupní soubor nebyl nalezen.")
            else:
                self.status_label.config(text="✗ Chyba při kompilaci", foreground="red")
                self.log_message(f"\n✗ Kompilace selhala s kódem: {result.returncode}")
                messagebox.showerror("Chyba kompilace", f"Kompilace selhala s kódem {result.returncode}.\nZkontrolujte log pro detaily.")

        except subprocess.TimeoutExpired:
            self.status_label.config(text="✗ Timeout při kompilaci", foreground="red")
            self.log_message("\n✗ Kompilace trvala příliš dlouho (timeout 30s)")
            messagebox.showerror("Timeout", "Kompilace trvala příliš dlouho a byla zrušena.")
        
        except FileNotFoundError:
            self.status_label.config(text="✗ Kompilátor nenalezen", foreground="red")
            self.log_message(f"\n✗ Chyba: Kompilátor nenalezen: {self.fbc_path}")
            messagebox.showerror("Chyba", f"Kompilátor nenalezen:\n{self.fbc_path}")
        
        except Exception as e:
            self.status_label.config(text="✗ Chyba při kompilaci", foreground="red")
            self.log_message(f"\n✗ Neočekávaná chyba: {str(e)}")
            messagebox.showerror("Chyba", f"Neočekávaná chyba:\n{str(e)}")
        
        finally:
            self.compile_button.config(state='normal')

if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = FreeBASICCompilerGUI(root)
    root.mainloop()