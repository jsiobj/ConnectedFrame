#!/usr/bin/env python

from Tkinter import *
from os import putenv, getenv, system, remove
from os.path import dirname, abspath,realpath
from PIL import Image, ImageTk 
from glob import glob

from time import sleep, strftime
import datetime
import urllib2
import inspect


import errno
import sys

#dropbox_link = getenv("DROPBOX_LINK")
#download_interval = int(getenv("DOWNLOAD_INTERVAL_HOURS")) * 60 * 60 * 1000
#carousel_interval = int(getenv("CAROUSEL_INTERVAL_SECONDS")) * 1000
frame_owner = getenv("FRAME_OWNER")
ifttt_key = getenv("IFTTT_KEY")

dropbox_link = "https://www.dropbox.com/sh/n5bo8z52lqm2eov/AAAC3ylCk86jT85L0s-D_CwGa?dl=1"
download_interval = 1 * 60 * 60 * 1000
carousel_interval = 20 * 1000

script_path = dirname(realpath(__file__))
image_path = script_path + "/images"
icon_path = script_path + "/icons"

carrousel_status = True
image_index = 0
image_list = []
initial_init = True


def debugPrint(msg,logLevel=3,logFileName=script_path + "/ConnectedFrame.log"):

	maxLogLevel=9
    
	if logLevel<=maxLogLevel:
        
		fullMsg  = strftime("%X-%d/%m/%Y")
		fullMsg += "|"
		fullMsg += inspect.stack()[1][3]
		fullMsg += "|"
		fullMsg += str(logLevel)
		fullMsg += "|"
		fullMsg += msg
      
		with open(logFileName,'a') as logFile:
			logFile.write(fullMsg + '\n')
			logFile.close()

def download_images(url):
	archive = image_path + "/temp.zip"

	download = "wget -q  "+ url + " -O " + archive
	extract = "unzip -o " + archive + " -d " + image_path

	try:
		remove(image_path + "/*")
	except OSError as e: 
		if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
			raise # re-raise exception if a different error occurred


	debugPrint("Downloading photos...")
	system(download)
	debugPrint("Extracting photos...")
	system(extract)

def resize_images():
	images = list_images()

	for file in images:
		img = Image.open(file)
		img = img.resize((640, 480), Image.ANTIALIAS)
		img.save(file, "JPEG")

def list_images():
	images = []

	dir = image_path + "/*.JPG"
	debugPrint("glob:"+dir)

	images = glob(dir)
	debugPrint(','.join(images))

	return images

def previous_image():
	global image_index
	image_index = image_index - 1

	if image_index < 0:
		image_index = len(image_list) - 1

	image_path = image_list[image_index]

	update_image(image_path)
	
def next_image():
	global image_index
	image_index = image_index + 1

	if image_index > len(image_list) - 1:
		image_index = 0

	image_path = image_list[image_index]

	update_image(image_path)

def play_pause():
	global carrousel_status

	carrousel_status = not carrousel_status

	if(carrousel_status):
		img = ImageTk.PhotoImage(Image.open(icon_path + "/pause.png"))
	else:
		img = ImageTk.PhotoImage(Image.open(icon_path + "/play.png"))
	
	play_button.configure(image=img)
	play_button.image = img

def carrousel():
	if(carrousel_status):
		next_image()

	root.after(carousel_interval, carrousel)

def update_image(image_path):
	img = ImageTk.PhotoImage(Image.open(image_path))
	center_label.configure(image=img)
	center_label.image = img

	img = ImageTk.PhotoImage(Image.open(icon_path + "/like.png"))
	like_button.configure(image=img)
	like_button.image = img

def initialize():
	global image_list, carrousel_status, initial_init
	current_carrousel_status = carrousel_status
	carrousel_status = False

	download_images(dropbox_link)
	resize_images()
	image_list = list_images()

	carrousel_status = current_carrousel_status

	if(initial_init):
		initial_init = False
		root.after(1000, initialize)
	else:
		root.after(download_interval, initialize)

def send_event():
	img = ImageTk.PhotoImage(Image.open(icon_path + "/liked.png"))
	like_button.configure(image=img)
	like_button.image = img

	command = "curl -X POST -H \"Content-Type: application/json\" -d '{\"value1\":\"" + frame_owner + "\",\"value2\":\"" + image_list[image_index] + "\"}' https://maker.ifttt.com/trigger/connectedframe_like/with/key/" + ifttt_key

	system(command)


debugPrint("Starting...")

root = Tk()
root.title('Connected Frame')
root.geometry('{}x{}'.format(800, 480))
root.attributes("-fullscreen", True)
root.config(cursor='none')

initialize()

left_column = Frame(root, bg='black', width=80, height=480)
center_column = Frame(root, bg='black', width=640, height=480)
right_column = Frame(root, bg='black', width=80, height=480)

left_column.pack_propagate(0)
center_column.pack_propagate(0)
right_column.pack_propagate(0)

left_column.grid(row=0, column=0, sticky="nsew")
center_column.grid(row=0, column=1, sticky="nsew")
right_column.grid(row=0, column=2, sticky="nsew")

next_icon = ImageTk.PhotoImage(Image.open(icon_path + "/next.png"))
previous_icon = ImageTk.PhotoImage(Image.open(icon_path + "/previous.png"))
play_icon = ImageTk.PhotoImage(Image.open(icon_path + "/pause.png"))
like_icon = ImageTk.PhotoImage(Image.open(icon_path + "/like.png"))

previous_button = Button(left_column, image=previous_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=previous_image)
next_button = Button(left_column, image=next_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=next_image)
play_button = Button(right_column, image=play_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=play_pause)
like_button = Button(right_column, image=like_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=send_event)

center_image = Image.open(image_list[0])
center_photo = ImageTk.PhotoImage(center_image)
center_label = Label(center_column, image=center_photo)

previous_button.pack(fill=BOTH, expand=1)
next_button.pack(fill=BOTH, expand=1)
center_label.pack(side="bottom", fill=BOTH, expand=1)
play_button.pack(fill=BOTH, expand=1)
like_button.pack(fill=BOTH, expand=1)

carrousel()

root.mainloop()
