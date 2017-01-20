#!../venv/bin/python 
''' Python script to generate new run plan docs

Author: Ed Leming
Date:   28/07/2016
'''
import argparse
import json
import datetime
import pytz
import sys
try:
    import database
except:
    print "Please run from inside newSmellie/database_file_builder"
    sys.exit()

def run_info(name):
    '''Create a run file
    '''
    # Make run_info field to describe the run
    run_info = {}
    # GLOBALS
    run_info["run_name"] = name
    run_info["operation_mode"] = "Master Mode"
    run_info["trigger_frequency"] = 1000
    run_info["triggers_per_loop"] = 1000

    # LASERS
    run_info["375nm_laser_on"] = 1 # 0/1 is off/on
    run_info["405nm_laser_on"] = 0
    run_info["440nm_laser_on"] = 0
    run_info["500nm_laser_on"] = 0
    run_info["superK_laser_on"] = 1

    # FIBRES
    run_info["FS007"] = 0
    run_info["FS107"] = 0
    run_info["FS207"] = 0
    # 25s
    run_info["FS025"] = 0
    run_info["FS125"] = 0
    run_info["FS225"] = 0
    #37s
    run_info["FS037"] = 0
    run_info["FS137"] = 0
    run_info["FS237"] = 0
    #55s
    run_info["FS055"] = 1
    run_info["FS155"] = 0
    run_info["FS255"] = 0
    #93s
    run_info["FS093"] = 0
    run_info["FS193"] = 0
    run_info["FS293"] = 0

    # WAVELENGTHS for superK
    run_info["superK_wavelength_start"] = 4000     # 1e-10m
    run_info["superK_wavelength_step_length"] = 50 # 1e-10m
    run_info["superK_wavelength_bandwidth"] = 100  # 1e-10m
    run_info["superK_wavelength_no_steps"] = 1     # How man steps of 

    # INTENSITIES for fixed wavelengths
    run_info["375nm_intensity_minimum"] = 10       # %
    run_info["375nm_intensity_increment"] = 20     # %
    run_info["375nm_intensity_no_steps"] = 1       # 
    #
    run_info["405nm_intensity_minimum"] = 10       # %
    run_info["405nm_intensity_increment"] = 20     # %
    run_info["405nm_intensity_no_steps"] = 1       # 
    #
    run_info["440nm_intensity_minimum"] = 10       # %
    run_info["440nm_intensity_increment"] = 20     # %
    run_info["440nm_intensity_no_steps"] = 1       # 
    #
    run_info["500nm_intensity_minimum"] = 10       # %
    run_info["500nm_intensity_increment"] = 20     # %
    run_info["500nm_intensity_no_steps"] = 1       # 

    # currently the superK intensity has no physical meaning, but has been requested
    run_info["superK_intensity_minimum"] = 10      # %
    run_info["superK_intensity_increment"] = 20    # %
    run_info["superK_intensity_no_steps"] = 1      # 

    # GAIN settings for monitoring PMT
    run_info["375nm_gain_minimum"] = 0.25          # V
    run_info["375nm_gain_increment"] = 0.05        # V
    run_info["375nm_gain_no_steps"] = 1            # 
    #
    run_info["405nm_gain_minimum"] = 0.25          # V
    run_info["405nm_gain_increment"] = 0.05        # V
    run_info["405nm_gain_no_steps"] = 1            #
    #
    run_info["440nm_gain_minimum"] = 0.25          # V
    run_info["440nm_gain_increment"] = 0.05        # V
    run_info["440nm_gain_no_steps"] = 1            #
    #
    run_info["500nm_gain_minimum"] = 0.25          # V
    run_info["500nm_gain_increment"] = 0.05        # V
    run_info["500nm_gain_no_steps"] = 1            #
    #
    run_info["superK_gain_minimum"] = 0.25         # V
    run_info["superK_gain_increment"] = 0.05       # V
    run_info["superK_gain_no_steps"] = 1           #
    
    # DELAYS TO BE APPLIED TO TRIGGERS BEFORE REACHING THE MTCD
    run_info["delay_fixed_wavelength"] = 400                # ns
    run_info["delay_superK"] = 400                 # ns

    return run_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('run_name', type=str,
                        help='name of this run decription [superK_structure_example]')
    parser.add_argument('-s', dest='server', 
                        help='database server [http://couch.snopl.us]',
                        default='http://couch.snopl.us')
    parser.add_argument('-d', dest='database', help='database name [smellie]',
                        default='smellie')
    args = parser.parse_args()

    # Make a database document. Fill run_info fields using the provided function
    document = {}
    document["doc_type"] = "smellie_run_description"
    document["run_info"] = run_info(args.run_name)
    document["time_stamp"] = datetime.datetime.now(pytz.timezone('US/Eastern')).isoformat()
    document["index"] = ""
    document["version"] = 1 #Version 0 didn't include superK fields
    document["pass"] = 0

    # Save doc to the db
    newFileName = '{}.json'.format(args.run_name)
    with open(newFileName, "w") as f:
        json.dump(document, f, sort_keys=True, indent=4, separators=(',', ': '))

    request = raw_input("Doc {} created. Would you like to push it to database? [Y/n] : ".format(newFileName))
    if request == "Y" or request == "y" or request == "":
        # Get a reference to the smelliedb
        db = database.SmellieDatabase(args.server, args.database)

        # Does document already exist with this name? 
        runDocsOnDB = db.get_docs_from_view("_design/smellieMainQuery/_view/pullEllieRunHeaders")
        for doc in runDocsOnDB:
            if doc["run_info"]["run_name"] == document["run_info"]["run_name"]:
                request = raw_input("There is already a smellie run description called {}. Would you like to updated it? [Y/n] : ".format(doc["run_info"]["run_name"]))
                if request == "Y" or request == "y" or request == "":
                    db.update_doc(doc["_id"], document)
                    print "Document {} sucessfully updated on {}/_utils/database.html?{}".format((doc["_id"], args.server, args.database))
                else:
                    print "Exiting..."
                    sys.exit()

        # If no existing docs, save this one
        _id, _rev = db.save(document)
        print "Run document {} saved to {}/_utils/database.html?{}, search for it with doc_id = {}".format(document["run_info"]["run_name"], args.server, args.database, _id)
        sys.exit()

    print "File {} created, but not pushed".format(newFileName)
