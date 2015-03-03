"""
*****************************************************************
*
*  File Name........: ims_simulation.py
*
*  Description......: Simulation program for IMS
*
*  Author...........: Shashanka Sharma
*
*****************************************************************
"""

#!/usr/bin/python
import random
import math as m

def average(a):
	return (m.fsum(a)/len(a))

def percentile(a,i):
	b = a
	b.sort()
	k = int(m.ceil(i*len(a)/100))
	return b[k-1]

def std(a):
	b = a
	mean = average(a)
	sum = 0.0
	for i in b:
		sum += m.pow(i-mean,2)
	sdev = m.sqrt (sum/(len(b)-1))
	return sdev

#Open input file to read values
inlist = [] 
with open('input.txt','r') as filedes:
	for line in filedes:
		inlist.append(line)
filedes.close()

# Take input values
"""
lam = 1
up = 0.1
us = 0.2
uas = 0.5
departure = 60100
batch_num = 60
"""
lam = float(inlist[0])
up = float(inlist[1])
us = float(inlist[2])
uas = float(inlist[3])
departure = int(inlist[4])
batch_num = int(inlist[5])


#Calculate batch size from total departures and batch_num
batch_size = int((departure-300)/batch_num)

# Assign values to static variables
seed = 51517
MC = 0.05

# List to track next service time
next_time = {'tarr':0.05,'tpc':99999999999,'tsc':99999999999,'tasc':99999999999}

#List of UEs who have completed service
UE_List = []
tarr=[]

#Initial state for P-CSCF, S-CSCF and AS
P = {'current':{},'queue':[]}
S = {'current':{},'queue':[]}
AS = {'current':{},'queue':[]}

#Insert first arrival detail with time of entry = MC
tarr.append({'ue_id':1,'t_entry':0.05,'t_exit':0.0,'t_delay':0.0,'flag':False})

#Generate arrival sequences for all departures plus extra (to simulate infinite UEs) using random sequences
random.seed(seed)
for i in range(1,departure+1000):
	tentry = tarr[i-1]['t_entry'] - 1/lam*m.log(random.random())
	tarr.append({'ue_id':i+1,'t_entry':tentry,'t_exit':0.0,'t_delay':0.0,'flag':False})

while (True):
	MC = min(next_time.itervalues())	
	event = min(next_time,key=next_time.get)
#	print event
	if event is 'tarr':
#		print next_time
#		print tarr[0]
		if(len(P['current'])==0 ):
			P['current']=(tarr.pop(0))
			if (len(tarr)==0):
				next_time['tarr'] = 99999999999
			else:
				next_time['tarr'] = tarr[0]['t_entry']
			next_time['tpc'] = MC - up*m.log(random.random())
			continue
		elif (len(P['current'])!=0):			
			P['queue'].append(tarr.pop(0))
			if (len(tarr)==0):
				next_time['tarr'] = 99999999999
			else:
				next_time['tarr'] = tarr[0]['t_entry']
			continue

#print P['current']['flag']
	if event is 'tpc':
#		print next_time
#		print P['current']
		if (P['current']['flag'] is False):	#Using Flag is False for forward direction (P-CSCF --> S-CSCF --> AS)
#			print "Going towards S-CSCF"			
			if(len(S['current'])==0):
				S['current'] = P['current']
				if (len(P['queue'])!=0):			
					P['current']=P['queue'].pop(0)
					next_time['tpc'] = MC - up*m.log(random.random())								
				else:
					P['current']={}
					next_time['tpc'] = 99999999999
				next_time['tsc']= MC - us*m.log(random.random())
				continue
			elif (len(S['current'])!=0):
				S['queue'].append(P['current'])
				if (len(P['queue'])!=0):			
					P['current']=P['queue'].pop(0)
					next_time['tpc'] = MC - up*m.log(random.random())
				else:
					P['current']={}
					next_time['tpc'] = 99999999999
				continue
		else:
#			print "Exiting system"
			P['current']['t_exit'] = next_time['tpc']
			P['current']['t_delay'] = P['current']['t_exit'] - P['current']['t_entry']
#			print P['current']
			UE_List.append(P['current'])
#			print len(UE_List),"customers exited"
			if (len(P['queue'])!=0):
				P['current']=P['queue'].pop(0)
				next_time['tpc'] = MC - up*m.log(random.random())
			else:
				P['current']={}	
				next_time['tpc'] = 99999999999
			if(len(UE_List)==departure):
				break			
			continue
	if event is 'tsc':
#		print next_time
#		print S['current']
		if S['current']['flag'] is False:	#Using Flag is False for forward direction (P-CSCF --> S-CSCF --> AS)
			if(len(AS['current'])==0):
				AS['current'] = S['current']
				if (len(S['queue'])!=0):			
					S['current']=S['queue'].pop(0)
					next_time['tsc'] = MC - us*m.log(random.random())
				else:
					S['current']={}
					next_time['tsc'] = 99999999999
				next_time['tasc']= MC - uas*m.log(random.random())
				continue
			elif (len(AS['current'])!=0):
				AS['queue'].append(S['current'])
				if (len(S['queue'])!=0):			
					S['current']=S['queue'].pop(0)
					next_time['tsc'] = MC - us*m.log(random.random())
				else:
					S['current']={}
					next_time['tsc'] = 99999999999
				continue
		else:
			if(len(P['current'])==0 ):
				P['current']=S['current']
				next_time['tpc'] = MC - up*m.log(random.random())
				if (len(S['queue'])!=0):			
					S['current']=S['queue'].pop(0)
					next_time['tsc'] = MC - us*m.log(random.random())
				else:
					S['current']={}
					next_time['tsc'] = 99999999999
				continue
			elif (len(P['current'])!=0):
				P['queue'].append(S['current'])
				if (len(S['queue'])!=0):			
					S['current']=S['queue'].pop(0)
					next_time['tsc'] = MC - us*m.log(random.random())
				else:
					S['current']={}
					next_time['tsc'] = 99999999999
				continue
	if event is 'tasc':
#		print next_time
#		print AS['current']
		AS['current']['flag'] = True
		if(len(S['current'])==0 ):
			S['current']=AS['current']
			next_time['tsc'] = MC - us*m.log(random.random())
			if (len(AS['queue'])!=0):			
				AS['current']=AS['queue'].pop(0)
				next_time['tasc'] = MC - uas*m.log(random.random())
			else:
				AS['current']={}
				next_time['tasc'] = 99999999999
			continue
		elif (len(S['current'])!=0):
			S['queue'].append(AS['current'])
			if (len(AS['queue'])!=0):			
				AS['current']=AS['queue'].pop(0)
				next_time['tasc'] = MC - uas*m.log(random.random())
			else:
				AS['current']={}	
				next_time['tasc'] = 99999999999
			continue			

#Create lists to store delay values, batch means and batch percentiles
delay_list_all = []
batch_list_mean = []
batch_list_percentile = []
batch_list = []

#print len(UE_List)
#print UE_List

#print UE_List[len(UE_List)-1]['t_exit']

#Calculate batch mean and append to batch_list_mean, calculate batch percentile and append to batch_list_percentile
for i in range(batch_num):
	for k in range(100+batch_size*i,100+batch_size+batch_size*i):
		batch_list.append(UE_List[k]['t_delay'])
		delay_list_all.append(UE_List[k]['t_delay'])
	batch_list_mean.append(average(batch_list))
	batch_list_percentile.append(percentile(batch_list,95))
	batch_list = []

#Calculate batch mean and batch percentile
batch_mean = average(batch_list_mean)
batch_percentile = average(batch_list_percentile)

#Calculate standard devition for the batches
batch_mean_sd = std(batch_list_mean);
batch_percentile_sd = std(batch_list_percentile);

#Calculate error for the batches
error_mean = 1.96*batch_mean_sd/m.sqrt(batch_num)
error_percentile = 1.96*batch_percentile_sd/m.sqrt(batch_num)

# Uncomment below lines to print output on screen:

#print "Mean end-to-end delay w/o batch: ",average(delay_list_all)
#print "95th percentile end-to-end delay w/o batch: ",percentile(delay_list_all,95)
#print "Mean end-to-end delay w batch: ",batch_mean
#print "Confidence interval of mean at 95% confidence: [",(batch_mean-error_mean),",",(batch_mean+error_mean),"]"
#print "95th percentile end-to-end delay with batch: ",batch_percentile
#print "Confidence interval of 95th percentile at 95% confidence: [",(batch_percentile-error_percentile),",",(batch_percentile+error_percentile),"]"

#Open output file to write results
with open('output.txt','wb') as filedes:
	filedes.write("Mean of end-to-end delay without using batch means: "+str(average(delay_list_all))+"\n")
	filedes.write("95th percentile without using batch means: "+str(percentile(delay_list_all,95))+"\n")
#	filedes.write("Mean end-to-end delay w batch: "+str(batch_mean)+"\n")
#	filedes.write("Mean of end-to-end delay and confidence interval using batch means: ["+str((batch_mean-error_mean))+","+str((batch_mean+error_mean))+"]\n")
	filedes.write("Mean of end-to-end delay and confidence interval using batch means: ["+str((batch_mean-error_mean))+","+str(batch_mean)+","+str((batch_mean+error_mean))+"]\n")
#	filedes.write("95th percentile end-to-end delay with batch: "+str(batch_percentile)+"\n")
	filedes.write("95th percentile and confidence interval using batch means: ["+str((batch_percentile-error_percentile))+","+str(batch_percentile)+","+str((batch_percentile+error_percentile))+"]\n")
#	filedes.write("95th percentile and confidence interval using batch means: ["+str((batch_percentile-error_percentile))+","+str((batch_percentile+error_percentile))+"]\n")
filedes.close()
