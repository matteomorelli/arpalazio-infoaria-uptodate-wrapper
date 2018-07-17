# Copyright (c) 2018 ARPA Lazio <craria@arpalazio.it>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import argparse
import datetime
import logging
import ConfigParser
import os.path
import subprocess

# Script version
VERSION = "0.3.0"


def validate_input_date(time_string):
    # Declare error message
    msg = "Not a valid date or valid date format: %s" % (time_string)
    # Start testing
    if time_string.count("/") == 2:
        year, month, day = time_string.split("/")
        try:
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            raise argparse.ArgumentTypeError(msg)
        return time_string
    raise argparse.ArgumentTypeError(msg)


def validate_input_hour(hour_string):
    # Declare error message
    msg = "Not a valid hour format: %s" % (hour_string)
    # Adapt string from range 1 <= hour <= 24
    # to 0 <= hour < 24
    check_hour = int(hour_string) - 1
    try:
        datetime.time(check_hour)
    except ValueError:
        raise argparse.ArgumentTypeError(msg)
    return hour_string


def simple_file_check(file_str):
    try:
        with open(file_str) as f:
            f.read()
            pass
    except IOError as err:
        # TODO(matteo.morelli@gmail.com): fail gracefuly and output with logger handler
        print "%s - %s" % (file_str, err)
        return False
    return True


def _define_check_args(parser):
    ##############################################
    # Function to chek valid input format
    # Arguments:
    #   a parser from argparse module
    # Returns:
    #   a tuple
    ##############################################
    parser.add_argument("ini_file", help="Location of wrapper configuration \
                        file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity")
    parser.add_argument("-s", "--start", type=validate_input_date,
                        help="Starting day YYYY/MM/DD. Default: yesterday")
    parser.add_argument("-e", "--end", type=validate_input_date,
                        help="Ending day YYYY/MM/DD. Default: today")
    parser.add_argument("-H", "--hour", type=validate_input_hour,
                        help="Hour to be processed/transmitted, format HH.\
                        Default: current hour.")
    args = parser.parse_args()
    # initialize variable
    start = args.start
    end = args.end
    hour = args.hour
    # Set optional value to default
    if start is None:
        start = datetime.datetime.strftime(datetime.datetime.now() -
                                           datetime.timedelta(1), '%Y/%m/%d')
    if end is None:
        end = datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d')
    if hour is None:
        system_hour = datetime.datetime.strftime(datetime.datetime.now(), '%H')
        # Apply a correction for ecomanager time system 1 <= time <= 24
        # against system time 0 <= time < 24
        hour = int(system_hour) + 1
        if hour < 10:
            hour = "0" + hour
    return (args.ini_file, start, end, hour, args.verbose)


def _parse_configuration_value(ini_path):
    cfg = ConfigParser.SafeConfigParser()
    try:
        cfg.read(ini_path)
        # Build dict from configuration file
        executable = {
            'dataorganizer': cfg.get("main", "dataorganizer"),
            'mainelab': cfg.get("main", "mainelab"),
            'infoaria': cfg.get("main", "infoaria"),
            'db_download': cfg.get("main", "db_download")
        }
        dataorganizer = {
            'ini_file': cfg.get("dataorganizer", "ini_file"),
            'delta_time': cfg.get("dataorganizer", "delta_time"),
            'provs': cfg.get("dataorganizer", "provs"),
            'do_input_datafile': cfg.get("dataorganizer", "do_input_datafile"),
            'output_path': cfg.get("dataorganizer", "output_path")
        }
        infoaria = {
            'sampling_point': cfg.get("infoaria", "sampling_point"),
            'pollutant_file': cfg.get("infoaria", "pollutant_file"),
            'station_file': cfg.get("infoaria", "station_file"),
            'output_path': cfg.get("infoaria", "output_path"),
            'output_file_suffix': cfg.get("infoaria", "output_file_suffix"),
            'output_file_extension':
            cfg.get("infoaria", "output_file_extension")
        }
    except ConfigParser.NoOptionError as err:
        # TODO(matteo.morelli@gmail.com): output with a logger handler
        print "|E| Error in INI file: %s" % (err)
        exit(1)
    except ConfigParser.ParsingError as err:
        # TODO(matteo.morelli@gmail.com): output with a logger handler
        print "|E| There is a syntax error in your INI file: %s" % (ini_path)
        exit(1)
    return executable, dataorganizer, infoaria


def _validate_configuration_value(cfg_dict):
    ##############################################
    # Function to validate that file and directory declared by the use
    # in the INI file exist and are accessible
    # Arguments:
    #   a dictionary with configuration value
    # Returns:
    #   True if everything fine
    #   False if value is not the expected one
    ##############################################
    if cfg_dict and type(cfg_dict) is dict:
        check_result = list()
        # Choose which check to perform based on key ecistence
        if 'dataorganizer' in cfg_dict:
            check_result.append(os.path.isfile(cfg_dict['dataorganizer']))
            check_result.append(os.path.isfile(cfg_dict['mainelab']))
            check_result.append(os.path.isfile(cfg_dict['infoaria']))
            check_result.append(os.path.isfile(cfg_dict['db_download']))

        if 'ini_file' in cfg_dict:
            check_result.append(os.path.isfile(cfg_dict['ini_file']))
            check_result.append(os.path.isdir(cfg_dict['output_path']))
            # Check that DataOrganizer data file is not empty or further
            # execution and processing will fail
            if cfg_dict['do_input_datafile']:
                check_result.append(True)
            else:
                check_result.append(False)
            # Check that delta_time is valid value [3, 6, 24]
            dt_valid_values = ["3", "6", "24"]
            if cfg_dict['delta_time'] in dt_valid_values:
                check_result.append(True)
            else:
                check_result.append(False)

        if 'sampling_point' in cfg_dict:
            check_result.append(os.path.isfile(cfg_dict['sampling_point']))
            check_result.append(os.path.isfile(cfg_dict['pollutant_file']))
            check_result.append(os.path.isfile(cfg_dict['station_file']))
            check_result.append(os.path.isdir(cfg_dict['output_path']))
            if cfg_dict['output_file_suffix'] and \
               cfg_dict['output_file_extension']:
                check_result.append(True)
            else:
                check_result.append(False)
        # All configuration variable checked if all results are True everything
        # is fine
        if check_result and False not in check_result:
            return True
    return False


def main():
    # TODO: build a log handler class

    parser = argparse.ArgumentParser()
    input_value = _define_check_args(parser)
    # Initialize variable
    conf_file = input_value[0]
    start_day = input_value[1]
    end_day = input_value[2]
    hour = input_value[3]
    verbose = input_value[4]

    if not simple_file_check(conf_file):
        exit(1)
    # Some visual input for the user
    print "|I| InfoAria wrapper initializing"
    print "|I| Configuration file: %s" % (conf_file)
    print "|I| Time period: %s => %s" % (start_day, end_day)
    print "|I| Processing time: %s" % (hour)
    # TODO(matteo.morelli@gmail.com): get return var from function
    if verbose:
        print "|I| Log level: DEBUG"
        # TODO(matteo.morelli@gmail): set logger to debug level
    bin_file, dorganizer, infoaria = _parse_configuration_value(conf_file)

    # Initialize InfoAria specific variable
    infoaria_datetime = end_day.replace("/", "") + str(hour)
    infoaria_year = infoaria_datetime[0:4]
    infoaria_file_out = infoaria['output_path'] \
                        + infoaria['output_file_suffix'] \
                        + infoaria_datetime \
                        + infoaria['output_file_extension']
    print "|I| Output file: %s" % (infoaria_file_out)

    # Convert dorganizer provs into a list for post processing
    if not dorganizer['provs']:
        print "|E| Error in your INI file: no province set."
        exit(1)
    dorganizer['provs'] = dorganizer['provs'].strip("\"").split(",")
    # Check all file existence before going to execution
    if not _validate_configuration_value(bin_file):
        print "|E| Error in [main] section of INI file: %s" % (conf_file)
        exit(1)
    if not _validate_configuration_value(dorganizer):
        print "|E| Error in [dataorganizer] section of INI file: %s"\
            % (conf_file)
        exit(1)
    if not _validate_configuration_value(infoaria):
        print "|E| Error in [infoaria] section of INI file: %s" % (conf_file)
        exit(1)
    # Now go live! Downloading db data from ecomanager server
    print "|I| Executing ecomanager_db_download.sh script"
    db_output_file = dorganizer['output_path'] \
        + dorganizer['do_input_datafile']
    db_data = subprocess.call([bin_file['db_download'],
                               '-t', 'i',
                               '-s', start_day,
                               '-e', end_day,
                               '-o', db_output_file])
    if db_data != 0:
        print "|E| Something wrong with data download"
        exit(1)
    print "|I| Executon of ecomanager_db_download.sh script, DONE"
    # Cycle through configured province
    # and execute both DataOrganizer and MainElab

    # Open some file for logging stdout and stderr
    dorganizer_logfile = dorganizer['output_path'] + "dataorganizer.log"
    mainelab_logfile = dorganizer['output_path'] + "mainelab.log"
    infoaria_logfile = dorganizer['output_path'] + "infoaria.log"
    try:
        do_file = open(dorganizer_logfile, "w")
        mainelab_file = open(mainelab_logfile, "w")
        infoaria_file = open(infoaria_logfile, "w")
    except IOError as err:
        print "|E| %s" % (err)
        exit(1)
    for prov in dorganizer['provs']:
        print "|I| Parsing province: %s" % (prov)
        print "|I| Executing: %s" % (bin_file['dataorganizer'])
        do_execution = subprocess.call([bin_file['dataorganizer'],
                                        dorganizer['ini_file'],
                                        start_day,
                                        end_day,
                                        dorganizer['delta_time'],
                                        prov], stdout=do_file, stderr=do_file)
        if do_execution != 0:
            print "|E| Something wrong with: %s" % (bin_file['dataorganizer'])
            exit(1)
        print "|I| Executing: %s" % (bin_file['mainelab'])
        mainelab_execution = subprocess.call([bin_file['mainelab'],
                                              dorganizer['ini_file'],
                                              start_day,
                                              end_day,
                                              prov],
                                             stdout=mainelab_file,
                                             stderr=mainelab_file)
        if mainelab_execution != 0:
            print "|E| Something wrong with: %s" % (bin_file['mainelab'])
            exit(1)
    do_file.close()
    mainelab_file.close()
    # Convert data to InfoAria specification
    print "|I| Executing: %s" % (bin_file['infoaria'])
    infoaria_execution = subprocess.call([bin_file['infoaria'],
                                          infoaria_datetime,
                                          infoaria['sampling_point'],
                                          infoaria['pollutant_file'],
                                          infoaria['station_file'],
                                          infoaria_year,
                                          infoaria_file_out],
                                         stdout=infoaria_file,
                                         stderr=infoaria_file
                                         )
    if infoaria_execution != 0:
        print "|E| Something wrong with: %s" % (bin_file['infoaria'])
        exit(1)
    infoaria_file.close()
    # Check network status
    # 
    # Start of user requested network transmission protocol
    # 
    # Checking transmission execution
    # 
    # Closing transmission and quitting execution


if __name__ == ("__main__"):
    main()
