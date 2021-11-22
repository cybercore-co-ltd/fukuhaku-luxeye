from posixpath import basename
from celery import Celery, shared_task, current_task
from django.conf import settings
import sys
import os
sys.path.append(os.path.join(settings.BASE_DIR, "luxeye", "algorithms", "BrightFast", "BrightFast_code"))
import torch
import torch.nn as nn
import torchvision
import torch.backends.cudnn as cudnn
import torch.optim
import argparse
import time
import dataloader
import model
import numpy as np
from torchvision import transforms
from PIL import Image
import glob
import time
from luxeye.algorithms.tool import MyParser
import subprocess

import cv2

def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

def remove4chanel(opencv_image):
    if len(opencv_image.shape) > 2 and opencv_image.shape[2] == 4:
        #convert the image from RGBA2RGB
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2BGR)
    return opencv_image

@shared_task
def run(in_folder,out_folder,method,model_name):
    # pid_file = MyParser().as_dict()['uwsgi']['smart-attach-daemon'].split(' ')[0]
    try:
        DCE_net = model.enhance_net_nopool().cuda()
        print("hello bright fast")
        urls = []
        with torch.no_grad():
            # filePath = 'data/test_data/'
        
            test_list = sorted(glob.glob(in_folder+"/*"))

            for index, image in enumerate(test_list):
                # image = image
                print(image)
                file_name = basename(image)
                save_path = out_folder+"/"+file_name
                print("save path", save_path)
                lowlight(DCE_net, image, save_path)

                img_name_url = settings.MEDIA_URL + save_path.split(settings.MEDIA_URL)[1]
                urls.append(img_name_url)

                print("len test list", len(test_list))

                percent_number = round((index+1)/len(test_list)*100,2)
                # pid_file = MyParser().as_dict()['uwsgi']['smart-attach-daemon'].split(' ')[0]
                # pid_number = open(pid_file).read()
                # print("pid number", pid_number)
                # subprocess.run(["kill", str(int(pid_number))])

                current_task.update_state(state='PROGRESS',
                                    meta={'urls': urls, 'percent': percent_number, 'method': method})

            return {'urls': urls, 'percent': 100, 'method': method}
    except Exception as error:
        print("error", error)
        current_task.update_state(state='FAILURE',
                            meta={'urls': [], 'percent': 100, 'method': method, 'state': 'FAILURE'})
        return {'urls': [], 'percent': 100, 'method': method, 'state': 'FAILURE'}
    

def lowlight(DCE_net, image_path, save_path):
    # os.environ['CUDA_VISIBLE_DEVICES']='0'
    data_lowlight = Image.open(image_path)
    data_lowlight = pil2cv(data_lowlight)
    data_lowlight = remove4chanel(data_lowlight)
    data_lowlight = cv2pil(data_lowlight)

    data_lowlight = (np.asarray(data_lowlight)/255.0)

    data_lowlight = torch.from_numpy(data_lowlight).float()
    data_lowlight = data_lowlight.permute(2,0,1)
    data_lowlight = data_lowlight.cuda().unsqueeze(0)

    # DCE_net = model.enhance_net_nopool().cuda()

    current_folder = os.path.dirname(os.path.abspath(__file__))
    DCE_net.load_state_dict(torch.load(current_folder+'/'+'snapshots/Epoch99.pth'))
    start = time.time()
    _,enhanced_image,_ = DCE_net(data_lowlight)

    end_time = (time.time() - start)
    print(end_time)
    # image_path = image_path.replace('test_data','result')
    # result_path = image_path
    # if not os.path.exists(image_path.replace('/'+image_path.split("/")[-1],'')):
    # 	os.makedirs(image_path.replace('/'+image_path.split("/")[-1],''))

    torchvision.utils.save_image(enhanced_image, save_path)
    

# if __name__ == '__main__':
# # test_images
# 	with torch.no_grad():
# 		filePath = 'data/test_data/'
    
# 		file_list = os.listdir(filePath)

# 		for file_name in file_list:
# 			test_list = glob.glob(filePath+file_name+"/*") 
# 			for image in test_list:
# 				# image = image
# 				print(image)
# 				lowlight(image)
