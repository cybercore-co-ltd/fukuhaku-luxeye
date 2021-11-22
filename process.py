import torch
import torchvision
import torch.optim
import os
import argparse
import time
import model
import numpy as np
from torchvision import transforms
from PIL import Image
import glob
import time
import argparse
import smtplib, ssl
from os.path import exists
from os import stat
import datetime as dt
from cryptography.fernet import Fernet
import ast

def lowlight(image_path, output_dir):
	os.environ['CUDA_VISIBLE_DEVICES']='0'
	data_lowlight = Image.open(image_path)

	data_lowlight = (np.asarray(data_lowlight)/255.0)

	data_lowlight = torch.from_numpy(data_lowlight).float()
	data_lowlight = data_lowlight.permute(2,0,1)
	data_lowlight = data_lowlight.cuda().unsqueeze(0)

	DCE_net = model.enhance_net_nopool().cuda()
	DCE_net.load_state_dict(torch.load('snapshots/Epoch99.pth'))
	start = time.time()
	_,enhanced_image,_ = DCE_net(data_lowlight)

	end_time = (time.time() - start)
	print(end_time)
	image_name = os.path.basename(image_path)
	result_path = os.path.join(output_dir, image_name)
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	torchvision.utils.save_image(enhanced_image, result_path)

def send_mail(total_number_of_pictures):
    try:
        # port = 587  # For starttls
        port = 465  # For SMTP_SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "sender.cybercore@gmail.com"
        receiver_email = "receiver.morioka@gmail.com"
        password = "cybercoremorioka1!"
        subject="Test email for LuxEye"
        text = 'In this month ' + str(total_number_of_pictures) + ' pictures have been processed'
        message = 'Subject: {}\n\n{}'.format(subject, text)

    # with SMTP_SSL
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    except Exception as ex:
        print ("Error sending mail ",ex)

def process_mail_and_log(total_pics, date,f, data_exists):
	send_mail(total_pics)
	with open('mail_log.txt', 'a') as log_file:
		message = 'email sent on '+ str(date) 
		print (message)
		message = message.encode()
		current_encrypted_data = f.encrypt(message)
		if data_exists:
			encrypted_mail_data = ','+str(current_encrypted_data)
		else:
			encrypted_mail_data = str(current_encrypted_data)
		log_file.write(encrypted_mail_data)

def processed_picture_info_log(files_processed,total_pics,pic_exists):
	current_encrypted_data = encrypt_data(files_processed,total_pics)
	if pic_exists:
		encrypted_data = ','+ str(current_encrypted_data)
	else:
		encrypted_data = str(current_encrypted_data)
	with open('picture_count_log.txt', "a") as file:
		file.write(encrypted_data)

def get_current_time():
	today = dt.datetime.now()
	# year = today.year
	month = today.month
	day = today.day
	date = today.strftime("%m/%d/%Y")
	time_now = today.strftime("%H:%M:%S")
	return date,time_now,month,day

def encrypt_data(files_processed,total_files_processed):
	date,time_now,_,_ = get_current_time()
	log_data  = {'date' : date, 'time' : time_now, 'image_processed' : files_processed, 'total_image_processed': total_files_processed}
	# print (log_data)	
	log_data = str(log_data).encode()
	current_encrypted_data = f.encrypt(log_data)
	return current_encrypted_data

def recovering_data(encrypted_data,f):
	encrypted_data_split = encrypted_data.split(',')
	encrypted_data_last = encrypted_data_split[-1]
	# encrypted_data_last = encrypted_data_last.replace("b'","").replace("'","").encode()
	encrypted_data_last = encrypted_data_last[2:-1].encode()
	decrypted_data = str(f.decrypt(encrypted_data_last))[2:-1]
	return decrypted_data


if __name__ == '__main__':	
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--input_dir', required=True, help='path to input images')
	parser.add_argument('--output_dir', required=True, help='path to input images')
	args = parser.parse_args()
	send_date = 16
	key = "j-wo0BP76EORpbkTYgG2kbJZBber1Vr2DUml0Zlyv_0=".encode()
	f = Fernet(key)

# test_images
	with torch.no_grad():
		if (exists('picture_count_log.txt') and exists('mail_log.txt')):
			file_list = glob.glob(os.path.join(args.input_dir, "*"))
			files_processed = len(file_list)
			output_dir = args.output_dir
			for image in file_list:
				# print(image)
				lowlight(image, output_dir)
		
    		# checking if the file is empty
			if stat('picture_count_log.txt').st_size != 0:
				with open('picture_count_log.txt', "r") as file:
					# read the encrypted data
					encrypted_data = file.read()
				decrypted_data = recovering_data(encrypted_data,f)
				decrypted_data = ast.literal_eval(decrypted_data)
				total_pics = decrypted_data['total_image_processed'] + files_processed

				pic_exists = True
				processed_picture_info_log(files_processed,total_pics,pic_exists)

				date,_,month,day = get_current_time()
				if day >= send_date:
					if stat('mail_log.txt').st_size != 0:
						with open('mail_log.txt', "r") as file:
							# read the encrypted data
							encrypted_mail_data = file.read()
						# decrypt data
						decrypted_mail_data = recovering_data(encrypted_mail_data,f)
						# find the date (month) of last sent mail
						last_month = int (decrypted_mail_data[-10:-8])
						# checking if the the mail has already been sent
						if month == last_month:
							print ("Mail already sent")
						else:
							data_exists = True
							process_mail_and_log(total_pics, date,f, data_exists)
					else:
						data_exists = False
						process_mail_and_log(total_pics, date,f, data_exists)

			else:
				pic_exists = False
				processed_picture_info_log(files_processed,files_processed,pic_exists)
		else:
			raise("Important log file not found")
