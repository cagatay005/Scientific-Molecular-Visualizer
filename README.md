#  Scientific Molecular Visualizer
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![RDKit](https://img.shields.io/badge/Cheminformatics-RDKit-00CC00)
![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-11557c)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
**Scientific Molecular Visualizer** is a sophisticated desktop application designed for real-time 3D visualization and analysis of chemical compounds. It leverages **PubChemPy** for data retrieval and **RDKit** for computational chemistry calculations (MMFF optimization), rendered within a modern **CustomTkinter** interface.
![Application Demo](demo.gif)

##  Overview
This tool allows researchers, students, and developers to generate accurate 3D molecular structures simply by entering a compound name (e.g., *Caffeine, Aspirin*). Unlike static image viewers, it calculates atomic hybridization, detects bond types, and identifies potential ionic/metallic interactions in real-time.

##  Technical Architecture & Features
The project is built using a modular Python architecture, highlighting several advanced integration techniques:
* **Computational Chemistry (RDKit):**
    * **SMILES to 3D:** Converts isomeric SMILES strings into 3D coordinate systems.
    * **MMFF Optimization:** Utilizes the *Merck Molecular Force Field* to calculate the most stable 3D conformation (energy minimization).
    * **Hybridization Analysis:** Automatically detects and displays atomic hybridization states (sp, sp2, sp3).
* **Advanced Visualization (Matplotlib Embedding):**
    * **GUI Integration:** Embeds interactive Matplotlib 3D plots directly into the CustomTkinter window using `FigureCanvasTkAgg`.
    * **Event Handling:** Implements a "picking" mechanism (`pick_event`). Users can click on individual atoms or bonds to retrieve specific metadata (Element, Bond Type, Distance).
    * **CPK Standards:** Atoms are rendered according to international **CPK coloring and radius standards**, defined in a custom `data.py` layer.
* **Concurrency (Multithreading):**
    * API requests (PubChem) and heavy mathematical optimizations run on background **Daemon Threads**, ensuring the UI remains responsive and fluid during calculations.
* **Data Export:**
    * Supports exporting processed molecular data to **.PDB** (Protein Data Bank) and **.XYZ** (Cartesian Coordinates) formats for use in other scientific software.

##  Installation
Follow these steps to set up the project locally:
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
2.  **Install the required dependencies:**
    ```bash
    pip install customtkinter matplotlib numpy rdkit pubchempy
    ```
3.  **Run the application:**
    ```bash
    python molecular_visualizer.py
    ```

##  Usage Guide
1.  **Search:** Enter a chemical compound name (English) in the sidebar (e.g., `Serotonin`) and press **"Analiz Et"** (Analyze).
2.  **Interact:**
    * **Rotate:** Click and drag with the left mouse button.
    * **Zoom:** Use the scroll wheel or right-click drag.
    * **Inspect:** Click on any atom or bond to view detailed properties in the info panel.
3.  **Export:** Use the "Save as PDB" or "Save as XYZ" buttons to save the 3D structure to your disk.

##  Project Structure
* `molecular_visualizer.py`: **Core Application.** Handles the GUI logic, Matplotlib embedding, threading, and main event loop.
* `data.py`: **Data Dictionary.** Contains the CPK color codes, atomic radii, and element metadata.
* `demo.gif`: **Preview Asset.** Demonstration of the application in action.
##  License
This project is licensed under the MIT License. See the `LICENSE` file for details.
