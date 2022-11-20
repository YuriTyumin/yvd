import datetime
import yt_dlp
import time
import os
import shutil
import psutil
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


#
# This part of the def from
# "https://python-programs.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/"
# and "https://www.programcreek.com/python/example/53869/psutil.process_iter"
def findProcessIdByName(processCMDLine):
    # Here is the list of all the PIDs of all the running processes
    # whose name contains the given string processCMDLine
    listOfProcessObjects = []
    #Iterating over the all running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
           # Checking if process name contains the given string processCMDLine.
           if processCMDLine in pinfo['cmdline']:
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
    return listOfProcessObjects


# Downloader video url (yt-dlp)
def downloader(video_url):
    ydl_opts = {
        'ratelimit': 20000,
        'outtmpl': f'{source_path}%(title)s [%(id)s].%(ext)s',
        # 'paths': f'{source_path}',
        'format': 'm4a',
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_url)
    # help(yt_dlp.YoutubeDL)


# File mover
def file_mover(trg):
    url_tail = '[' + trg[-11:] + ']' + '.mp3'
    trg = readed_new[new - 1]
    trg = trg[0:-1]
    tmp_file.write(f'File "{trg} {url_tail}" was downloaded')
    tmp_file.write('\n')
    for folderName, subfolders, filenames in os.walk(source_path):
        if len(filenames) > 0:
            for file in filenames:
                if url_tail in file:
                    shutil.move(f'{source_path}{file}', f'{target_path}')
                    # shutil.move(f'{source_path}{target}.mp3', f'{target_path}')
                    print(f'New file "{file}" was moved to {target_path}')
                    tmp_file.write(f'File "{file}" was moved to {target_path}')
                    tmp_file.write('\n')


# Constants
url = 'Your target youtube channel /videos'
source_path = 'Directory for downloading'
target_path = 'Directory for moving'
q = 3   # Quantity of URL`s in new.txt ant old.txt

# # DOWNLOAD AND CREATE NEW LIST OF VIDEO FROM YOUTUBE CHANNEL
print(f'Current work directory: {os.getcwd()}')
print("Browser is loading...It can takes some minutes")

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
driver.get(url)
time.sleep(300)
print("Browser was downloaded!")
print("This is a last videos:")
lst = driver.find_elements(By.ID, "video-title")
new_file = open('new.txt', 'w') # new list of videos
for i in range(len(lst)):
    print(lst[i].text)
    print(lst[i].get_attribute('href'))
    new_file.write(lst[i].text)
    new_file.write('\n')
    new_file.write(lst[i].get_attribute('href'))
    new_file.write('\n')
    if i == (q - 1):
        break
new_file.close()

# Finding PIDs of all the running instances of process
# which contains '/usr/bin/firefox' in it's CMDLine and kill its
listOfProcessIds = findProcessIdByName('/usr/bin/firefox')
if len(listOfProcessIds) > 0:
    print('Process Exists | PID and other details are')
    for elem in listOfProcessIds:
        processID = elem['pid']
        processName = elem['name']
        processCMDLine = elem['cmdline']
        print(processID, processName, processCMDLine)
        time.sleep(5)
        print(f'Found running "Firefox --marionette" process with pid "{processID}" and it be killed')
        psutil.Process(processID).kill()
else:
    print('No Running Process found with this text')

# MATCHING NEW VIDEO <-> OLD VIDEO
old_file = open('old.txt') # new list of videos
new_file = open('new.txt') # list of videos last time
tmp_file = open('tmp.txt', 'a') # as log file
tmp_file.write(f'{datetime.datetime.now()}')
tmp_file.write('\n')
readed_old = old_file.readlines()
readed_new = new_file.readlines()
# print(len(readed_old))
# print(len(readed_new))
for new in range(1, len(readed_new) + 1, 2):
    target = readed_new[new]
    target = target[0:-1]   # cut '\n' in the end of current string
    # DOWNLOAD & MOVING MISSING VIDEO
    if readed_new[new] not in readed_old:
        print(f'Video "{(readed_new[new - 1])[0:-1]}" is not in old list. This is a new video.')

        trg = readed_new[new - 1]
        trg = trg[0:-1]
        full_filename = trg + ' ' + '[' + target[-11:] + ']' + '.mp3'
        print(f'target_path + full_filename: {target_path}{full_filename}')
        print(f'source_path + full_filename: {source_path}{full_filename}')
        if os.path.exists(f'{target_path}{full_filename}') is False:
            if os.path.exists(f'{source_path}{full_filename}') is False:
                downloader(target)
                file_mover(target)
            else:
                file_mover(target)
        else:
            print(f'File "{full_filename}" already exist in the "{target_path}"')

    else:
        print(f'Video "{(readed_new[new - 1])[0:-1]}" is in old list already.')

        # DOWNLOAD & MOVING MISSING VIDEO
        trg = readed_new[new - 1]
        trg = trg[0:-1]
        full_filename = trg + ' ' + '[' + target[-11:] + ']' + '.mp3'
        print(f'target_path + full_filename: {target_path}{full_filename}')
        print(f'source_path + full_filename: {source_path}{full_filename}')
        if os.path.exists(f'{target_path}{full_filename}') is False:
            if os.path.exists(f'{source_path}{full_filename}') is False:
                downloader(target)
                file_mover(target)
            else:
                file_mover(target)
        else:
            print(f'File "{full_filename}" already exist in the "{target_path}"')

old_file.close()
new_file.close()
tmp_file.close()

shutil.copy('new.txt', 'new.backup')
shutil.copy('old.txt', 'old.backup')
os.renames('new.txt', 'old.txt')
os.remove('geckodriver.log')
# I need to add exist "old.txt" file checker at the first start
