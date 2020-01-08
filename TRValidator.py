# given session Parent Path, XML schema Path and Report directory , do analysis and send Email to configured recipients about the Testrail mapping status

import os
from fnmatch import fnmatch
import Utils
import xml.dom.minidom
import json
import sys



def get_files_to_be_validated(root , pattern = "*.xml"):
    result = []    
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch(name, pattern):
                result.append(os.path.join(path, name))             
    return result


def filter_only_session_files(path_list):
    session_files=[]
    validator = Utils.Validator()
    for items in path_list:
        if(validator.validate(items)):
            session_files.append(items)
    return session_files

def get_unmapped_items_per_session(path_to_session_file):
    result=[]
    doc = xml.dom.minidom.parse(path_to_session_file)
    TestSuites = doc.getElementsByTagName("TestSuite")
    for Suites in TestSuites:
        if(bool(Suites.getAttribute('Enabled'))):
            TestCases = Suites.getElementsByTagName("TestCase")
            for Cases in TestCases:
                Test_rail_id = Cases.getAttribute("TestRailID")
                enabled = Cases.getAttribute("Enabled")
                name = Cases.getAttribute("Name")
                result.append({
                    "TestSuite":Suites.getAttribute("Name"),
                    "TestCase":name,
                    "Enabled":enabled,
                    "TestRailId":Test_rail_id
                })
    return result

if __name__ == "__main__":

    
#####Parse Arguments
    root =None
    result_csv_name = None
    report_all = False
    arguments = sys.argv

    for i in range(1,arguments.__len__()):
        if(arguments[i]=='-session'):
            root = arguments[i+1]
        if(arguments[i]== '-output'):
            result_csv_name = arguments[i+1]
        if(arguments[i]== '-report_all'):
            report_all = arguments[i+1]
            if(report_all.lower()=='true'):
                report_all = True
            else:
                report_all = False
######################

    config = json.load(open('config.json'))
    send_mail = config["send_Email"]
    final_result = {}
    files_to_be_validated = get_files_to_be_validated(root)

    filtered_session_files = filter_only_session_files(files_to_be_validated)

    for files in filtered_session_files:
        try:
            file_result = get_unmapped_items_per_session(files)
        except:
            print("{0} files is malformed and will not be considered for validation!".format(files))
        final_result[files]= file_result
    
    data_frame = Utils.save_as_csv(final_result , result_csv_name , report_all)
    if(data_frame.__len__()>0 and send_mail):
        msg = Utils.create_email_msg(config['email_recipients'], result_csv_name , "Missing TestRail Ids for {0} : {1}".format(config['division'], config['POR']))
        Utils.sendmail_msg(msg)
        sys.exit(1)
    sys.exit(0)