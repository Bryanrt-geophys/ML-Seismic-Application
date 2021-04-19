# EQTransformer 
1. Of the three methods, EQT is the most established, referenced, and published in the most reputable journal.
2. Authors are highly active on the GitHub Issues page, this is a great reference to trouble shoot problems.
3. Method works well on provided sample data and is easy to use, retraining is necessary for application to local data sets. However, retraining is well instructed in step 3.5 in the tutorial. Data wrangling and tidying necessary for retraining.

## Operating System
- Code was created on MacOS. Thus, this is the preferntial working OS.
- Have not tested Windows or Linux

## Creating Virtual Enivironment
The first step in the tutorial to get this project to work is creating the virtual environment and loading the proper packages in thier compatable versions. I have created a [file](EQT_Packages) to that can be used from the shell window to create the virtual environemnt and load all packages in the versions that the author helped me get to work at this date (02.16.2021).

## Using the EQTransformer Python Package
We can collect data within the NMTSO study area with functions built into the EQT package by populating the variables with applicable data. The full python file to run the EQTransformer tutorial can be found [here](spyder/EQTransformer_test/project/eqtTutorial.py). This works well if we use the provided data sets but the provided training model does not qadiquately charectorize NMTSO and must be retrained.

## Retraining the Model
To build a training model, data must be set up in the [STEAD format](https://github.com/smousavi05/STEAD). I have cerated a workflow, explained here, to convert the NMTSO data into the STEAD format so we can pass this back into the EQTransformer package to create a new training model to test on our data. 

### hdf5 File Format
EQTransformer is trained by passing labeled picutres of the waveforms into the algorithm. The data is contained in a python based, nested format called hdf5. Because of my experience in data maniulation in R, the way that R handles data inately in the same manner as hdf5 was created to replicate, and the existing hdf5r package in the R language, I will be working all NMTSO into hdf5 format by way of R.

### Finding what stations are going to go into the model
We can perform an API query from IRIS to find what stations are available within a given latitude-longitutde box. This can can be filtered by date, channels, network, and then told which stations to omit. 
```
import os

json_basepath = os.path.join(os.getcwd(),"json/station_list.json")

from EQTransformer.utils.downloader import makeStationList

makeStationList(json_path=json_basepath,
                client_list=["IRIS"], 
                min_lat=31.00, 
                max_lat=33.50, 
                min_lon=-105.00, 
                max_lon=-102.00, 
                start_time="2020-09-01 00:00:00.00", 
                end_time="2020-09-03 00:00:00.00", 
                channel_list=["HHZ", "HHE", "HHN", "EHZ"], 
                filter_network=["SY", "PN"], 
                filter_station=["DG01", "DG02", "DG03", "DG04", "DG05", "DG06", "DG07", "DG08", "DG09", 
                                "MB01", "MB02", "MB04", "MB07",
                                 "PB03", "PB04", "PB06", "PB02", "PB09", "PB10", "PB12", "PB13", "PB14", "PB15",
                                  "PB16", "PB18", "PB19", "PB21", "PB28", "PB29", "PB30", "PB31", "PB32", "PB33"])
```

### Gathering NMTSO Data to Merge 
Using the terminal window, remote access the bureau machine to wrangle data:
- Use matcha login info to access picfil.dat files to begin building STEAD dataframes `SSH -XY .....@mathca.nmt.edu`
- `csh`
- `source .cshrc`
- `bryant`
- `cd ..`
- This takes me to the available data sets
- Move to a chosen date to access the months located data: `cd 202012/located/`
- `scp -r ....@match.nmt.edu: ?WORK/nmtso.data/locations/WIPP/bryanrt/MAN$` will copy all directories in the path whose names end in "MAN" to the local machine 

Once the files are on the local machine, data for labeling the seismic signal (hdf5 attributes) will be taken from select .dat files. 

The trace data is contained in the SAC files. However, the SAC files NMTSO uses to interpret by hand are cute into 180 second intervals. This is not the standard STEAD format. For this reason we will use EQTransformer to gather minisead data that we can convert to SAC using IRIS' [mseed2SAC](https://github.com/iris-edu/mseed2sac). Install and compile this program as instructed to create the mseed2SAC exicutable. This will be important later on.


```
from EQTransformer.utils.downloader import downloadMseeds

# Downloads station data found for stations on list

downloadMseeds(client_list=["IRIS"], 
               stations_json=json_basepath, 
               output_dir="downloads_mseeds", 
               min_lat=31.00, 
               max_lat=33.50, 
               min_lon=-105.00, 
               max_lon=-102.00, 
               start_time="2020-09-01 00:00:00.00", 
               end_time="2020-09-03 00:00:00.00", 
               chunk_size=1, 
               channel_list=["HHZ", "HHE", "HHN", "EHZ", "HH1", "HH2"], 
               n_processor=4)
```
### Converting mseed Files to SAC 
To provide the trace data (e.g. singal and noise) necissary to load into the hdfy format that EQTransformer requires to build a training model, I have written [using_mseed2sac.R](R_wrangle_data/using_mseed2sac.R). Insure the pointers within the here() functions point to the appropriate directory where you installed the mseed2sac program and run this file and where the station_list is found. This will cerate new subdirectories into a SAC directory within the wd. The subdirectories will be named by the station from the station_list that had data available. All mseed data will be accessed, converted to SAC format, and then moved into the newly created subdirectories. This file will later be turned into a function to pass into the final MAKE to foramalize the workflow.

From here, I am currently working on properly merging and splitting these files in accordance with EQTransformer's requesits. A new R file will be linked here to use when this process is complete. This will then be passed as the objects into the hdf5 file for training EQTransformer. 

### Gathering Attribute data from .dat files
The SAC files will provide the trace data (e.g. the pictures) to train our model, but these data need labels. I have written [wrangling_STEAD.R](R_wrangle_data/wrangling_STEAD.R) to look through the .dat files pulled from the NMTSO database that was coppied to the local machine in the "Gathering NMTSO Data to Merge" step completed above. This file organizes all labels into a singular dataframe that can be munipulated to match the STEAD formatting and then passed as the attributes in the hdf5 file and paired with the objects based on a source_id variable wich will be included in both data sets.This file will later be turned into a function to pass into the final MAKE to foramalize the workflow.

### Creating the Training Model 
I have created the [hdf5_learning.R](R_wrangle_data/hdf5_learning.R) file to help the user understand the way that hdf5 formatting works and it's last section is being made to take the objects from using_mseed2sac and wrangling_STEAD. In the final _targets.R file (a MAKE-like compiler) each of these functions will be used to create one hdf5 and one csv file that will then be passed into the EQTransformer predictor() function.

```
from EQTransformer.core.predictor import predictor

# Change the directory for input_model to match where the training model is 
# found

predictor(input_dir= 'downloads_mseeds_processed_hdfs', 
          input_model='../../../published_examples/EQTransformer/ModelsAndSampleData/EqT_model.h5', 
          output_dir='detections', 
          detection_threshold=0.3, # detection threshold can be low as the program is robust against false positives
          P_threshold=0.1,         # detection threshold can be low as the program is robust against false positives
          S_threshold=0.1,         # detection threshold can be low as the program is robust against false positives
          number_of_plots=10, 
          plot_mode='time')        # plot mode can be in either time or time_frequency


```
