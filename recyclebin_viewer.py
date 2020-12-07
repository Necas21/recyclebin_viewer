import os
from winreg import *
import re
import binascii
from datetime import datetime

# Checks for which directory the recycling bin is in
def get_recyclebin():
    dirs=["C:\\Recycler\\", "C:\\Recycled\\", "C:\\$Recycle.Bin\\"]

    for dir in dirs:
        if os.path.isdir(dir):
            return dir

    return None


# Converts a users SID to their username
def sid_to_user(sid):
    try:
        key = OpenKey(HKEY_LOCAL_MACHINE, f"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{sid}")
        value, type = QueryValueEx(key, "ProfileImagePath")
        user = value.split("\\")[-1]
        return user

    except:
        return sid


# Converts Windows filetime to Unix time
def filetime_to_unix(filetime):
    EPOCH_AS_FILETIME = 116444736000000000
    HUNDRED_NS = 10000000
    epoch_time = (filetime - EPOCH_AS_FILETIME)/HUNDRED_NS
    dt = datetime.fromtimestamp(epoch_time)
    dt = dt.strftime("%d/%m/%Y %H:%M:%S")
    return dt


# Takes hex metadata and returns the fields. Metadata is stored in little endian format so will need to reverse the hex.
def get_metadata(hex):
    # Splitting the data into bytes
    hex = [hex[i:i+2] for i in range(0,len(hex), 2)]
    # The header makes up the first 8 bytes of metadata
    header = hex[0:8]
    header.reverse()
    header = "".join(header)
    header = int(header, 16)
    print(f"[+] File Header: {header}")
    # File size makes up the next 8 bytes
    file_size = hex[8:16]
    file_size.reverse()
    file_size = "".join(file_size)
    file_size = int(file_size, 16)
    print(f"[+] File Size: {file_size}")
    # Date/time makes up the next 8 bytes
    time = hex[16:24]
    time.reverse()
    time = "".join(time)
    time = int(time, 16)
    time = filetime_to_unix(time)
    print(f"[+] Time of Deletion: {time}")
    # File name and path
    file_name = hex[28:]
    file_name = "".join(file_name)
    bytes_object = bytes.fromhex(file_name)
    file_path = bytes_object.decode("ASCII")
    print(f"[+] File Path: {file_path}")


# Takes the recyclying bin path as an argument a returns which files have been deleted by which users
def get_recycled(recycle_dir):
    dir_list = os.listdir(recycle_dir)
    for sid in dir_list:
        user = sid_to_user(sid)
        path = recycle_dir + sid
        deleted_files = os.listdir(path)
        print(f"[*] Listing deleted files for user: {user}")
        for file in deleted_files:
            print(f"[+] Found file: {file}")
            if re.search("^\$I", file):
                f = open(f"{path}\\{file}", "rb")
                file_contents = binascii.hexlify(f.read())
                file_contents = file_contents.decode("ascii")
                f.close()
                get_metadata(file_contents)


def main():
    recycle_dir = get_recyclebin()
    get_recycled(recycle_dir)


if __name__ == "__main__":
    main()

