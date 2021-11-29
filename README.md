# Fukuhaku Luxeye Library
# 1. Installation

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
![](data/test_result_2/0288.jpg)  |  ![](data/test_result_2/0288.jpg)
![](data/test_data_2/0293.bmp)  |  ![](data/test_result_2/0293.jpg)
![](data/test_data_2/IMG_1416.jpg)  |  ![](data/test_result_2/IMG_1416.jpg)


