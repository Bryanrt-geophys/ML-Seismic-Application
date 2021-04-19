# -*- coding: utf-8 -*-
"""
Spyder Editor

This is the EQT tutorial edited to gather data from NMTSO study area
"""


# Importing Data ---- 

import os

# Creates the path for where the station list is going to be placed 

json_basepath = os.path.join(os.getcwd(),"json/station_list.json")

from EQTransformer.utils.downloader import makeStationList

# Creates a list of stations found within coordinates, filter, and the time
# span to query data for  

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

# Detecting and Picking (Option 1) ----

# option 1 is recomended for days-1 month of data
# fallowing commands slices continous data into 1 min long arrays
# from each miniseed file and generates a CSV and hdf5

from EQTransformer.utils.hdf5_maker import preprocessor

preprocessor(preproc_dir="preproc", 
             mseed_dir='downloads_mseeds', 
             stations_json=json_basepath, 
             overlap=0.3, 
             n_processor=4)




from EQTransformer.core.trainer import trainer

trainer(input_hdf5='NMTSO_trainer.h5', 
        input_csv='meta_data.csv', 
        output_name='NMTSO_model_trainer', 
        cnn_blocks=2, lstm_blocks=1, 
        padding='same', 
        activation='relu', 
        drop_rate=0.2, 
        label_type='gaussian', 
        add_event_r=0.6, 
        add_gap_r=0.2, 
        shift_event_r=0.9, 
        add_noise_r=0.5, 
        mode='generator', 
        train_valid_test_split=[0.60, 0.20, 0.20], 
        batch_size=20, 
        epochs=10, 
        patience=2, 
        gpuid=None, 
        gpu_limit=None)




from EQTransformer.core.predictor import predictor

# Change the directory for input_model to match where the training model is 
# found. The tutorial uses EqT_model.h5 in the ModelsAndSampleData folder 

predictor(input_dir= 'downloads_mseeds_processed_hdfs', 
          input_model='final_model.h5', 
          output_dir='detections', 
          detection_threshold=0.3, # detection threshold can be low as the program is robust against false positives
          P_threshold=0.1,         # detection threshold can be low as the program is robust against false positives
          S_threshold=0.1,         # detection threshold can be low as the program is robust against false positives
          number_of_plots=10, 
          plot_mode='time')        # plot mode can be in either time or time_frequency

# Creates detection directory with results

# Detecting and Picking (Option 2) ----
"""
# Useful when using on downloaded miniseed data that is longer than a month long

from EQTransformer.core.mseed_predictor import mseed_predictor

mseed_predictor(input_dir='downloads_mseeds', 
                input_model='../../published_examples/EQTransformer/ModelsAndSampleData/EqT_model.h5', 
                stations_json=json_basepath, 
                output_dir='detections', 
                detection_threshold=0.3, 
                P_threshold=0.1, 
                S_threshold=0.1, 
                number_of_plots=100, 
                plot_mode='time_frequency', 
                overlap=0.3, 
                batch_size=500)
"""

# Visualization & Results ----

# checking data continuity

from EQTransformer.utils.plot import plot_data_chart

# Be sure the full path is provided to time_tracks.pkl from the cwd is provided 
# as the first argument in plot_data_chart 

plot_data_chart('preproc/time_tracks.pkl', time_interval=10)

# To check your thrshold of false negatives, first plot events picked from a selected times mseeds file

from EQTransformer.utils.plot import plot_detections, plot_helicorder

plot_helicorder(input_mseed='downloads_mseeds/PB11/TX.PB11.00.HHZ__20200902T000000Z__20200903T000000Z.mseed', 
                input_csv=None, 
                save_plot=True)   # be sure to add save_plot=True to view

# Next plot highlights detected events on the former plot

plot_helicorder(input_mseed='downloads_mseeds/DAG/SC.DAG.00.EHZ__20200902T000000Z__20200903T000000Z.mseed', 
                input_csv='detections/DAG_outputs/X_prediction_results.csv',
                save_plot=True)   # cant view without saving but overwrittes last plot

# using these two plots, threshold values can be determined as too high or low

# Visualizing number of events per station

# This is often helpful to determin if one station is problimatic (e.g. near
# anthropomorphic noise) and needs to be removed from analysis

# Be sure that the exact path to the station_list.json from the cwd is specified 

plot_detections(input_dir="detections", 
                input_json="json/station_list.json", 
                plot_type='station_map', 
                marker_size=50)

# next line generates histrgram of detected events for each station in the detection folder

plot_detections(input_dir="detections", 
                input_json="json/station_list.json", 
                plot_type='hist', 
                time_window=120)

# Phase Association ----

import shutil
import os
from EQTransformer.utils.associator import run_associator

out_dir = "association"
try:
        shutil.rmtree(out_dir)
except Exception:
        pass
os.makedirs(out_dir)

# Be sure to add output_dir= "asociation" to run_associator or files will be 
# saved in main directory
# Fix spelling of asociator and suggest spelling of traceNmae

run_associator(input_dir='detections', 
               start_time="2020-09-01 00:00:00.00", 
               end_time="2020-09-03 00:00:00.00",  
               moving_window=15, 
               pair_n=3, 
               output_dir= "association")
