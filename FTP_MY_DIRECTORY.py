#!/usr/bin/env python
'''
Python Script to login to a ftp server and transfer data.
Creates a dictionary of file name and compares the MD5 checksum of the files in directory
'''

import os
import glob
from ftplib import FTP
import hashlib

def ftp_login(ip, user, password):
	'''
	Logs to the given ftp address.
	
	:param ip: Ip address of the server as string
	:param user: user name as string
	:param password: password as string
	'''
	try:
	   ftp = FTP()
	   ftp.connect(server)
	   ftp.login(u_name, token)
	   print "FTP connection Established"
	   return ftp
	except IOError as e:
	    print "I/O error({0}): {1}".format(e.errno, e.strerror)

def get_md5_ftp(ftp, remote_path):
	'''
	Returns the MD5 Signature of the file in a FTP server
	
	:param ftp: ftp object that has established connection
	:pram remote_path: The file path of the file whose md5 hash is to be calculated
	'''
	
	mhash = hashlib.md5()
	ftp.retrbinary('RETR %s' % remote_path, mhash.update)
	return mhash.hexdigest()

def upload_file(ftp, origin_path, destin_path):
	'''
	Upload files from local to ftp server using binary store
	
	:param ftp: ftp object that has established connection
	:param origin_path: The path of the file to be copied or transfered
	:param destin_path: The destination file path to be copied or over written
	'''
	#Use binary store
	try:
	   ftp.storbinary('STOR ' + destin_path , open(origin_path, 'rb'))
	except Exception, err:
	   print err


if __name__ == '__main__':

	##################################user data to modify################################
	
	server = "72.0.146.92" # Change to your IP
	u_name = "myusername" # Use your User Name
	token = "!mypassword" #use your password
	origin_path = r"/Users/Chikoo/Desktop/TEST_FTP" # local directory with the files
	destin_path = "test" # Directory path in the ftp server where files are to be copied
	
	#####################################################################################
	
	
	# create a ftp connection
	ftp = ftp_login(server, u_name, token)
	
	# get ftp dir list
	ftp_dir = ftp.nlst(destin_path)
	print ftp_dir

	# go through the list of files in the directory
	mydir = glob.glob(origin_path + "/*.Airfoil")
        
	# Loop through each file and check if it exist in ftp location. If
	# it exist do MD5 comparison and if varies copy the new file else
	# dont update. If the file does not exit copy the new file.
        
	for file in mydir:
	    f_name = os.path.basename(file)
	    dest_fname = os.path.join(destin_path, f_name)
	    
	    #get md5 hash of origin file
	    org_MD5_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
	    
	    #Check if file in sin ftp dir list
	    if f_name in ftp_dir:
	        # Get MD5 Hash of ftp file
	        des_MD5_hash = get_md5_ftp(ftp, dest_fname)
	        
	        #compare hashes
	        if org_MD5_hash == des_MD5_hash:
	            print "{0} already in ftp server".format(f_name)
	        else:
	            print "MD5 checksum is different. Updating with new file"
	            print "Copying {0} to ftp server".format(f_name)
	            upload_file(ftp, file, dest_fname)
	    else:
	        print "{0} is not in ftp directory. Copying file to ftp server".format(f_name)
	        upload_file(ftp, file, dest_fname)
	    
	ftp.close()
	print "FTP connection Closed"