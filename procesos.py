import os

os.system('ps aux |grep python > log.txt')



with open('log.txt', 'r') as infile:

    data = infile.read() 



my_list = data.splitlines()

caido='Si'

for d in my_list:

	

	if str(d).find('0.0.0.0:1000') != -1:

		caido = 'No'



if caido =='Si':

	os.system('cd /home/proyectos/')