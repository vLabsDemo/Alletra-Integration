import configparser
import base64
import time
import Alletra
import os


def main():

    # main
    Alletra_dict = {}
    SN_Mid_dict = {}
    file_path = os.getcwd()
    os.chdir(file_path)
    Config = configparser.ConfigParser()
    Config.read("Alletra_SN_Connect.ini")
    Mid_servers = Config.sections()
    Mid_server_len = len(Mid_servers)
    for x in Mid_servers:
        Midserver = x
        MID_Primary_IP = Config[Midserver]['MID_Primary_IP']
        MID_Seconday_IP = Config[Midserver]['MID_Secondary_IP']
        SN_MIDPort = Config[Midserver]['MIDPort']
        SN_user = Config[Midserver]['SN_user']
        SN_Password = Config[Midserver]['SN_Password']
        Alletra_Primary_IP = Config[Midserver]['Alletra_Primary_IP']
        Alletra_Seconday_IP = Config[Midserver]['Alletra_Secondary_IP']
        Alletra_user = Config[Midserver]['Alletra_user']
        Alletra_Password = Config[Midserver]['Alletra_Password']
        Alletra_PortNo = Config[Midserver]['Alletra_Port']
        Alletra_Protocol = Config[Midserver]['Alletra_Protocol']

    sn_passv = SN_Password.encode()
    Alletra_passv = Alletra_Password.encode()
    sn_pass = base64.b64decode(sn_passv)
    sn_pass = sn_pass.decode("utf-8")
    Alletra_pass = base64.b64decode(Alletra_passv)
    Alletra_pass = Alletra_pass.decode("utf-8")

    if Alletra_Seconday_IP:
        Alletra_dict['Primary_IP'] = Alletra_Primary_IP
        Alletra_dict['Seconday_IP'] = Alletra_Seconday_IP
    else:
        Alletra_dict['Primary_IP'] = Alletra_Primary_IP

    if MID_Seconday_IP:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP
        SN_Mid_dict['Seconday_IP'] = MID_Seconday_IP
    else:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP
    operatorname = Alletra_user
    # Interval for checking of alert value
    epoch = int(round(time.time()))
    # print("Epoch", epoch)
    millis = epoch - 360
    print("Run time", millis)
    Alletra.getalarm(Alletra_user, Alletra_pass, operatorname, str(millis), Alletra_Protocol, Alletra_dict, Alletra_PortNo, SN_user, sn_pass, SN_Mid_dict, SN_MIDPort)


if __name__ == "__main__":
    main()
