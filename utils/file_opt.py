import os
import json
import csv

def save_json_to_file(file_path,json_data):
    folderpath = file_path.replace("/"+file_path.split("/")[-1],'')
    folder = os.path.exists(folderpath)
    if not folder:
        os.makedirs(folderpath)
    f = open(file_path, 'w')
    content = json.dumps(json_data)
    f.write(content)
    f.close()

def read_json_from_file(file_path):
    f = open(file_path, 'r',encoding="utf8")
    content = json.loads(f.readline())
    f.close()
    return content

def save_line_to_file(file_path,line):
    f = open(file_path, 'a')
    f.write(line+"\n")
    f.close()

def read_lastline_in_file(file_path):
    f = open(file_path, 'r')
    content = f.readlines()
    f.close()
    if content == []:
        return None
    else:
        return content[-1][:-1]

def save_csv_to_file(file_path,csv_data):
    folderpath = file_path.replace("/"+file_path.split("/")[-1],'')
    folder = os.path.exists(folderpath)
    if not folder:
        os.makedirs(folderpath)
    f = open(file_path, 'w', newline="", encoding='utf-8')
    csv_writer = csv.writer(f, dialect='excel')
    csv_writer.writerows(csv_data)
    f.close()

def read_csv_from_file(file_path):
    f = open(file_path, 'r',encoding="utf8")
    content = csv.reader(f)
    return content