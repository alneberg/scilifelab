#!/usr/bin/env python

desc = """A script to compare extraction output from the lims, given two different
executables of project_summary_upload_LIMS.py.

Given the full path of independent executables (such as within two conda environments),
the comparison is not limited to the actual script but also its dependencies. 

The comparison is based on the objects created to build documents in the projects database 
on StatusDB. A recursive function compares all values in the objects and any differing 
values or missing keys are logged in a validation log file.

Maya Brandi, Science for Life Laboratory, Stockholm, Sweden.
Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden.

*****Recomended validation procedure:*****

Testing the script:

Test that the script is caching differences by changing something on the 
stage server, eg. the value of the sample udf "status_(manual)". for some 
project J.Doe_00_00. Then run the script with the -p flagg:

validation_project_upload_script.py -p J.Doe_00_00 <script1_path> 
       -name1 <script_name1> <script2_path> -name2 <script_name2>

This should give the output:

<script_name1> and <script_name2> are differing for proj J.Doe_00_00: True
Key status_(manual) differing: <script_name2> gives: Aborted. <script_name1> gives In Progress.

Comparing all projects
Using the -a flag instead of -p will run the comparison for all projects. 
This could take quite some time.

If you don't find anything when grepping for True in the log file, no differences 
are found for any projects. If you get output when grepping for True, there are 
differences. Then read the log file to find what is differing. 

"""
import sys
import os
import codecs
from argparse import ArgumentParser, RawTextHelpFormatter
from scilifelab.db.statusDB_utils import *
from helpers import *
from pprint import pprint
from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD
#import objectsDB as DB
from datetime import date
import scilifelab.log
lims = Lims(BASEURI, USERNAME, PASSWORD)

def comp_obj(stage, prod):
    """compares the two dictionaries obj and dbobj"""
    LOG.info('project %s is being handeled' % stage['project_name'])
    diff = recursive_comp(stage, prod)
    LOG.info('tools and tools-dev are differing for proj %s: %s' % ( stage['project_name'],diff))

def recursive_comp(stage, prod):
    diff = False
    keys = list(set(stage.keys() + prod.keys()))
    for key in keys:
        if not (stage.has_key(key)):
            LOG.info('Key %s missing in tools to db object ' % key)
            diff = True
        elif not  prod.has_key(key):
            LOG.info('Key %s missing in tools-dev to db object ' % key)
            diff = True
        else:
            prod_val = prod[key]
            stage_val = stage[key]
            if (prod_val != stage_val):
                diff = True
                if (type(prod_val) is dict) and (type(stage_val) is dict):
                    diff = diff and recursive_comp(stage_val, prod_val)
                else:
                    LOG.info('Key %s differing: tools gives: %s. tools-dev gives %s. ' %( key,prod_val,stage_val))
    return diff

def  main(proj_name, all_projects, conf_tools_dev):
    first_of_july = '2013-06-30'
    today = date.today()
    couch_tools = load_couch_server(os.path.join(os.environ['HOME'],'opt/config/post_process.yaml'))
    couch_tools_dev = load_couch_server(conf_tools_dev)
    proj_db_tools = couch_tools['projects']
    proj_db_tools_dev = couch_tools_dev['projects']
    if all_projects:
        for key in proj_db_tools:
            proj_tools = proj_db_tools.get(key)
            proj_tools_dev = proj_db_tools_dev.get(key)
            proj_name = proj_tools['project_name']
            try:
                if not proj_tools_dev:
                    LOG.warning("""Found no projects on tools-dev with name %s""" % proj_name)
                else:
                    comp_obj(proj_tools, proj_tools_dev)
            except:
                LOG.info('Failed comparing stage and prod for proj %s' % proj_name)    
    elif proj_name is not None:
        key = find_proj_from_view(proj_db_tools, proj_name)
        proj_tools = proj_db_tools.get(key)
        proj_tools_dev = proj_db_tools_dev.get(key)
        if (not proj_tools) | (not proj_tools_dev):
            LOG.warning("Found no project named %s" %(proj_name))
        else:
            comp_obj(proj_tools, proj_tools_dev)

if __name__ == '__main__':
    parser = ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-p", "--project", dest="project_name", default=None,
                        help = "eg: M.Uhlen_13_01. Dont use with -a flagg.")

    parser.add_argument("-a", "--all_projects", action="store_true",
                      help = "Check all projects on couchDB. Don't use with -p flag.")

    parser.add_argument("-c", "--conf", dest="conf", 
                      default=os.path.join(os.environ['HOME'],
                                           'opt/scilifelab/scilifelab/lims_utils/post_process.yaml'),         
                      help = ("Config file for tools-dev.  "
                              "Default: ~/opt/scilifelab/scilifelab/lims_utils/post_process.yaml"))

    args = parser.parse_args()

    LOG = scilifelab.log.file_logger('LOG', args.conf, 'validate_LIMS_upgrade.log', 'log_dir_tools')
    main(args.project_name, args.all_projects, args.conf)

