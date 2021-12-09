import requests
from requests.auth import HTTPDigestAuth
import urllib3
import sys
import json
import datetime
import os
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def post(base_url, headers, payload):
    try:
        response = requests.request("POST" ,base_url, headers=headers, data=payload, verify=False, timeout=15)
        if response.ok and response.status_code == 201:
            getSessionJ = response.json()
            return getSessionJ
        else:
            return "failed", response.status_code, response.cookies
    except Exception as e:
        return "failed", e, "postrequest"

def get(base_url, headers):
    try:
        response = requests.request("GET", base_url, headers=headers, verify=False)
        if response.ok and response.status_code == 200:
            getEventJ = response.json()
            return getEventJ
        else:
            return "failed", response.status_code, response.cookies
    except Exception as e:
        return "failed", e, "getrequest"

def rename_files():
    file_path = os.getcwd()
    Files = os.listdir(file_path)
    files_list = []
    all_values = 0
    all_yes = False

    for file in Files:
        if file.endswith(".txt"):
            files_list.append(file)
    files_exist = len(files_list)
    if files_exist < 7:
        for i in reversed(files_list):
            file_val = files_exist
            file_name = "Alletra_servicenow." + str(file_val) + ".txt"
            os.rename(i, file_name)
            files_exist = files_exist - 1
    if files_exist == 7:
        files_exist = files_exist - 1
        file_val = files_exist
        file_name = "Alletra_servicenow.6.txt"
        os.remove(file_name)
        files_list1 = []
        once = 0
        Files1 = os.listdir(file_path)
        files_exist1 = 0
        for file1 in Files1:
            if file1.endswith(".txt"):
                files_list1.append(file1)
            files_exist1 = len(files_list1)
        for j in reversed(files_list1):
            if once == 0:
                file_val1 = files_exist1
                file_name1 = "Alletra_servicenow." + str(file_val1) + ".txt"
                os.rename(j, file_name1)
                once = 1
            else:
                file_val1 = files_exist1 - 1
                file_name1 = "Alletra_servicenow." + str(file_val1) + ".txt"
                os.rename(j, file_name1)
                files_exist1 = file_val1


def logger(file_update):
    # writing to the file
    date_time = datetime.datetime.now()
    date_ISO = date_time.isoformat()
    file_info = os.stat("Alletra_servicenow.0.txt")
    file_size = file_info.st_size
    file_mb = file_size / (1024 * 1024)
    if file_mb < 10:
        with open("Alletra_servicenow.0.txt", "a+") as fileobj:
            file_update = "***********************" + str(date_ISO) + "***********************" + "\n" + file_update
            fileobj.write(file_update)
    else:
        rename_files()
        with open("Alletra_servicenow.0.txt", "a+") as fileobj:
            file_update = "\n***********************" + str(
                date_ISO) + "***********************" + "\n" + file_update
            fileobj.write(file_update)

def CallSN(user, Password, midip, midport, headers, devicename, eventtype, description, resource, severity):
    severity = str(severity)
    urli = "http://" + midip + ":" + midport + "/api/mid/em/inbound_event?Transform=jsonv2"
    payload = {}
    payload['source'] = "Alletra"
    payload['description'] = description
    payload['type'] = eventtype
    payload['node'] = devicename
    payload['severity'] = severity
    payload['resource'] = resource
    JSON_data = json.dumps(payload)
    try:
        response = requests.post(urli, auth=(user, Password), timeout=10, headers=headers, data="{\"records\":[" + JSON_data + "]}")
        if response.status_code == 200:
            result = response.status_code
            return result, "success"
        else:
            result = response.status_code
            return result, "failed"
    except:
        response = "Exception Occured in event Processing"
        return response, "failed"

def mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, devicename, eventtype, description, resource, severity, file_updates):
    mid_exit_flag = 0
    mid_server = 0
    for each_mid_ip in SN_MIDIP:
        get_mid_status = CallSN(SN_user, sn_pass, SN_MIDIP[each_mid_ip], SN_MIDPort, header, devicename, eventtype, description, resource, severity)
        if "failed" not in get_mid_status:
            mid_exit_flag = 1
            mid_server = SN_MIDIP[each_mid_ip]
            file_updates = file_updates + "************************************************************************\n"
            file_updates = file_updates + "Succesfully Established connection to MID Server{0} : {1}\n".format(each_mid_ip, SN_MIDIP[each_mid_ip])
            file_updates = file_updates + "************************************************************************\n"
            File_up = "exit code " + str(get_mid_status[0]) + "\n" + "Event - Node " + devicename
            file_updates = file_updates + File_up + "\n"
            file_updates = file_updates + "************************************************************************\n"
            break
        elif "failed" in get_mid_status:
            file_updates = file_updates + "************************************************************************\n"
            file_updates = file_updates + "failed to establish connection to MID Server{0} : {1}\n".format(each_mid_ip, SN_MIDIP[each_mid_ip])
            file_updates = file_updates + "Error: " + str(get_mid_status[0])
            file_updates = file_updates + "\n************************************************************************\n"
    if not mid_exit_flag:
        logger(file_updates)
        sys.exit(1)
    else:
        return mid_server, file_updates