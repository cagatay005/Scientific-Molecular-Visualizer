---Scientific Molecular Visualizer---
Real-time 3D molecular analysis tool built with RDKit, PubChemPy, Matplotlib, and CustomTkinter
<p align="center"> <img src="https://raw.githubusercontent.com/yourusername/yourrepo/main/demo.gif" width="60%" /> </p>
Scientific Molecular Visualizer is a modern, scientific desktop application that allows users to search by molecule name via PubChem, generate 3D coordinates, examine molecules by rotating them, obtain information by selecting atoms and bond types, and export data as PDB/XYZ.
This project offers an interactive molecular visualization experience for chemists, students, science enthusiasts, and developers.

***Features***
1. PubChem Integration
• Type in a molecule name → Data is automatically retrieved from PubChem
• Create 3D structures via SMILES using RDKit

2. Full 3D Interaction
• Rotate and zoom in a Matplotlib 3D environment
• Click on an atom to view element information
• Click on a bond to view Single / Double / Triple / Aromatic bond types
• Automatic detection of metallic / ionic interactions

3.True CPK Color System
• The full list of international CPK color standards is implemented in data.py.

4. PDB / XYZ Export
• One-click:
molecule.pdb
molecule.xyz
Saved via RDKit.

5. Modern Interface
• CustomTkinter Light Mode
• Responsive sidebar
• Live display of molecule properties

***Installation***
1. Clone the repository
git clone https://github.com/yourusername/molecular-visualizer.git
cd molecular-visualizer

3. Install Requirements
pip install -r requirements.txt

→ Main dependencies:
• rdkit
• pubchempy
• numpy
• matplotlib
• customtkinter

--RDKit installation is recommended via Conda:--
→ conda install -c conda-forge rdkit

--Run the Application
→ python molecular_visualizer.py


--- The program will automatically start by loading the Caffeine molecule. ---

+ Screenshots
<p align="center"> <img src="demo.gif" width="60%"> </p>

DEMO GIF: Interactive 3D visualization of the caffeine molecule with selectable atoms & bond types.

⚙️ Project Structure
MolecularVisualizer
├── data.py                     # CPK color standard and atom styles
├── molecular_visualizer.py     # Main application
├── demo.gif                    # Demonstration GIF
└── README.md

Technical Details
🔹 3D Coordinate Generation with RDKit
AddHs()
EmbedMolecule()
MMFFOptimizeMolecule()
🔹 Bond Classification System
Automatically detected and styled in code:
Bond Type	Style	Color
Single	Solid	#7F8C8D
Double	Solid	#2C3E50
Triple	Solid	#1A2530
Aromatic	Dashed	#E67E22
🔹 Selectable Atoms & Bonds
Implemented using objects from mpl_toolkits.mplot3d:
Path3DCollection (atoms)
Line3DCollection (bonds)
Both configured with picker=True to allow mouse interaction.
→ Export Features
Export as PDB:
Chem.MolToPDBFile(mol, file_path)
Export as XYZ:
Chem.MolToXYZFile(mol, file_path)

→ License
This project is released under the MIT License.

📝 License

This project is released under the MIT License.
