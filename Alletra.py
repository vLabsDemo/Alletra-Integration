import requests
from requests.auth import HTTPDigestAuth
import urllib3
import sys
import json
import datetime
import os
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get(base_url, session, headers, payload, cookies='no'):
    try:
        response = session.get(base_url, headers=headers, data=payload, verify=False, timeout=10)
        if response.ok:
            if cookies != 'no':
                get_cookies = dict(response.cookies)['JSESSIONID']
                cookies_str = 'JSESSIONID=' + str(get_cookies)
                return cookies_str
            else:
                return response.json()
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
            file_name = "IMC_servcienow." + str(file_val) + ".txt"
            os.rename(i, file_name)
            files_exist = files_exist - 1
    if files_exist == 7:
        files_exist = files_exist - 1
        file_val = files_exist
        file_name = "IMC_servcienow.6.txt"
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
                file_name1 = "IMC_servcienow." + str(file_val1) + ".txt"
                os.rename(j, file_name1)
                once = 1
            else:
                file_val1 = files_exist1 - 1
                file_name1 = "IMC_servcienow." + str(file_val1) + ".txt"
                os.rename(j, file_name1)
                files_exist1 = file_val1


def logger(file_update):
    # writing to the file
    date_time = datetime.datetime.now()
    date_ISO = date_time.isoformat()
    file_info = os.stat("IMC_servcienow.0.txt")
    file_size = file_info.st_size
    file_mb = file_size / (1024 * 1024)
    if file_mb < 10:
        with open("IMC_servcienow.0.txt", "a+") as fileobj:
            file_update = "***********************" + str(date_ISO) + "***********************" + "\n" + file_update
            fileobj.write(file_update)
    else:
        rename_files()
        with open("IMC_servcienow.0.txt", "a+") as fileobj:
            file_update = "\n***********************" + str(
                date_ISO) + "***********************" + "\n" + file_update
            fileobj.write(file_update)


def mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, source, devicename, eventtype, resource, severity, description, file_updates):
    mid_exit_flag = 0
    mid_server = 0
    for each_mid_ip in SN_MIDIP:
        get_mid_status = CallSN(SN_user, sn_pass, SN_MIDIP[each_mid_ip], SN_MIDPort, header, source, devicename, eventtype, resource, severity, description)
        if "failed" not in get_mid_status:
            mid_exit_flag = 1
            mid_server = SN_MIDIP[each_mid_ip]
            file_updates = file_updates + "************************************************************************\n"
            file_updates = file_updates + "Succesfully Established connection to MID Server{0} : {1}\n".format(each_mid_ip, SN_MIDIP[each_mid_ip])
            file_updates = file_updates + "************************************************************************\n"
            File_up = "exit code " + str(get_mid_status[0]) + " for event " + eventtype + " " + description
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


def CallSN(user, Password, midip, midport, headers, source, devicename, eventtype, resource, severity, description):
    severity = str(severity)
    urli = "http://" + midip + ":" + midport + "/api/mid/em/inbound_event?Transform=jsonv2"
    payload = {}
    payload['source'] = "IMC"
    payload['description'] = description
    payload['type'] = eventtype
    payload['node'] = devicename
    payload['severity'] = severity
    payload['resource'] = resource
    JSON_data = json.dumps(payload)

    try:
        time.sleep(2)
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


def getalarm(username, password, operator_name, qtime, imc_protocol, imc_ip, imc_port, SN_user, sn_pass, SN_MIDIP, SN_MIDPort):
    imc_exit_flag = 0
    newlist = []
    mid_select = 1
    with requests.session() as getsession:
        file_updates = ""
        getsession.auth = HTTPDigestAuth(username, password)
        payload = {}
        header = {'Content-Type': 'application/json'}
        for each_imc_ip in imc_ip:
            url = imc_protocol + "://" + imc_ip[each_imc_ip] + ":" + imc_port + "/imcrs"
            get_cookie = get(url, getsession, header, payload, 'yes')
            if "failed" not in get_cookie:
                imc_exit_flag += 1
                file_updates = file_updates + "************************************************************************\n"
                file_updates = file_updates + "Succesfully Established connection to IMC {0} : {1}\n".format(
                    each_imc_ip, imc_ip[each_imc_ip])
                break
            elif "failed" in get_cookie:
                file_updates = file_updates + "************************************************************************\n"
                file_updates = file_updates + "failed to establish connection to IMC {0} : {1}\n".format(each_imc_ip,
                                                                                                         imc_ip[
                                                                                                             each_imc_ip])
                file_updates = file_updates + "failed to getCookies: " + str(get_cookie[1]) + " " + str(get_cookie[2])
                file_updates = file_updates + "\n************************************************************************\n"
        if not imc_exit_flag:
            logger(file_updates)
            sys.exit(1)
        header_alarm = {'Content-Type': 'application/json', 'Cookie': get_cookie, 'Accept': 'application/json'}
        base_url = url + "/fault/alarm?operatorName=" + operator_name + "&startAlarmTime=" + qtime + "&desc=false&size=200"
        # base_url = url + "/fault/alarm?operatorName=" + operator_name + "&desc=true&size=200"
        # get the alarm
        get_alarm = get(base_url, getsession, header_alarm, payload)
        if "failed" in get_alarm:
            file_updates = file_updates + "failed to get Events: " + str(get_alarm[1]) + " " + str(get_alarm[2])
            file_updates = file_updates + "\n************************************************************************\n"
            logger(file_updates)
            sys.exit(2)
        if get_alarm:
            alarmlengthlist = get_alarm['alarm']
            alarmlist = get_alarm['alarm']
            if "dict" in str(type(alarmlist)):
                alarmlengthlist=[]
                alarmlengthlist.append(alarmlist)
                file_updates = file_updates + "*********************************************************************\n"
                file_updates = file_updates + "Alarm Time: " + alarmlengthlist[0]["faultTimeDesc"] + "\n"
                file_updates = file_updates + "ID: " + alarmlengthlist[0]["id"] + "\n"
                file_updates = file_updates + "deviceip: " + alarmlengthlist[0]["deviceIp"] + "\n"
                file_updates = file_updates + "devicename: " + alarmlengthlist[0]["deviceName"] + "\n"
                alarmdescraw = alarmlengthlist[0]["alarmDesc"]
                alarmdesc = alarmdescraw.replace("\"", "")
                file_updates = file_updates + "alarmdesc: " + alarmdesc + "\n"
                file_updates = file_updates + "alarmcategorydesc: " + alarmlengthlist[0]["alarmCategoryDesc"] + "\n"
                file_updates = file_updates + "originaltype: " + alarmlengthlist[0]["originalTypeDesc"] + "\n"
                alarmlevel = alarmlengthlist[0]["alarmLevel"]
                if alarmlevel == "5":
                    alarmlevel = "0"
                file_updates = file_updates + "alarmlevel: " + alarmlevel + "\n"
                resourcestr = alarmlengthlist[0]['paras']
                try:
                    for i in resourcestr.split(";"):
                        newlist.append(tuple(i.split("=")))
                    resourceDict = dict(newlist)
                    resource = resourceDict['Interface Description']
                except:
                    resource = ""
                file_updates = file_updates + "resource: " + resource + "\n"
                file_updates = file_updates + "*********************************************************************\n"
                # mid server selection
                get_mid = mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, alarmlengthlist[0]["originalTypeDesc"], alarmlengthlist[0]["deviceName"], alarmlengthlist[0]["alarmCategoryDesc"], resource, alarmlevel, alarmdesc, file_updates)
                file_updates = get_mid[1]
                file_updates = file_updates + "************************************************************************\n"
                logger(file_updates)
            elif len(alarmlengthlist) > 1:
                for each in range(len(alarmlengthlist)):
                    file_updates = file_updates + "************************************************************************\n"
                    file_updates = file_updates + "RunTime: " + qtime + "\n"
                    file_updates = file_updates + "Alarm Time: " + alarmlengthlist[each]["faultTimeDesc"] + "\n"
                    file_updates = file_updates + "ID: " + alarmlengthlist[each]["id"] + "\n"
                    file_updates = file_updates + "deviceip: " + alarmlengthlist[each]["deviceIp"] + "\n"
                    file_updates = file_updates + "devicename: " + alarmlengthlist[each]["deviceName"] + "\n"
                    alarmdescraw = alarmlengthlist[each]["alarmDesc"]
                    alarmdesc = alarmdescraw.replace("\"", "")
                    file_updates = file_updates + "alarmdesc: " + alarmdesc + "\n"
                    file_updates = file_updates + "alarmcategorydesc: " + alarmlengthlist[each][
                        "alarmCategoryDesc"] + "\n"
                    file_updates = file_updates + "originaltype: " + alarmlengthlist[each]["originalTypeDesc"] + "\n"
                    alarmlevel = alarmlengthlist[each]["alarmLevel"]
                    if alarmlevel == "5":
                        alarmlevel = "0"
                    file_updates = file_updates + "alarmlevel: " + alarmlevel + "\n"
                    resourcestr = alarmlengthlist[each]['paras']
                    try:
                        for i in resourcestr.split(";"):
                            newlist.append(tuple(i.split("=")))
                        resourceDict = dict(newlist)
                        resource = resourceDict['Interface Description']
                    except:
                        resource = ""
                    file_updates = file_updates + "resource: " + resource + "\n"
                    file_updates = file_updates + "************************************************************************\n"
                    # mid server selection
                    if mid_select:
                        get_mid = mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, alarmlengthlist[0]["originalTypeDesc"], alarmlengthlist[0]["deviceName"], alarmlengthlist[0]["alarmCategoryDesc"], resource, alarmlevel, alarmdesc, file_updates)
                        mid_select = 0
                        file_updates = get_mid[1]
                    else:
                        sncall = CallSN(SN_user, sn_pass, get_mid[0], SN_MIDPort, header, alarmlengthlist[each]["originalTypeDesc"], alarmlengthlist[each]["deviceName"], alarmlengthlist[each]["alarmCategoryDesc"], resource, alarmlevel, alarmdesc)
                        File_up = "exit code " + str(sncall[0]) + " for event " + alarmlengthlist[each]["alarmCategoryDesc"] + " " + alarmdesc
                        file_updates =  file_updates + File_up + "\n"
                        file_updates = file_updates + "************************************************************************\n"
                logger(file_updates)

        else:
            file_updates = file_updates + "RunTime: " + qtime + "\n"
            file_updates = file_updates + "No events in current check\nSending Clear Event to ServiceNow\n"
            # mid server selection
            snseverity = 0
            resource = "system"
            label = "10.0.135.37"
            eventtype = "script_running"
            description = "Monitor Event"
            source = "IMC"
            if mid_select:
                get_mid = mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, source, label, eventtype,
                                        resource, snseverity, description, file_updates)
                mid_select = 0
                file_updates = get_mid[1]
                # print("mid", get_mid[0])
            file_updates = file_updates + "************************************************************************\n"
            logger(file_updates)
