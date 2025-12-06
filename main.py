import math
import tkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox # Dosya kaydetme pencereleri için
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
import pubchempy as pcp
import threading
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Path3DCollection
import os # Dosya yolu işlemleri için
from data import ATOM_STYLES
# --- AYARLAR ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")
class ScientificChemistApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Molecular Visualizer")
        self.geometry("1280x850")
        self.after(0, lambda: self.state('zoomed'))
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.atoms_data = []
        self.current_mol = None # Export için mevcut molekülü hafızada tutacağız
        self.current_mol_name = ""
        self.setup_ui()
        self.setup_matplotlib()
        self.search_molecule_thread("Caffeine")

    def setup_ui(self):
        # BİLGİLENDİRME PANELİ
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#F0F0F0")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        # Başlık
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Moleküler\nAnaliz Aracı",
                                     font=ctk.CTkFont(size=20, weight="bold"), text_color="#333333")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        # Arama
        self.input_label = ctk.CTkLabel(self.sidebar_frame, text="Molekül Adı:", text_color="#555555", anchor="w")
        self.input_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.search_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Örn: Aspirin", fg_color="white", text_color="black")
        self.search_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.start_search())
        self.search_button = ctk.CTkButton(self.sidebar_frame, text="Analiz Et",
                                         command=self.start_search,
                                         fg_color="#2B5797", hover_color="#1E3E6E")
        self.search_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Sistem Hazır", text_color="#2B5797", font=("Arial", 12))
        self.status_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        # Özellikler
        self.props_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="white", border_color="#CCCCCC", border_width=1)
        self.props_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        self.mol_weight_label = ctk.CTkLabel(self.props_frame, text="Mol. Ağırlığı: -", text_color="#333333", anchor="w")
        self.mol_weight_label.pack(padx=10, pady=5, fill="x")
        self.formula_label = ctk.CTkLabel(self.props_frame, text="Formül: -", text_color="#333333", anchor="w")
        self.formula_label.pack(padx=10, pady=5, fill="x")
        # DIŞA AKTAR (EXPORT KISMI)
        self.export_label = ctk.CTkLabel(self.sidebar_frame, text="DIŞA AKTAR (3D Veri)",
                                         font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333", anchor="w")
        self.export_label.grid(row=6, column=0, padx=20, pady=(20, 10), sticky="w")
        self.export_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.export_frame.grid(row=7, column=0, padx=20, sticky="ew")
        # PDB Kaydet Butonu
        self.btn_save_pdb = ctk.CTkButton(self.export_frame, text="PDB Olarak Kaydet", command=lambda: self.save_molecule("pdb"),
                                          fg_color="#27AE60", hover_color="#219653", height=30)
        self.btn_save_pdb.pack(pady=5, fill="x")
        # XYZ Kaydet Butonu
        self.btn_save_xyz = ctk.CTkButton(self.export_frame, text="XYZ Olarak Kaydet", command=lambda: self.save_molecule("xyz"),
                                          fg_color="#E67E22", hover_color="#D35400", height=30)
        self.btn_save_xyz.pack(pady=5, fill="x")
        # Atom Bilgisi
        self.atom_info_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#E0E0E0")
        self.atom_info_frame.grid(row=9, column=0, padx=20, pady=20, sticky="s")
        self.atom_detail_label = ctk.CTkLabel(self.atom_info_frame, text="Seçili Atom: Yok", text_color="#333333")
        self.atom_detail_label.pack(pady=10)

    def setup_matplotlib(self):
        self.plot_frame = ctk.CTkFrame(self, fg_color="white")
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.fig = plt.figure(facecolor='white')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='white')
        self.ax.set_axis_off()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
    def start_search(self):
        name = self.search_entry.get()
        if name:
            self.search_molecule_thread(name)

    def search_molecule_thread(self, name):
        self.search_button.configure(state="disabled", text="Hesaplanıyor...")
        self.status_label.configure(text=f"Veri çekiliyor: {name}...", text_color="#E67E22")
        # Butonları devre dışı bırakma kısmı
        self.btn_save_pdb.configure(state="disabled")
        self.btn_save_xyz.configure(state="disabled")
        threading.Thread(target=self.perform_search, args=(name,), daemon=True).start()
    
    def perform_search(self, name):
        try:
            compounds = pcp.get_compounds(name, 'name')
            if not compounds:
                self.after(0, lambda: self.update_status(False, f"Bulunamadı: {name}"))
                return
            compound = compounds[0]
            smiles = compound.isomeric_smiles
            formula = compound.molecular_formula
            # RDKit Mol nesnesini saklama kısmı
            atoms, bonds, mol_obj = self.generate_3d_data(smiles)
            if mol_obj:
                self.current_mol = mol_obj # Molekülü hafızaya alma kısmı
                self.current_mol_name = name
                mw = Descriptors.MolWt(mol_obj)
            else:
                mw = 0
            self.after(0, lambda: self.visualize_molecule(atoms, bonds, name, formula, mw))
            self.after(0, lambda: self.update_status(True, "Hazır"))
        except Exception as e:
            self.after(0, lambda: self.update_status(False, f"Hata: {str(e)[:20]}..."))

    def update_status(self, success, message):
        self.search_button.configure(state="normal", text="Analiz Et")
        # Butonları tekrar aktif etme kısmı
        self.btn_save_pdb.configure(state="normal")
        self.btn_save_xyz.configure(state="normal")
        color = "#2B5797" if success else "#C0392B"
        self.status_label.configure(text=message, text_color=color)

    # --- KAYDETME İŞLEMİ ---
    def save_molecule(self, fmt):
        if not self.current_mol:
            messagebox.showerror("Hata", "Önce bir molekül yüklemelisiniz.")
            return

        # Varsayılan dosya adı oluştur
        default_name = "".join(x for x in self.current_mol_name if x.isalnum())
        if fmt == "pdb":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdb",
                initialfile=f"{default_name}.pdb",
                filetypes=[("Protein Data Bank Files", "*.pdb"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    Chem.MolToPDBFile(self.current_mol, file_path)
                    messagebox.showinfo("Başarılı", f"PDB dosyası kaydedildi:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Kaydetme Hatası", str(e))
        elif fmt == "xyz":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xyz",
                initialfile=f"{default_name}.xyz",
                filetypes=[("XYZ Cartesian Coordinates", "*.xyz"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    Chem.MolToXYZFile(self.current_mol, file_path)
                    messagebox.showinfo("Başarılı", f"XYZ dosyası kaydedildi:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Kaydetme Hatası", str(e))
    def generate_3d_data(self, smiles):
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return None, None, None
        mol = Chem.AddHs(mol)
        try:
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
        except:
            AllChem.EmbedMolecule(mol, useRandomCoords=True)
        conf = mol.GetConformer()
        atoms = []
        bonds = []
        for i, atom in enumerate(mol.GetAtoms()):
            pos = conf.GetAtomPosition(i)
            num = atom.GetAtomicNum()
            style = ATOM_STYLES.get(num, ATOM_STYLES['default'])
            atoms.append({
                'x': pos.x, 'y': pos.y, 'z': pos.z,
                'color': style['color'],
                'size': style['size'],
                'edge': style.get('edge', 'black'),
                'info': f"Element: {style.get('name')}\nAtom No: {num}\nHibritleşme: {atom.GetHybridization()}"
            })
        for bond in mol.GetBonds():
            bonds.append((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))
        # RDKit Mol nesnesini de geri döndürüyoruz ki kaydedebilelim
        return atoms, bonds, mol

    def visualize_molecule(self, atoms, bonds, name, formula, mw):
        self.ax.clear()
        self.ax.set_axis_off()
        self.atoms_data = atoms
        self.mol_weight_label.configure(text=f"Ağırlık: {mw:.2f} g/mol")
        self.formula_label.configure(text=f"Formül: {formula}")
        if not atoms: return
        # Atom Verileri
        xs = [d['x'] for d in atoms]
        ys = [d['y'] for d in atoms]
        zs = [d['z'] for d in atoms]
        colors = [d['color'] for d in atoms]
        sizes = [d['size'] * 0.8 for d in atoms]
        edges = [d['edge'] for d in atoms]

        # --- BAĞ TÜRÜNE GÖRE SINIFLANDIRMA ---
        # Hem koordinatları (segments) hem de bilgileri (info) tutacak listeler
        bond_groups = {
            'single': {'segs': [], 'info': [], 'color': '#7F8C8D', 'width': 1, 'style': 'solid'},
            'double': {'segs': [], 'info': [], 'color': '#2C3E50', 'width': 3, 'style': 'solid'},
            'triple': {'segs': [], 'info': [], 'color': '#1A2530', 'width': 5, 'style': 'solid'},
            'aromatic': {'segs': [], 'info': [], 'color': '#E67E22', 'width': 2, 'style': 'dashed'}
        }
        for start, end in bonds:
            p1 = atoms[start]
            p2 = atoms[end]
            segment = [(p1['x'], p1['y'], p1['z']), (p2['x'], p2['y'], p2['z'])]
            bond = self.current_mol.GetBondBetweenAtoms(start, end)
            b_type = bond.GetBondType()
            # Bağ bilgisini oluştur (Örn: "Tekli Bağ: C(1) - H(4)")
            a1_name = p1['info'].split('\n')[0].split(': ')[1]
            a2_name = p2['info'].split('\n')[0].split(': ')[1]
            bond_desc = f"{a1_name} - {a2_name}"
            if b_type == Chem.rdchem.BondType.SINGLE:
                key = 'single'
                desc = f"Tekli Bağ\n{bond_desc}"
            elif b_type == Chem.rdchem.BondType.DOUBLE:
                key = 'double'
                desc = f"Çiftli Bağ\n{bond_desc}"
            elif b_type == Chem.rdchem.BondType.TRIPLE:
                key = 'triple'
                desc = f"Üçlü Bağ\n{bond_desc}"
            elif b_type == Chem.rdchem.BondType.AROMATIC:
                key = 'aromatic'
                desc = f"Aromatik Bağ\n{bond_desc}"
            else:
                key = 'single'
                desc = f"Bağ\n{bond_desc}"
            bond_groups[key]['segs'].append(segment)
            bond_groups[key]['info'].append(desc)
        # Kovalent Bağları Çizme ve "picker" Ekleme
        for key, data in bond_groups.items():
            if data['segs']:
                lc = Line3DCollection(data['segs'], colors=data['color'],

                                      linewidths=data['width'], linestyles=data['style'], alpha=0.8)
                # Tıklanabilirlik ayarı (5 piksel tolerans)
                lc.set_picker(5)
                # Bilgiyi objenin içine gömüyoruz
                lc.bond_info_list = data['info']
                self.ax.add_collection3d(lc)
        # --- İYONİK VE METALİK BAĞ Kısmı (bağ tam adı verilmez ikisinden biri mantığı kullanılmıştır.) ---
        METALS = {3, 11, 12, 19, 20, 26, 27, 28, 29, 30, 46, 47, 48, 78, 79, 80, 92}
        inter_segs = []
        inter_info = []
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                atom1 = self.current_mol.GetAtomWithIdx(i)
                atom2 = self.current_mol.GetAtomWithIdx(j)
                n1, n2 = atom1.GetAtomicNum(), atom2.GetAtomicNum()
                if (n1 in METALS or n2 in METALS):
                    if self.current_mol.GetBondBetweenAtoms(i, j): continue
                    p1, p2 = atoms[i], atoms[j]
                    dist = np.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2 + (p1['z']-p2['z'])**2)
                    if dist < 2.6:
                        inter_segs.append([(p1['x'], p1['y'], p1['z']), (p2['x'], p2['y'], p2['z'])])
                        # Bilgi metni
                        a1_name = p1['info'].split('\n')[0].split(': ')[1]
                        a2_name = p2['info'].split('\n')[0].split(': ')[1]
                        inter_info.append(f"İyonik/Metalik Etkileşim\n{a1_name} ... {a2_name}\nMesafe: {dist:.2f} Å")

        if inter_segs:
            lc_inter = Line3DCollection(inter_segs, colors='#8E44AD', linewidths=1, linestyles='dashed', alpha=0.6)
            lc_inter.set_picker(5)
            lc_inter.bond_info_list = inter_info
            self.ax.add_collection3d(lc_inter)
        # Atomları Çizme kısmı
        self.ax.scatter(xs, ys, zs, s=sizes, c=colors, edgecolors=edges, linewidth=0.5, alpha=1.0, depthshade=False, picker=True)
        self.ax.text2D(0.02, 0.95, f"{name.upper()}", transform=self.ax.transAxes, color="#2C3E50", fontsize=16, weight='bold')
        if len(xs) > 0:
            center = np.mean([xs, ys, zs], axis=1)
            max_range = (np.max(np.abs(np.array([xs, ys, zs]).T - center)) + 1)
            self.ax.set_xlim(center[0]-max_range, center[0]+max_range)
            self.ax.set_ylim(center[1]-max_range, center[1]+max_range)
            self.ax.set_zlim(center[2]-max_range, center[2]+max_range)
        self.canvas.draw()

    def on_pick(self, event):
        # Tıklanan şey bir atom mu? (Path3DCollection = Noktalar/Scatter)
        if isinstance(event.artist, Path3DCollection):
            ind = event.ind[0]
            if ind < len(self.atoms_data):
                info = self.atoms_data[ind]['info']
                # Bilgi panelini güncelle
                self.atom_detail_label.configure(text=f"--- ATOM ---\n{info}")
        # Tıklanan şey bir bağ mı? (Line3DCollection = Çizgiler)
        elif isinstance(event.artist, Line3DCollection):
            try:
                ind = event.ind[0]
                # Bağın içine gizlediğimiz bilgiyi çek
                if hasattr(event.artist, 'bond_info_list'):
                    # Bazen tıklama hassasiyetinden dolayı index taşabilir, try-except ile koruyoruz
                    if ind < len(event.artist.bond_info_list):
                        info = event.artist.bond_info_list[ind]
                        self.atom_detail_label.configure(text=f"--- BAĞ ---\n{info}")
            except Exception as e:
                print(f"Bağ seçimi hatası: {e}")

if __name__ == "__main__":
    app = ScientificChemistApp()
    app.mainloop()
