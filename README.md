# ChemDB: SDB Query Tool

**SDB Query Tool** is a GUI-based tool to automate the collection of chemical data, including labour security-related information, and to provide substance data sheets. 

### 📖 Background and Motivation

At the latest with the introduction of the REACH regulation (Registration, Evaluation, Authorization, and Restriction of Chemicals), practical users of chemicals have access to a wealth of information about the chemical itself, as well as its use from the perspective of labour safety.

To the best of my knowledge, there is currently no officially by European authorities provided, automated method to easily obtain chemical data and labour safety-related information when handling these chemicals. The SDB Query Tool aims to fill this gap until an official user-friendly alternative is offered by authoritative sources.

### ⚡️ Attention

**SDB Query Tool** is currently in beta. Also, be aware that this project is my first in many aspects: in Python, in using GitHub, in publishing software. If you choose to use it, be prepared for potential bugs. It would help me a lot if you report bugs, propose changes to the code you find helpful and contribute to the project in any other way.

### 👨‍⚖️ Use and Liability

**SDB Query Tool** is provided under [MIT License](https://github.com/MsrSiege/ChemDB?tab=MIT-1-ov-file#readme) as-is, without any warranty. You are free to use it as you like.

*Despite my best efforts to limit the amount of data collected and to increase the efficiency of data acquisition from the [Sources](#-sources), the tool could possibly be against the interests of the sources' operators.*

## ⚙️ Installation

I've developed this tool for MS Windows and will provide [pre-compiled versions](https://github.com/MsrSiege/ChemDB/releases/latest) for MS Windows to run as-is.

> Choose `ChemDB_VERSION.zip` if you have Google Chrome installed. If not or if you find yourself encountering errors with the tool, choose `ChemDB_VERSION_chrome.zip`!

> Check `Example_Files.zip` for example input and output files.

I didn't test the tool on other platforms. If you are familiar with GitHub feel free to clone the repository and use your IDE of choice.

## 👋 Usage

***1. Choose one or more files to process.*** <br>
Use the `File Dialog` button to choose one or more files. The path to the folder that contains the selected file(s) will be shown in the `Folder Path` box. Enable `All Files` to use all files in the folder path instead of the selected ones.

> The tool looks for the keywords `CAS` and `Name` in the column headers of the selected files. To accept a file as compatible, at least one of these keywords must be present. If the selected file contains more than one column with any of these keywords (i. e. "CAS" and "cas no"), it will get rejected.

> The tool currently supports `.xlsx`, `.xls` and `.csv` files.

***2. Analyse your files.*** <br>
You can check if the tool accepts your file(s) as compatible by clicking the `Analyse Files` button. The tool will show you the number of valid files, the identified chemicals count and the number of valid CAS number entries. 

> Details and errors will be printed to the `Log` box. You can toggle it by clicking the `Show Log`/`Hide Log` button.

***3. Process your files.*** <br>
You can process your files by clicking the `Process Files` button. The software will report the file and chemical it currently works on. You can cancel the processing by clicking the `Cancel` button. After processing, the tool will create a `*_OUT.xlsx` file containing the processed data and and subfolder `/SDB` containing the substance data sheets.

> Details and errors will be printed to the `Log` box. You can toggle it by clicking the `Show Log`/`Hide Log` button.

> ***Limitation***: Currently, the `Cancel` button doesn't work during multi-threaded processing!

***4. Customise your SDB Query Tool.*** <br>
By clicking the `Settings` button you can customise the SDB Query Tool. Choose the `Query Targets` (see [Sources](#-sources) for the data queried by each target) and select `Threading Settings`.

> Multi-threaded processing speeds up the processing by a lot. Single-threaded processing of 60 chemicals took 395 s, whilst multi-threaded processing took 118 s.

> ***Limitation***: As multi-threaded processing uses multiple concurrent connections to each query target, it is not only resource-heavy but also prone to errors due to timeouts of the web services. I found choosing `Max Threads` of `6` to result in the fastest processing time while not running into errors.

> ***Limitation***: Currently, it seems to be more error-prone to run `Process Files` consecutively. I recommend restarting the tool after each processing run.

## 🐞 Known Bugs

- The `Cancel` button doesn't work during multi-threaded processing.
> This hopefully will be fixed in a later version.
- Multi-threaded processing is prone to errors due to timeouts of the web services.
> This may not be resolvable. Experiment with `Max Threads`, I found a number of `6` works best for me.
- Running multi-threaded `Process Files` consecutively seems to increase the chance of errors.
> This hopefully will be fixed in a later version. Restart the tool between consecutive processing runs.

## 📚 Sources

Source                                       | Information queried
---------------------------------------------|----------------------------------
[ChemInfo](https://www.chemikalieninfo.de/)  | Chemical data, labour safety data
[PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Chemical data
[Gestis](https://gestis.dguv.de/)            | substance data sheet