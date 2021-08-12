import csv
import os
import numpy as np
from os import path
from pydub import AudioSegment
from num2words import num2words as n2w
import argparse
import subprocess
import glob

parser = argparse.ArgumentParser(description="Preparing common voice dataset.")
parser.add_argument('-d', '--dataset', type=str, help='which dataset to prepare for')

args = parser.parse_args()

CHANNELS    = 1
SAMPLE_RATE = 16000
DATA_CSV    = f"cv-valid-{args.dataset}"

err_num = 0

def convert_to_wav(src, dst):
    global err_num
    for sound in glob.glob(os.path.join(src, '*.mp3')):
        # convert wav to mp3 
        wav_name = sound.split("/")[-1].split('.mp3')[0] + ".wav"
        try:   
            dst_new = os.path.join(dst, wav_name)
            subprocess.check_call(args=['ffmpeg', '-i','{}'.format(sound),\
                 '-acodec','pcm_s16le','-ac', '{}'.format(CHANNELS), '-ar', '{}'.format(SAMPLE_RATE),'{}'.format(dst_new), '-y'])

        except Exception:
            err_num += 1
            print(f"An error occured in {src}, process is continuing.. TOTAL ERRORS:{err_num}")
            continue

    print(f"All mp3 files converted to wav and copied to the wavs directory successfully.")


src_path = f"./DataArchive/{DATA_CSV}/{DATA_CSV}"
dst_path = f"./Ardıc_{args.dataset}_dataset/data/wavs/"
csv_file_path = f"./Ardıc_{args.dataset}_dataset/data/"

if not os.path.exists(dst_path):
    print(f"{dst_path} is being created.")
    os.makedirs(dst_path)

convert_to_wav(src_path, dst_path)

# read wavs file
present_clips = np.array(os.listdir(dst_path))
if ".DS_Store" in present_clips: 
    os.remove(".DS_Store")

with open(f"./DataArchive/{DATA_CSV}.csv", "r") as csv_read_file: ## .tsv file
    read_csv = csv.reader(csv_read_file)
    with open(csv_file_path + "metadata.csv", 'w') as csv_write_file:
        write_csv = csv.writer(csv_write_file)
        for i, row in enumerate(read_csv):
            if i == 0:
                continue
            if row[0].split("/")[-1].replace(".mp3", ".wav") not in present_clips: ## To avoid duplicate of data 
                print("File {} is not in dataset.".format(row[0]))
                continue
            else:
                id_to_write = row[0].split("/")[-1].split(".mp3")[0]
                content = row[1].lower()
                ## convert numbers to text
                content_list = content.split()
                for order, item in enumerate(content_list):
                    if item.isdigit():
                        item = (n2w(int(item), lang ='tr'))
                        content_list[order] = item
                content_clean = " ".join(content_list)
                write_csv.writerow([id_to_write + "|" + content + "|" + content_clean])

print("metadata.csv file is created successfully.")
