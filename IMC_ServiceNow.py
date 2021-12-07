import configparser
import base64
import time
import IMC
import os


def main():

    # main
    IMC_dict = {}
    SN_Mid_dict = {}
    file_path = os.getcwd()
    os.chdir(file_path)
    Config = configparser.ConfigParser()
    Config.read("IMC_SN_Connect.ini")
    Mid_servers = Config.sections()
    Mid_server_len = len(Mid_servers)
    for x in Mid_servers:
        Midserver = x
        MID_Primary_IP = Config[Midserver]['MID_Primary_IP']
        MID_Seconday_IP = Config[Midserver]['MID_Secondary_IP']
        SN_MIDPort = Config[Midserver]['MIDPort']
        SN_user = Config[Midserver]['SN_user']
        SN_Password = Config[Midserver]['SN_Password']
        IMC_Primary_IP = Config[Midserver]['IMC_Primary_IP']
        IMC_Seconday_IP = Config[Midserver]['IMC_Secondary_IP']
        IMC_user = Config[Midserver]['IMC_user']
        IMC_Password = Config[Midserver]['IMC_Password']
        IMC_PortNo = Config[Midserver]['IMC_Port']
        IMC_Protocol = Config[Midserver]['IMC_Protocol']

    sn_passv = SN_Password.encode()
    IMC_passv = IMC_Password.encode()
    sn_pass = base64.b64decode(sn_passv)
    sn_pass = sn_pass.decode("utf-8")
    IMC_pass = base64.b64decode(IMC_passv)
    IMC_pass = IMC_pass.decode("utf-8")

    if IMC_Seconday_IP:
        IMC_dict['Primary_IP'] = IMC_Primary_IP
        IMC_dict['Seconday_IP'] = IMC_Seconday_IP
    else:
        IMC_dict['Primary_IP'] = IMC_Primary_IP

    if MID_Seconday_IP:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP
        SN_Mid_dict['Seconday_IP'] = MID_Seconday_IP
    else:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP
    operatorname = IMC_user
    # Interval for checking of alert value
    epoch = int(round(time.time()))
    # print("Epoch", epoch)
    millis = epoch - 360
    print("Run time", millis)
    IMC.getalarm(IMC_user, IMC_pass, operatorname, str(millis), IMC_Protocol, IMC_dict, IMC_PortNo, SN_user, sn_pass, SN_Mid_dict, SN_MIDPort)


if __name__ == "__main__":
    main()
