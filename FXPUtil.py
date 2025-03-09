import os
import json
import requests
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

def _load_signatures():
    try:
        with open('signatures.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def _read_header(file_path):
    if not os.path.isfile(file_path):
        return None
    if not file_path.lower().endswith(('.fxp', '.fxb')):
        return None
    
    try:
        with open(file_path, 'rb') as f:
            header_bytes = f.read(20)
        if header_bytes[:4] != b'CcnK':
            return None
        return header_bytes
    except:
        return None

def GetCompany(file_path: str) -> str:
    """
    Get the company name of the synth that the preset was made for.
    Returns \"None\" if unknown
    """
    header = _read_header(file_path)
    if not header:
        return None
    
    signatures = _load_signatures()
    if not signatures:
        return None
    
    for plugin in signatures:
        if plugin['code'].strip().encode('utf-8') in header:
            return plugin['company'].strip()
    return None

def GetVendor(file_path: str) -> str:
    """
    Get the company name of the synth that the preset was made for.
    Returns \"None\" if unknown
    """
    return GetCompany(file_path)

def GetCode(file_path: str) -> str:
    """
    Get the plugin code of the synth that the preset was made for.
    Returns \"None\" if unknown, to bypass this use ForceGetCode() instead
    """
    header = _read_header(file_path)
    if not header:
        return None
    
    signatures = _load_signatures()
    if not signatures:
        return None
    
    for plugin in signatures:
        code = plugin['code'].strip().encode('utf-8')
        if code in header:
            return plugin['code'].strip()
    return None

def ForceGetCode(file_path: str) -> str:
    """
    Get the plugin code of the synth that the preset was made for, even if it there isn't a code to begin with
    """
    if not os.path.isfile(file_path):
        return None
        
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if len(content) < 20:
                return None
            return content[16:20].decode('utf-8')
    except:
        return None

def GetName(file_path: str) -> str:
    """
    Get the plugin name of the synth that the preset was made for.
    Returns \"None\" if unknown
    """
    header = _read_header(file_path)
    if not header:
        return None
    
    signatures = _load_signatures()
    if not signatures:
        return None
    
    for plugin in signatures:
        if plugin['code'].strip().encode('utf-8') in header:
            return plugin['name'].strip()
    return None

def SetCode(file_path: str, new_code: str) -> bool:
    """
    Set the plugin code to the preset file.
    Returns True if successful, False if not
    """
    if len(new_code) != 4:
        return False
    if not os.path.isfile(file_path):
        return False
        
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if len(content) < 20:
                return False
            new_code_bytes = new_code.encode('utf-8')
            modified = content[:16] + new_code_bytes + content[20:]
            
        with open(file_path, 'wb') as f:
            f.write(modified)
        return True
    except:
        return False
    
def AddToDatabase(code: str, name: str, company: str) -> bool:
    """
    Add a new entry to the signature database
    Returns True if successful, False if not
    """
    if not code or len(code) != 4 or not name or not company:
        return False

    try:
        data = _load_signatures() or []
        data.append({
            "code": code.strip(),
            "name": name.strip(),
            "company": company.strip()
        })
        with open('signatures.json', 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except:
        return False

def RemoveFromDatabase(code: str) -> bool:
    """
    Remove an entry from the signature database
    Returns True if successful, False if not
    """
    try:
        data = _load_signatures()
        if not data:
            return False
        
        filtered = [entry for entry in data if entry['code'].strip() != code.strip()]
        if len(filtered) == len(data):
            return False
            
        with open('signatures.json', 'w') as f:
            json.dump(filtered, f, indent=4)
        return True
    except:
        return False

def EditDatabase(code: str, newcode: str, newname: str, newcompany: str) -> bool:
    """
    Edit an existing entry in the signature database
    Returns True if successful, False if not
    """
    if not newcode or len(newcode) != 4 or not newname or not newcompany:
        return False

    try:
        data = _load_signatures()
        if not data:
            return False
        
        for entry in data:
            if entry['code'].strip() == code.strip():
                entry['code'] = newcode.strip()
                entry['name'] = newname.strip()
                entry['company'] = newcompany.strip()
                with open('signatures.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return True
        return False
    except:
        return False

def FetchDatabase() -> dict:
    """
    Get all entries from the signature database as a dict
    Returns None if failed
    """
    return _load_signatures()

def Compare(file1_path: str, file2_path: str, num_bytes_to_compare: int = 100) -> dict:
    """
    Compare two preset files and return detailed comparison information.
    
    Args:
        file1_path (str): Path to the first preset file
        file2_path (str): Path to the second preset file
        num_bytes_to_compare (int): Number of bytes to compare (default: 100)
        
    Returns:
        dict: Dictionary containing comparison results with the following keys:
            - 'differences': List of (byte_index, file1_value, file2_value, difference) tuples
            - 'same_code': Boolean indicating if both files have the same plugin code
            - 'same_company': Boolean indicating if both files are from the same company
            - 'same_plugin': Boolean indicating if both files are for the same plugin
            - 'total_different_bytes': Count of bytes that differ between files
            - 'file1': Info about file1
            - 'file2': Info about file2
    """
    result = {
        'differences': [],
        'same_code': False,
        'same_company': False,
        'same_plugin': False,
        'total_different_bytes': 0,
        'file1': {
            'code': GetCode(file1_path),
            'company': GetCompany(file1_path),
            'name': GetName(file1_path)
        },
        'file2': {
            'code': GetCode(file2_path),
            'company': GetCompany(file2_path),
            'name': GetName(file2_path)
        }
    }
    if not _read_header(file1_path) or not _read_header(file2_path):
        return result
    result['same_code'] = (result['file1']['code'] == result['file2']['code'])
    result['same_company'] = (result['file1']['company'] == result['file2']['company'])
    result['same_plugin'] = (result['file1']['name'] == result['file2']['name'])
    try:
        with open(file1_path, 'rb') as f1:
            bytes1 = f1.read()
        with open(file2_path, 'rb') as f2:
            bytes2 = f2.read()
    except IOError as e:
        return result
    smaller_size = min(len(bytes1), len(bytes2))
    bytes_to_compare = min(smaller_size, num_bytes_to_compare)
    for i in range(bytes_to_compare):
        byte1 = bytes1[i]
        byte2 = bytes2[i]
        if byte1 != byte2:
            difference = byte1 - byte2
            result['differences'].append((i, byte1, byte2, difference))
            result['total_different_bytes'] += 1
    
    return result

class GUI:
    def __new__(cls):
        root = tk.Tk()
        app = super().__new__(cls)
        app.__init__(root)
        root.mainloop()
        return app
    def __init__(self, root):
        self.root = root
        root.title("FXP Utility")
        root.geometry("800x600")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_tab = ttk.Frame(self.notebook)
        self.compare_tab = ttk.Frame(self.notebook)
        self.set_code_tab = ttk.Frame(self.notebook)
        self.database_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.info_tab, text="Info")
        self.notebook.add(self.compare_tab, text="Compare")
        self.notebook.add(self.database_tab, text="Database")
        self.notebook.add(self.set_code_tab, text="Change Code")

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self._setup_info_tab()
        self._setup_compare_tab()
        self._setup_database_tab()
        self._setup_set_code_tab()

    def _setup_info_tab(self):
        file_frame = ttk.LabelFrame(self.info_tab, text="Preset File")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.info_file_path, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self._browse_info_file).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Get Info", command=self._get_file_info).pack(side=tk.LEFT, padx=5, pady=5)
        
        results_frame = ttk.LabelFrame(self.info_tab, text="File Information")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_frame = ttk.Frame(results_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Plugin Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text="Company:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text="Plugin Code:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.plugin_name_var = tk.StringVar()
        self.company_var = tk.StringVar()
        self.plugin_code_var = tk.StringVar()
        
        ttk.Label(info_frame, textvariable=self.plugin_name_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.company_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.plugin_code_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
    
    def _setup_compare_tab(self):
        file_frame = ttk.LabelFrame(self.compare_tab, text="Preset Files to Compare")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="File 1:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.compare_file1_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.compare_file1_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=lambda: self._browse_compare_file(1)).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="File 2:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.compare_file2_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.compare_file2_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=lambda: self._browse_compare_file(2)).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Bytes to compare:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.compare_bytes_var = tk.StringVar(value="100")
        ttk.Entry(file_frame, textvariable=self.compare_bytes_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Compare Presets", command=self._compare_files).grid(row=2, column=2, padx=5, pady=5)
        
        results_frame = ttk.LabelFrame(self.compare_tab, text="Comparison Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        summary_frame = ttk.Frame(results_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        file1_frame = ttk.LabelFrame(summary_frame, text="File 1")
        file1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(file1_frame, text="Plugin:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file1_frame, text="Company:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file1_frame, text="Code:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.file1_plugin_var = tk.StringVar()
        self.file1_company_var = tk.StringVar()
        self.file1_code_var = tk.StringVar()
        
        ttk.Label(file1_frame, textvariable=self.file1_plugin_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file1_frame, textvariable=self.file1_company_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file1_frame, textvariable=self.file1_code_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        file2_frame = ttk.LabelFrame(summary_frame, text="File 2")
        file2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(file2_frame, text="Plugin:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file2_frame, text="Company:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file2_frame, text="Code:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.file2_plugin_var = tk.StringVar()
        self.file2_company_var = tk.StringVar()
        self.file2_code_var = tk.StringVar()
        
        ttk.Label(file2_frame, textvariable=self.file2_plugin_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file2_frame, textvariable=self.file2_company_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(file2_frame, textvariable=self.file2_code_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        compare_frame = ttk.LabelFrame(results_frame, text="Comparison Summary")
        compare_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(compare_frame, text="Same plugin:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(compare_frame, text="Total different bytes:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.same_code_var = tk.StringVar()
        self.diff_bytes_var = tk.StringVar()
        
        ttk.Label(compare_frame, textvariable=self.same_code_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(compare_frame, textvariable=self.diff_bytes_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        diff_frame = ttk.LabelFrame(results_frame, text="Byte Differences")
        diff_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.diff_text = scrolledtext.ScrolledText(diff_frame, wrap=tk.WORD, height=10)
        self.diff_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_set_code_tab(self):

        file_frame = ttk.LabelFrame(self.set_code_tab, text="Select File")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.set_code_file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.set_code_file_path, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self._browse_set_code_file).pack(side=tk.LEFT, padx=5, pady=5)
        
        code_frame = ttk.LabelFrame(self.set_code_tab, text="New Plugin Code")
        code_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(code_frame, text="New Code (exactly 4 characters):").pack(side=tk.LEFT, padx=5, pady=5)
        self.new_code_var = tk.StringVar()
        ttk.Entry(code_frame, textvariable=self.new_code_var, width=10).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(code_frame, text="Set Code", command=self._set_code).pack(side=tk.LEFT, padx=5, pady=5)
        
        info_frame = ttk.LabelFrame(self.set_code_tab, text="Current File Info")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Current Plugin:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text="Current Company:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text="Current Code:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.current_plugin_var = tk.StringVar()
        self.current_company_var = tk.StringVar()
        self.current_code_var = tk.StringVar()
        
        ttk.Label(info_frame, textvariable=self.current_plugin_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.current_company_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, textvariable=self.current_code_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(info_frame, text="Refresh Info", command=self._refresh_set_code_info).grid(row=3, column=0, columnspan=2, pady=10)
    
    def _browse_info_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("VST Preset Files", "*.fxp;*.fxb"), ("All Files", "*.*")]
        )
        if file_path:
            self.info_file_path.set(file_path)
            self._get_file_info()
    
    def _browse_compare_file(self, file_num):
        file_path = filedialog.askopenfilename(
            filetypes=[("VST Preset Files", "*.fxp;*.fxb"), ("All Files", "*.*")]
        )
        if file_path:
            if file_num == 1:
                self.compare_file1_path.set(file_path)
            else:
                self.compare_file2_path.set(file_path)
    
    def _browse_set_code_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("VST Preset Files", "*.fxp;*.fxb"), ("All Files", "*.*")]
        )
        if file_path:
            self.set_code_file_path.set(file_path)
            self._refresh_set_code_info()
    
    def _get_file_info(self):
        file_path = self.info_file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a preset file first.")
            return
        
        self.status_var.set(f"Getting info for {os.path.basename(file_path)}...")
        self.root.update_idletasks()
        
        plugin_name = GetName(file_path)
        company = GetCompany(file_path)
        plugin_code = GetCode(file_path)
        
        self.plugin_name_var.set(plugin_name or "Unknown")
        self.company_var.set(company or "Unknown")
        self.plugin_code_var.set(plugin_code or "Unknown")
        
        self.status_var.set("Ready")
    
    def _compare_files(self):
        file1_path = self.compare_file1_path.get()
        file2_path = self.compare_file2_path.get()
        
        if not file1_path or not file2_path:
            messagebox.showwarning("Warning", "Please select two preset files to compare.")
            return
        
        try:
            num_bytes = int(self.compare_bytes_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Number of bytes must be an integer.")
            return
        
        self.status_var.set("Comparing files...")
        self.root.update_idletasks()
        
        result = Compare(file1_path, file2_path, num_bytes)
        
        self.file1_plugin_var.set(result['file1']['name'] or "Unknown")
        self.file1_company_var.set(result['file1']['company'] or "Unknown")
        self.file1_code_var.set(result['file1']['code'] or "Unknown")
        
        self.file2_plugin_var.set(result['file2']['name'] or "Unknown")
        self.file2_company_var.set(result['file2']['company'] or "Unknown")
        self.file2_code_var.set(result['file2']['code'] or "Unknown")
        
        self.same_code_var.set(str(result['same_code']))
        self.diff_bytes_var.set(str(result['total_different_bytes']))
        
        self.diff_text.delete(1.0, tk.END)
        if result['differences']:
            self.diff_text.insert(tk.END, "Byte differences (index, file1 value, file2 value, difference):\n")
            for diff in result['differences']:
                self.diff_text.insert(tk.END, f"Byte {diff[0]}: {diff[1]} vs {diff[2]} (diff: {diff[3]})\n")
        else:
            self.diff_text.insert(tk.END, "No byte differences found!")
        
        self.status_var.set("Ready")
    
    def _refresh_set_code_info(self):
        file_path = self.set_code_file_path.get()
        if not file_path:
            return
        
        plugin_name = GetName(file_path)
        company = GetCompany(file_path)
        plugin_code = ForceGetCode(file_path)
        
        self.current_plugin_var.set(plugin_name or "Unknown")
        self.current_company_var.set(company or "Unknown")
        self.current_code_var.set(plugin_code or "Unknown")
    
    def _set_code(self):
        file_path = self.set_code_file_path.get()
        new_code = self.new_code_var.get()
        
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        
        if len(new_code) != 4:
            messagebox.showwarning("Warning", "Code must be exactly 4 characters.")
            return
        
        self.status_var.set(f"Setting code for {os.path.basename(file_path)}...")
        self.root.update_idletasks()
        
        success = SetCode(file_path, new_code)
        
        if success:
            messagebox.showinfo("Success", f"Code for {os.path.basename(file_path)} has been set to '{new_code}'.")
            self._refresh_set_code_info()
        else:
            messagebox.showerror("Error", "Failed to set code. Check that the file is valid and accessible.")
        
        self.status_var.set("Ready")
    def _setup_database_tab(self):
        main_frame = ttk.Frame(self.database_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add", command=self._add_new_entry).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Refresh", command=self._refresh_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Save", command=self._save_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Update", command=self._update_database).pack(side=tk.RIGHT, padx=5, pady=5)

        columns = ("code", "name", "company")
        self.db_tree = ttk.Treeview(main_frame, columns=columns, show="headings")

        self.db_tree.heading("code", text="Code")
        self.db_tree.heading("name", text="Name")
        self.db_tree.heading("company", text="Company")
        self.db_tree.column("code", width=100)
        self.db_tree.column("name", width=200)
        self.db_tree.column("company", width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        self.db_tree.configure(yscroll=scrollbar.set)

        self.db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.db_tree.bind("<Double-1>", self._edit_entry)
        self.db_tree.bind("<Button-3>", self._delete_entry)
        self._refresh_database()

    def _refresh_database(self):
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        signatures = _load_signatures()
        if signatures:
            for entry in signatures:
                self.db_tree.insert("", tk.END, values=(entry["code"], entry["name"], entry["company"]))
        
        self.status_var.set("Database refreshed")

    def _save_database(self):
        entries = []
        for item_id in self.db_tree.get_children():
            values = self.db_tree.item(item_id, "values")
            entries.append({
                "code": values[0],
                "name": values[1],
                "company": values[2]
            })

        try:
            with open('signatures.json', 'w') as f:
                json.dump(entries, f, indent=4)
            messagebox.showinfo("Success", "Database saved successfully")
            self.status_var.set("Database saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save database: {str(e)}")
            self.status_var.set("Error saving database")

    def _update_database(self):
        url = "https://raw.githubusercontent.com/AbsoluteSkid/FXPUtil/refs/heads/main/signatures.json"  
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            with open('signatures.json', 'w') as f:
                json.dump(data, f, indent=4)
            
            self._refresh_database()
            messagebox.showinfo("Success", "Database updated successfully")
            self.status_var.set("Database updated")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
            self.status_var.set("Error updating database")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save database: {str(e)}")
            self.status_var.set("Error saving database")

    def _add_new_entry(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Entry")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Code (4 chars):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(dialog, text="Company:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        code_var = tk.StringVar()
        name_var = tk.StringVar()
        company_var = tk.StringVar()
        
        code_entry = ttk.Entry(dialog, textvariable=code_var, width=20)
        code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        company_entry = ttk.Entry(dialog, textvariable=company_var, width=20)
        company_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def add_and_close():
            code = code_var.get().strip()
            name = name_var.get().strip()
            company = company_var.get().strip()
            
            if not code or len(code) != 4:
                messagebox.showwarning("Invalid Entry", "Code must be exactly 4 characters")
                return
            
            if not name:
                messagebox.showwarning("Invalid Entry", "Name cannot be empty")
                return
            
            if not company:
                messagebox.showwarning("Invalid Entry", "Company cannot be empty")
                return
            
            self.db_tree.insert("", tk.END, values=(code, name, company))
            dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=add_and_close).grid(row=3, column=0, columnspan=2, pady=10)
        code_entry.focus_set()

    def _edit_entry(self, event):
        selected_item = self.db_tree.selection()
        if not selected_item:
            return
        current_values = self.db_tree.item(selected_item[0], "values")
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Entry")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Code (4 chars):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(dialog, text="Company:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        code_var = tk.StringVar(value=current_values[0])
        name_var = tk.StringVar(value=current_values[1])
        company_var = tk.StringVar(value=current_values[2])
        
        code_entry = ttk.Entry(dialog, textvariable=code_var, width=20)
        code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        company_entry = ttk.Entry(dialog, textvariable=company_var, width=20)
        company_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def update_and_close():
            code = code_var.get().strip()
            name = name_var.get().strip()
            company = company_var.get().strip()
            
            if not code or len(code) != 4:
                messagebox.showwarning("Invalid Entry", "Code must be exactly 4 characters")
                return
            
            if not name:
                messagebox.showwarning("Invalid Entry", "Name cannot be empty")
                return
            
            if not company:
                messagebox.showwarning("Invalid Entry", "Company cannot be empty")
                return
            
            self.db_tree.item(selected_item[0], values=(code, name, company))
            dialog.destroy()
        
        ttk.Button(dialog, text="Update", command=update_and_close).grid(row=3, column=0, columnspan=2, pady=10)

    def _delete_entry(self, event):
        item = self.db_tree.identify_row(event.y)
        if not item:
            return
        
        values = self.db_tree.item(item, "values")
        if messagebox.askyesno("Confirm Deletion", f"Delete entry for {values[1]}?"):
            self.db_tree.delete(item)
            self.status_var.set(f"Deleted entry for {values[1]}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='FXPUtil: A utility for working with VST preset files')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    compare_parser = subparsers.add_parser('compare', help='Compare two preset files')
    compare_parser.add_argument('-f1', type=str, required=True, help='Path to first preset file')
    compare_parser.add_argument('-f2', type=str, required=True, help='Path to second preset file')
    compare_parser.add_argument('-n', type=int, default=100, help='Number of bytes to compare (default: 100)')


    info_parser = subparsers.add_parser('info', help='Get information about a preset file')
    info_parser.add_argument('-f', type=str, required=True, help='Path to preset file')
    
    help_parser = subparsers.add_parser('help', help='Show this help message')
    args = parser.parse_args()
    
    if not args.command:
        print("Running GUI, because no command was specified. Type -h for help.")
        GUI()
        exit(0)
    if args.command == 'compare':
        result = Compare(args.f1, args.f2, args.n)
        print(f"File 1: {args.f1}")
        print(f"  Plugin: {result['file1']['name']}")
        print(f"  Company: {result['file1']['company']}")
        print(f"  Code: {result['file1']['code']}")
        print()
        
        print(f"File 2: {args.f2}")
        print(f"  Plugin: {result['file2']['name']}")
        print(f"  Company: {result['file2']['company']}")
        print(f"  Code: {result['file2']['code']}")
        print()
        
        print(f"Same plugin: {result['same_code']}")
        print(f"Total different bytes: {result['total_different_bytes']}")
        print()
        
        if result['differences']:
            print("Byte differences (index, file1 value, file2 value, difference):")
            for diff in result['differences']:
                print(f"  Byte {diff[0]}: {diff[1]} vs {diff[2]} (diff: {diff[3]})")
    
    elif args.command == 'info':
        print(f"File: {args.f}")
        print(f"Plugin: {GetName(args.f)}")
        print(f"Company: {GetCompany(args.f)}")
        print(f"Code: {GetCode(args.f)}")
