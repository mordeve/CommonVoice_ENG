import csv
import os
from os import path
from pydub import AudioSegment
from num2words import num2words as n2w
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Preparing common voice dataset.")
parser.add_argument('-d', '--dataset', type=str, help='which dataset to prepare for')

args = parser.parse_args()

CHANNELS    = 1
SAMPLE_RATE = 16000
err_num = 0

def convert_to_wav_and_copy(src, dst, filename):
    global err_num
    filename_old = os.path.join(src, filename)
    filename_new = filename.split('.mp3')[0] + ".wav"
    try:   
        dst_new = os.path.join(dst, filename_new)
        subprocess.check_call(args=['ffmpeg', '-i','{}'.format(filename_old), \
                '-acodec','pcm_s16le','-ac', '{}'.format(CHANNELS), '-ar',    \
                    '{}'.format(SAMPLE_RATE),'{}'.format(dst_new), '-y'])

    except Exception:
        err_num += 1
        print(f"An error occured in {src}, process is continuing.. TOTAL ERRORS:{err_num}")

    

src_path      =  "./../../../../../Downloads/cv-corpus-eng/en/clips/"
tsv_file_path = f"./../../../../../Downloads/cv-corpus-eng/en/{args.dataset}.tsv/"

dst_path      = f"./common_voice_{args.dataset}/data/wavs/"
csv_file_path = f"./common_voice_{args.dataset}/data/"



if not os.path.exists(dst_path):
    print("dst path created.")
    os.makedirs(dst_path)

## read ./clips
present_clips = os.listdir(dst_path)
if ".DS_Store" in present_clips:
    present_clips.remove(".DS_Store")

     
with open("./LibriSpeech/validated.tsv", "r") as tsv_file: ## .tsv file
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    with open(csv_file_path + 'metadata.csv', 'a') as csv_file:
        writer = csv.writer(csv_file)
        for i, row in enumerate(read_tsv):
            if i == 0:
                continue
            if row[1] in present_clips: ## To avoid duplicate of data 
               print("File {} is present in dataset.".format(row[1]))
               continue
            convert_to_wav_and_copy(src_path, dst_path, row[1])
            content = row[2].lower()
            ## convert numbers to text
            content_list = content.split()
            for order, item in enumerate(content_list):
                if item.isdigit():
                    item = (n2w(int(item), lang ='en'))
                    content_list[order] = item
            content_clean = " ".join(content_list)
            writer.writerow([row[1].split(".mp3")[0] + "|" + content + "|" + content_clean])

print("All mp3 files in dataset converted to wav and copied to the wavs directory successfully.")
print("metadata.csv file is created successfully.")
