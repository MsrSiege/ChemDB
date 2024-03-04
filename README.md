# ChemDB: SDB Query Tool

**SDB Query Tool** is a GUI-based tool to automate the collection of chemical data, including labour security-related information, and to provide substance data sheets. 

### 📖 Background and Motivation

With the introduction of the REACH regulation (Registration, Evaluation, Authorization, and Restriction of Chemicals) at the latest, practical users of chemicals have access to a wealth of information about the chemical itself, as well as its use from the perspective of labour safety.

To the best of my knowledge, there is currently no officially by European authorities provided, automated method to easily obtain chemical data and labour safety-related information when handling these chemicals. The SDB Query Tool aims to fill this gap until an official user-friendly alternative is offered by authoritative sources.

### ⚡️ Attention

**SDB Query Tool** is currently in Beta. Be also aware that this project is my first in many regards: in Python, in using GitHub, in publishing software. If you choose to use it, be prepared for potential bugs. It would help me a lot if you report bugs, propose changes to the code you find helpful and contribute to the project in any other way.

## ⚙️ Installation

I've developed this tool for MS Windows and will provide a precompiled version for MS Windows to run as-is. I didn't test the tool on other platforms.

If you are familiar with GitHub feel free to clone the repostitory and use your IDE of choice.

## 👋 Usage

***1. Choose one ore more files to process.*** <br>
Use the `File Dialog` button to choose one or more files. The path to the folder that contains the selected file(s) will be shown in the `Folder Path` box. Enable `All Files` to use all files in the folder path instead of the selected ones.

> The tool looks for the keywords `CAS` and `Name` in the column headers of the selected files. To accept a file as compatible, at least one of these keywords must be present. If the selected file contains more than one column with one of these keywords, it will get rejected.

> The tool currently supports `.xlsx`, `.xls` and `.csv` files.

***2. Analyse your files.*** <br>
You can check if the tool accepts your file(s) as compatible by clicking the `Analyse Files` button. The tool will show you the number of valid files, the identified chemicals count and the number of valid CAS number entries. 

> Details and errors will be printed to the `Log` box. You can toggle it by clicking the `Show Log`/`Hide Log` button.

***3. Process your files.*** <br>
You can process your files by clicking the `Process Files` button. The software will report the file and chemical it currently works on. You can cancel the processing by clicking the `Cancel` button. After processing, the tool will create a `*_OUT.xlsx` file containing the processed data and and subfolder `/SDB` containing the substance data sheets.

> Details and errors will be printed to the `Log` box. You can toggle it by clicking the `Show Log`/`Hide Log` button.

> **Limitation**: Currently, the `Cancel` button doesn't work during multi-threaded processing!

***4. Customise your SDB Query Tool.*** <br>
By clicking the `Settings` button you can customise the SDB Query Tool. Choose the `Query Targets` (see below for the data queried by each target) and select `Threading Settings`.

> Multi-threaded processing speeds up the processing by a lot. Single-threaded processing of 60 chemicals took 395 s, whilst multi-threaded processing took 118 s.

> **Limitation**: As multi-threaded processing uses multiple concurrent connections to each query target, it is not only ressource-heavy but also prone to errors due to timeouts of the web services. I found choosing `Max Threads` of `6` to result in the fastest processing time while not running into errors.

> **Limitation**: Currently, it seems to be more error-prone to run `Process Files` consecutively. I recommend restarting the tool after each processing run.

## 📚 Sources

Source                                       | Information queried
---------------------------------------------|----------------------------------
[ChemInfo](https://www.chemikalieninfo.de/)  | Chemical data, labour safety data
[PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Chemical data
[Gestis](https://gestis.dguv.de/)            | substance data sheet

