# Fukuhaku Luxeye Library
# 1. Installation
![fukuhaku_concept](https://user-images.githubusercontent.com/60061358/143806781-1ea19974-9943-4e4a-81cc-8af355c6c88e.png)

### Create an environment for the project

$ conda create --name cc-luxeye python=3.7.7

### Activate the environment

$ conda activate cc-luxeye

### Requirements for creating the necessary environment

The necessary packages are listed in 'requirements.txt' file.
Install the packages with....

$ pip install -r requirements.txt

# 2. Command to run the program
### run the following command to process images in "input_dir":

$ python process.py --input_dir data/test_data/DICM/ --output_dir data/test_result/

# 3. Samples
| Input             |  Output |
:-------------------------:|:-------------------------:
![](data/test_data_2/0288.bmp)  |  ![](data/test_result_2/0288.bmp)
![](data/test_data_2/0293.bmp)  |  ![](data/test_result_2/0293.bmp)
![](data/test_data_2/IMG_9114.bmp)  |  ![](data/test_result_2/IMG_9114.bmp)


