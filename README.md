# CRNS
Python scripts to convert and plot CRNS data to soil moisture values.


## Managing input data

1. Each station must have a corresponding row inside the metadati_stazioni.csv file and a folder must be created accordingly to the folderName field in that file. Such folder must contain all the data necessary. Both the file and the folder must be placed inside the SCRIPT folder.
2. Necessary data is:
	1. finapp.csv - CRNS data. Download from the [Finapp cloud](http://cloud.finapptech.com/finapp/api/v2/getCSV_id.php?ID=61&D=1&SM=1&token=v3s364). Change the 'ID=61' in the url based on the station ID (from metadati_stazioni.csv).
	2. incoming.csv - data from the Jungfraujoch station. Download from [the nmdb website](https://www.nmdb.eu/nest/search.php).
 	3. ERG5.csv - meteorological data regarding the area in which the station is installed. **This file can be automatically downloaded and formatted by the script, but only if you don't have your VPN on.** If you're unable to turn off the VPN, you have to manually create ERG5.csv by downloading the data from [here](https://dati.arpae.it/dataset/erg5-interpolazione-su-griglia-di-dati-meteo) and putting all the data from the necessary years (e.g. 2023, 2024 and 2025) in a single .csv file. For the correct ERG5 cell, see the ERG5cellID column in metadati_stazioni.csv.
3. Input data will be rewritten without holes or duplicates. These files will be in the same folder as the input files.
4. Output data will be: three .csv files (hourly, daily, bi-weekly data) and two .jpg files (daily and bi-weekly graphs).
