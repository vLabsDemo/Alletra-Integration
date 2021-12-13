import requests
from requests.auth import HTTPDigestAuth
import urllib3
import base64
import sys
import json
import datetime
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def post(base_url, headers, payload):
    try:
        response = requests.request("POST" ,base_url, headers=headers, data=payload, verify=False, timeout=15)
        if response.ok and response.status_code == 201:
            getSessionJ = response.json()
            return getSessionJ
        else:
            return "failed", response.status_code, response.json()
    except Exception as e:
        return "failed", e, "postrequest"

def get(base_url, headers):
    try:
        response = requests.request("GET", base_url, headers=headers, verify=False)
        if response.ok and response.status_code == 200:
            getEventJ = response.json()
            return getEventJ
        elif response.status_code == 403:
            return "InValid Session Key", response.status_code, response.json() 
        else:
            return "failed", response.status_code, response.json()
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

def CallSN(user, Password, midip, midport, headers, devicename, eventtype, description, resource, severity, additional_info):
    #severity = str(severity)
    urli = "http://" + midip + ":" + midport + "/api/mid/em/inbound_event?Transform=jsonv2"
    payload = {}
    payload['source'] = "Alletra"
    payload['description'] = description
    payload['type'] = eventtype
    payload['node'] = devicename
    payload['severity'] = severity
    payload['resource'] = resource
    payload['additional_info'] = additional_info
    JSON_data = json.dumps(payload)
    try:
        time.sleep(1)
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

def mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, header, devicename, eventtype, description, resource, severity, file_updates, additional_info):
    mid_exit_flag = 0
    mid_server = 0
    for each_mid_ip in SN_MIDIP:
        get_mid_status = CallSN(SN_user, sn_pass, SN_MIDIP[each_mid_ip], SN_MIDPort, header, devicename, eventtype, description, resource, severity, additional_info)
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

def getalarm(username, password, date_time, alletra_protocol, alletra_ip, Alletra_LookbackTime, SN_user, sn_pass, SN_MIDIP, SN_MIDPort):

    event_flag = 1
    event_payload = {}
    flag = 0
    noOfEvents=0
    mid_select = 1
    with requests.session() as getsession:
        file_updates = ""
        payload = '{"password": "' + password + '", "user": "' + username + '", "sessionType": 1}'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = "{0}://{1}/api/v1".format(alletra_protocol,alletra_ip)
        alletra_login_url = url + "/credentials"
        # Login and get the cookies
        # get cookie and store it in file for 5 days
        filepath = r'C:\MIDserver\Alletra\getsession.json'
        if os.path.exists(filepath):
            #print("Session File Exists")
            with open(filepath) as fileobj:
                keyValue = json.load(fileobj)
                PreviousExecution = keyValue["ExecutionTime"]
            FileTimeStamp = datetime.datetime.fromtimestamp(float(PreviousExecution))
            curTime = time.time()
            diff = (datetime.datetime.fromtimestamp(curTime) - FileTimeStamp).total_seconds() / 60
            if diff >= 15:
                #print("Executed After 15 Min, New Session Key Required")
                file_updates = file_updates + "Executed After 15 Min, New Session Key Required\n"
                logger(file_updates)
                get_sessions = post(alletra_login_url, headers, payload)
                if "failed" in get_sessions:
                    file_updates = file_updates + "************************************************************************\n"
                    file_updates = file_updates + "Session Found URL: {0}, Head: {1}, Body: {2}\n".format(alletra_login_url,headers,payload)
                    file_updates = file_updates + "failed to establish connection to Alletra : {0}\n".format(alletra_ip)
                    file_updates = file_updates + "failed to Session Key: " + str(get_sessions[1]) + " " + str(get_sessions[2])
                    file_updates = file_updates + "\n************************************************************************\n"
                    logger(file_updates)
                    sys.exit(1)
                get_session = get_sessions["key"]
                message_bytes = get_session.encode('ascii')
                base64_bytes = base64.b64encode(message_bytes)
                base64_message = base64_bytes.decode('ascii')
                keyValue["SessionKey"] = base64_message
            else:
                file_updates = file_updates + "Executed Within 15 Min, No New Session Key Required\n"
                logger(file_updates)
                base64_message = keyValue["SessionKey"]
                base64_bytes = base64_message.encode('ascii')
                message_bytes = base64.b64decode(base64_bytes)
                get_session = message_bytes.decode('ascii')
            
            with open(filepath, "w") as outfile:
                keyValue["ExecutionTime"] = str(curTime)
                json.dump(keyValue, outfile)
        else:
            file_updates = file_updates + "Session File Doesn't Exists, New Session Key will be Required\n"
            logger(file_updates)
            with open(filepath, 'w') as file_write:
                get_sessions = post(alletra_login_url, headers, payload)
                if "failed" in get_sessions:
                    file_updates = file_updates + "************************************************************************\n"
                    file_updates = file_updates + "Session Not Found URL: {0}, Head: {1}, Body: {2}\n".format(alletra_login_url,headers,payload)
                    file_updates = file_updates + "failed to establish connection to Alletra : {0}\n".format(alletra_ip)
                    file_updates = file_updates + "failed to Session Key: " + str(get_sessions[1]) + " " + str(get_sessions[2])
                    file_updates = file_updates + "\n************************************************************************\n"
                    logger(file_updates)
                    sys.exit(1)
                get_session = get_sessions["key"]
                message_bytes = get_session.encode('ascii')
                base64_bytes = base64.b64encode(message_bytes)
                base64_message = base64_bytes.decode('ascii')
                epochTime = time.time()
                sessionJ = '{"SessionKey":"'+base64_message+'", "ExecutionTime":"'+str(epochTime)+'"}'
                file_write.write(sessionJ)
                file_updates = file_updates + "Session Key and Execution Time Updated\n"
                logger(file_updates)

        # Construct payload
        print(get_session)
        payload_Json = json.dumps(event_payload)
        event_url = url + "/eventlog/minutes:" +str(Alletra_LookbackTime)
        header_alarm = {'Content-Type': 'application/json' , 'x-hp3par-wsapi-sessionkey' : get_session}
        get_alarm = get(event_url, header_alarm)
        if "failed" in get_alarm:
            file_updates = file_updates + "failed to get Events: " + str(get_alarm[1]) + " " + str(get_alarm[2])
            file_updates = file_updates + "\n************************************************************************\n"
            logger(file_updates)
            sys.exit(1)
        elif "InValid Session Key" in get_alarm:
            file_updates = file_updates + "failed to get Events using exising Session Key: " + str(get_alarm[1]) + " " + str(get_alarm[2])
            file_updates = file_updates + "\n************************************************************************\n"
            logger(file_updates)
            sys.exit(1)
        try:
            get_events = get_alarm['members']
            noOfEvents = len(get_alarm['members'])
            if noOfEvents == 0:
                event_flag = 0
        except:
            event_flag = 0
        print("noOfEvents", noOfEvents)
        #print("get_events", get_events)
        if event_flag:
            def severity(psm_severity):
                switcher={
                    1:'1',
                    2:'1',
                    3:'2',
                    4:'3',
                    5:'4',
                }
                return switcher.get(psm_severity,'5')    
            for each_event in get_events:
                desc = each_event['description']
                #componenetData = each_event['component']
                #componenetidData = each_event['componentid']
                #resource = componenetData + ' ' +componenetidData
                resource = each_event['components']
                eventtype = each_event['type']
                
                if "componentName" in each_event:
                    label = each_event['componentName']
                else:
                    label = str(alletra_ip)

                psm_severity = each_event['severity']
                snseverity = severity(psm_severity)
                #additional_info = '{\\"Alletra_Payload\\":[' +str(each_event).replace('\'','\\"')+ ']}'
                #additional_info = '{"Alletra_Payload":[' +str(each_event)+ ']}'
                #additional_info = ""
                additional_info = str(each_event).replace("'","\\'")
                #additional_info = str(json.dumps(each_event)).replace('"','\\"')

                file_updates = file_updates + "************************************************************************\n"
                file_updates = file_updates + "RunTime: " + date_time + "\n"
                file_updates = file_updates + "EventType: " + eventtype + "\n"
                file_updates = file_updates + "Severity: " + str(psm_severity) + "\n"
                file_updates = file_updates + "SNOWSeverity: " + snseverity + "\n"
                file_updates = file_updates + "NodeLabel: " + label + "\n"
                file_updates = file_updates + "Additional Info: " + str(additional_info) + "\n"
                description = "EventType = "+ eventtype + "\nLabel = " + label + "\nResource= " + resource + "\nmessage = " + desc
                file_updates = file_updates + "Description: " + desc + "\n"
                file_updates = file_updates + "Resource: " + resource + "\n"
                file_updates = file_updates + "************************************************************************\n"
                # mid server selection
                if mid_select:
                    get_mid = mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, headers, label, eventtype, description, resource, snseverity, file_updates, additional_info)
                    mid_select = 0
                    file_updates = get_mid[1]
                    #print("mid", get_mid[0])
                else:
                    sncall = CallSN(SN_user, sn_pass, get_mid[0], SN_MIDPort, headers, label, eventtype, description, resource, snseverity, additional_info)
                    File_up = "exit code " + str(sncall[0]) + "\n"
                    file_updates = file_updates + File_up
                    file_updates = file_updates + "Event - Node " + label + "\n"
                    file_updates = file_updates + "************************************************************************\n"
            logger(file_updates)
        else:
            file_updates = file_updates + "RunTime: " + date_time + "\n"
            file_updates = file_updates + "No events in current check\nSending the Clear Event to Service now\n"
            # mid server selection
            snseverity = "0"
            resource = "system"
            label = str(alletra_ip)
            eventtype = "script_running"
            description = "Monitor Event"
            additional_info = ""
            if mid_select:
                get_mid = mid_selection(SN_user, sn_pass, SN_MIDIP, SN_MIDPort, headers, label, eventtype, description, resource, snseverity, file_updates, additional_info)
                mid_select = 0
                file_updates = get_mid[1]
                # print("mid", get_mid[0])
            logger(file_updates)