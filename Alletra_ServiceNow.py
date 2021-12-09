import configparser
import base64
import datetime
import Alletra
import os


def main():

    # main
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
        Alletra_user = Config[Midserver]['Alletra_user']
        Alletra_Password = Config[Midserver]['Alletra_Password']
        Alletra_Protocol = Config[Midserver]['Alletra_Protocol']

    sn_passv = SN_Password.encode()
    Pensando_passv = Alletra_Password.encode()
    sn_pass = base64.b64decode(sn_passv)
    sn_pass = sn_pass.decode("utf-8")
    Pensando_pass = base64.b64decode(Pensando_passv)
    Pensando_pass = Pensando_pass.decode("utf-8")

    if MID_Seconday_IP:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP
        SN_Mid_dict['Seconday_IP'] = MID_Seconday_IP
    else:
        SN_Mid_dict['Primary_IP'] = MID_Primary_IP

    now = datetime.datetime.now()
    now_minus_7 = now - datetime.timedelta(minutes=7)
    start_time = now_minus_7.isoformat() + "Z"
    #print(start_time)
    Alletra.getalarm(Alletra_user, Pensando_pass, str(start_time), Alletra_Protocol, Alletra_Primary_IP, SN_user, sn_pass, SN_Mid_dict, SN_MIDPort)


if __name__ == "__main__":
    main()