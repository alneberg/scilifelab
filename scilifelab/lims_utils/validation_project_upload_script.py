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

Run the validation script for some representative projects of different characteristics:

validation_project_upload_script.py -p J.Doe_00_00 J.Doe_00_01 J.Doe_00_02 
    --script_name1 <script_name1> --script_name2 <script_name2>
    --script1 <script_path1> --script2 <script_path2>

The script will create two output files with names 'PSUL_<proj_name>_<script_name>.out 
and one output file with name 'PSUL_<proj_name>_diff.out' for each project name 
where a diff was found.

Comparing all projects
Using the -a flag instead of -p will run the comparison for all projects. 
This could take quite some time.
"""
import os
from argparse import ArgumentParser, RawTextHelpFormatter
import subprocess

def  main(proj_names, all_projects, script1, script2, name1, name2):
    tmp_output_f1 = 'PSUL_{0}.tmp'.format(name1)
    tmp_output_f2 = 'PSUL_{0}.tmp'.format(name2)

    if all_projects:
        raise NotImplementedError
    elif proj_names is not None:
        diff_projs = []
        for proj_name in proj_names:
            subprocess.call([script1, "-p", proj_name,
                    "--no_upload", "--output_f", tmp_output_f1])
            subprocess.call([script2, "-p", proj_name,
                    "--no_upload", "--output_f", tmp_output_f2])

            output, error = subprocess.Popen(['diff', tmp_output_f1, tmp_output_f2], 
                        stdout=subprocess.PIPE).communicate()
            if output:
                output_f1 = 'PSUL_{0}_{1}.out'.format(proj_name, name1)
                output_f2 = 'PSUL_{0}_{1}.out'.format(proj_name, name2)
                    
                # Save output if diff was found
                shutil.copyfile(tmp_output_f1, output_f1)
                shutil.copyfile(tmp_output_f2, output_f2)
                
                diff_output = 'PSUL_{0}_diff.out'.format(proj_name)
                with open(diff_output, 'w') as dfh:
                    dfh.write(output)
                
                diff_projs.append(proj_name)
        if diff_projs:
            print 'Diff found for {0}.'.format(', '.join(diff_projs))

if __name__ == '__main__':
    parser = ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-p", "--projects", nargs='*', 
            help = ("Projects to use for comparison eg: J.Doe_13_01, J.Doe_13_02. "
                   "Don't use together with -a flag."))

    parser.add_argument("-a", "--all_projects", action="store_true",
            help = "Check all projects on couchDB. Don't use with -p flag.")

    parser.add_argument("--script1", required=True, 
            help = ("First path to executable for script. Preferably located in an "
                    "independent conda environment."))
    parser.add_argument("--script1_name",
            help = ("Name used for script1 in log file and output"))

    parser.add_argument("--script2", required=True,
            help = ("Second path to executable for script. Preferably located in an "
                    "independent conda environment."))
    parser.add_argument("--script2_name",
            help = ("Name used for script2 in log file and output"))

    args = parser.parse_args()

    main(args.projects, args.all_projects, args.script1, args.script2, args.script1_name, args.script2_name)

