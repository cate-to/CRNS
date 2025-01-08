# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:14:50 2025

@author: ctoscano
"""

#CONSTANTS 
import pandas as pd
import os

print("Starting up...")
stationsMetadata = pd.read_csv(os.getcwd() + '\\metadati_stazioni.csv')
print("You'll need to type the ID of the station. \n\tOZZANO DELL'EMILIA - 61\n\tCAVRIAGO - 65\n\tMARINA DI RAVENNA - 66\n\tSAN PIETRO CAPOFIUME - 60")
stationID = int(input("Your ID: "))
#stationID = 60
folderName = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[7] 

#site specific values
P_REF = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[2]          # DEPENDS ON SITE
N0 = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[4]             # DEPENDS ON SITE
BD = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[5]             # DEPENDS ON SITE
THETA_OFFSET = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[6]   # DEPENDS ON SITE
SATURATION = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[8]   # DEPENDS ON SITE
FIELD_CAPACITY = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[9]   # DEPENDS ON SITE
WILTING_POINT = stationsMetadata.loc[stationsMetadata.loc[(stationsMetadata == stationID).any(axis=1)].index[0]].iat[10]   # DEPENDS ON SITE


#atmospheric corrections
NINC_REF = 150
RH_REF = 0          # DEPENDS ON SITE?
ALPHA = 0.0054      
BETA = 0.0076

#conversion to soil moisture
A0 = 0.0808
A1 = 0.372
A2 = 0.115

###################################################


import csv
import numpy
import matplotlib.pyplot as plt


def prepareFiles(fileName, folderName):
    if fileName == 'ERG5' or fileName == "raw" or fileName == "finapp":
        separator = ','
    else:
        separator = ';'
    path = os.getcwd()
    df = pd.read_csv(os.getcwd() + '\\' + folderName + "\\" + fileName + '.csv', sep=separator, parse_dates=[0])
    start = df[df.columns[0]].min()
    end = df[df.columns[0]].max()
    df = df.drop_duplicates(subset=df.columns[0])
    new_index = pd.date_range(start=start, end=end, freq='h')
    df = df.set_index(df.columns[0]).reindex(new_index)
    df.to_csv(os.getcwd() + '\\' + folderName + '\\' + fileName + '_filled.csv', index_label='datetime')

def atmosphericCorrections(data):
    RH_REF = data["RHAVG"].mean()
    data["incoming_correction"] = NINC_REF/data["incoming"]
    data["press_correction"] = numpy.exp(BETA*(data["PRESS(hPa)"]-P_REF))
    #data['AH']=data['PRESS(hPa)']*100/(461.5*(data['TAVG']+273,15))
    #data["RH_correction"] = (1+ALPHA*(data["AH"]/100-RH_REF/100))
    data['RH_correction'] = 1
    data["corrected_neutrons"] = data["uncorrectedNeutrons"]*data["incoming_correction"]*data["press_correction"]*data["RH_correction"]
    data['movingAvg_neutrons'] = data['corrected_neutrons'].rolling(24, center=True).mean()

def calculateDailyAndBiWeeklyData(data):
    
    #create two pairs of daily and biweekly data: one for prec (needs to be summed) and one for everything else (needs to be averaged)
    dailyData = data.copy()
    biWeeklyData = data.copy()
    dailyPrec = data.copy()
    biWeeklyPrec = dailyPrec.copy()
    dailyPrec = dailyPrec.drop(columns=['uncorrectedNeutrons', 'incoming', 'TAVG', 'RHAVG', 'soil_moisture_volumetric[m3/m3]', 'soil_moisture_gravimetric[g/g]', 'pressureCorrectedNeutrons', 'PRESS(hPa)', 'incoming_correction', 'press_correction', 'RH_correction', 'corrected_neutrons', 'movingAvg_neutrons', 'soil_moisture'])#drop unused columns
    biWeeklyPrec = biWeeklyPrec.drop(columns=['uncorrectedNeutrons', 'incoming', 'TAVG', 'RHAVG', 'soil_moisture_volumetric[m3/m3]', 'soil_moisture_gravimetric[g/g]', 'pressureCorrectedNeutrons', 'PRESS(hPa)', 'incoming_correction', 'press_correction', 'RH_correction', 'corrected_neutrons', 'movingAvg_neutrons', 'soil_moisture'])#drop unused columns
    del(dailyData['PREC'])
    del(biWeeklyData['PREC'])
    
    #resampling of prec
    dailyPrec = dailyPrec.resample("D").sum()
    dailyPrec['cumulatedPrec'] = dailyPrec['PREC'].rolling(14).sum()
    biWeeklyPrec = biWeeklyPrec.resample("SME").sum()
    
    #resampling of everything else
    dailyData = dailyData.resample('D').mean()
    dailyData = pd.merge(dailyData, dailyPrec, how = 'inner', left_index = True, right_index = True)
    biWeeklyData = biWeeklyData.resample('SME').mean()
    biWeeklyData = pd.merge(biWeeklyData, biWeeklyPrec, how = 'inner', left_index = True, right_index = True)
    
    return dailyData, biWeeklyData

def plotDailyData(dailyData):
    fig, ax = plt.subplots(figsize=(30,5))
    ax2 = ax.twinx()
    x = dailyData.index
    ax2.bar(x, dailyData['cumulatedPrec'], width = 1.3, label = "cumulated precipitation", alpha=0.3)
    ax.plot(x, dailyData['soil_moisture'], label = "soil moisture", color = "red")
    ax.set_ylabel("soil moisture", fontsize = 12)
    ax2.set_ylabel("precipitation (mm)",fontsize=12)
    ax.axhline(y=SATURATION, ls='--', label="saturation", color = 'blue')
    ax.axhline(y=FIELD_CAPACITY, ls='--', label="field capacity", color = 'skyblue')
    ax.axhline(y=WILTING_POINT, ls='--', label="wilting point", color = 'gold')
    ax.set_title("DAILY - CRNS soil moisture vs prec",fontsize=18)
    ax.legend(fontsize=13,ncol = 3, loc='upper right')
    ax2.legend(fontsize=13, ncol = 3, loc="upper left")
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    plt.tight_layout()
    plt.show()
    fig.savefig(os.getcwd() + '\\' + folderName + '\\RESULTS\\dailyPlot.png')
    return

def plotBiWeeklyData(biWeeklyData):
    fig, ax = plt.subplots(figsize=(20,5))
    ax2 = ax.twinx()
    x = biWeeklyData.index
    ax2.bar(x, biWeeklyData['PREC'], width = 8, label = "cumulated precipitation", alpha=0.3, edgecolor='black')
    ax.plot(x, biWeeklyData['soil_moisture'], label = "soil moisture", color = "red")
    ax.set_ylabel("soil moisture", fontsize = 12)
    ax2.set_ylabel("precipitation (mm)",fontsize=12)
    ax.axhline(y=SATURATION, ls='--', label="saturation", color = 'blue')
    ax.axhline(y=FIELD_CAPACITY, ls='--', label="field capacity", color = 'skyblue')
    ax.axhline(y=WILTING_POINT, ls='--', label="wilting point", color = 'gold')
    ax.set_title("SEMIMONTHLY - CRNS soil moisture vs prec",fontsize=18)
    ax.legend(fontsize=13,ncol = 3, loc='upper right')
    ax2.legend(fontsize=13, ncol = 3, loc="upper left")
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    plt.tight_layout()
    plt.show()
    fig.savefig(os.getcwd() + '\\' + folderName + '\\RESULTS\\semiMonthlyPlot.png')
    return

#%%

def main():
    print("You'll need three types of file in the same folder as this script named: \n\traw.csv (contains raw Finapp data)\n\tincoming.csv (downloaded from https://www.nmdb.eu/nest/search.php)\n\tERG5.csv (ERG5 data relative to cell)\n\tfinapp.csv (corrected Finapp soil moisture data)\nCheck that they're there and press any key to continue. \n")
    
    print("Reading and tidying data...", end="")

    #fill holes in datasets
    #datasets used are: raw data from finapp, elaborated data from finapp, incoming data from https://www.nmdb.eu/nest/search.php , hourly ERG5 data (prec, tavg, RH)    
    prepareFiles('raw', folderName)
    prepareFiles('incoming', folderName)
    prepareFiles('ERG5', folderName)
    prepareFiles('finapp', folderName)
    
    print("Done!\nPreparing dataset...", end="")
    df1 = pd.read_csv(os.getcwd() + '\\' + folderName + '\\raw_filled.csv', parse_dates=[0])
    df2 = pd.read_csv(os.getcwd() + '\\' + folderName + '\\incoming_filled.csv', parse_dates=[0])
    df3 = pd.read_csv(os.getcwd() + '\\' + folderName + '\\ERG5_filled.csv', parse_dates= [0])
    df4 = pd.read_csv(os.getcwd() + '\\' + folderName + '\\finapp_filled.csv', parse_dates= [0])

    #set datetime index
    df1 = df1.set_index(df1.columns[0])
    df2 = df2.set_index(df2.columns[0])
    df3 = df3.set_index(df3.columns[0])
    df4 = df4.set_index(df4.columns[0])
    
    #drop unused columns before merging
    df1 = df1.drop(columns=['muons','gamma', 'integration_time(s)', 'V_in(Volt)', 'temperature_in(°C)', 'temperature_ext(°C)', 'ur(%)', 'pressure(hPa)'])
    df3 = df3.drop(columns=['RAD', 'W_SCAL_INT', 'W_VEC_DIR', 'W_VEC_INT', 'LEAFW', 'ET0'])
    df4 = df4.drop(columns=['muons','gamma', 'integration_time(s)', 'V_in(Volt)', 'temperature_in(°C)', 'temperature_ext(°C)', 'ur(%)'])
    df1.rename(columns={"neutrons":"uncorrectedNeutrons"}, inplace=True)
    df2.rename(columns={df2.columns[0]:"incoming"}, inplace=True)
    df4.rename(columns={"neutrons":"pressureCorrectedNeutrons", "pressure(hPa)":"PRESS(hPa)"}, inplace=True)

    
    #merge datasets to obtain a single one
    data = pd.merge(df1, df2, how = 'inner', left_index = True, right_index = True)
    data = pd.merge(data, df3, how = 'inner', left_index = True, right_index = True)
    data = pd.merge(data, df4, how = 'inner', left_index = True, right_index = True)
    
    #atmospheric corrections are applied
    print(" Done!\nCalculating atmospheric corrections and corrected neutron count...", end ="")
    atmosphericCorrections(data)
    print(" Done!")
    
    #soil moisture is calculated
    print("Calculating soil moisture...", end ="")
    data['soil_moisture'] = (A0/((data["movingAvg_neutrons"]/N0)-A1)-A2-THETA_OFFSET)*BD
    
    #hourly, daily, semi-monthly data
    data.to_csv(os.getcwd() + '\\' + folderName + '\\RESULTS\\hourlyData.csv')
    dailyData, biWeeklyData = calculateDailyAndBiWeeklyData(data)
    dailyData.to_csv(os.getcwd() + '\\' + folderName + "\\RESULTS\\dailyData.csv")
    biWeeklyData.to_csv(os.getcwd() + '\\' + folderName + "\\RESULTS\\biWeeklyData.csv")
    
    #plot data (daily and bi-weekly only)
    plotDailyData(dailyData)
    plotBiWeeklyData(biWeeklyData)
    
    print(" Done! \n\nYou can find the hourly, daily and bi-weekly results (.csv and plots) at: " + os.getcwd() + '\\' + folderName + "\\RESULTS")
    print("Note that the cumulatedPrec variable in the daily data has been calculated with a moving window of the previous 14 days.")

main()















