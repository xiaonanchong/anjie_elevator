def loadmatlabfile(filepath, filename):# '/home/anjie/data/', '97.mat'
	from scipy.io import loadmat
	data = loadmat(filepath+filename)
	data_id = int(filename[:-4])
	if data_id < 100:
		FE = data['X0'+str(data_id)+'_FE_time']
		DE = data['X0'+str(data_id)+'_DE_time']
	else:
		FE = data['X'+str(data_id)+'_FE_time']
		DE = data['X'+str(data_id)+'_DE_time']
	return DE, FE

def slice_data(DE, slice_len, label): # DE, 3000, [0,1,0]
	import numpy as np
	a = int(DE.shape[0]/slice_len)*slice_len
	x = np.array(DE[:a]).reshape(-1, slice_len)
	y = np.array([label for i in range(x.shape[0])])
	return x, y

def load_and_slice(filepath, filename, label, slice_len=3000):
	import numpy as np
	k = str(filename)+'.mat'
	d,f = loadmatlabfile(filepath, k)
	x1, y1 = slice_data(d, slice_len, label)
	x2, y2 = slice_data(f, slice_len, label)
	x = np.concatenate((x1,x2), axis = 0)
	y = np.concatenate((y1,y2), axis = 0)
	return x,y

def form_training_data(file_list, label, slice_len=3000):#[97, 105], [1,0,0]
	import numpy as np	
	fp  = '/home/anjie/data/'
	x_train, y_trian = load_and_slice(fp, file_list[0], label, slice_len=3000)
	for k in file_list[1:]:
		k = str(k)+'.mat'
		d, f = loadmatlabfile(fp, k)
		x1, y1 = slice_data(d, slice_len, label)
		x2, y2 = slice_data(f, slice_len, label)
		x = np.concatenate((x1,x2), axis = 0)
		y = np.concatenate((y1,y2), axis = 0)
	x_train = np.concatenate((x_train, x), axis = 0)
	y_train = np.concatenate((y_trian, y), axis = 0)
	return x_train, y_train

def concatenate(data_list):
	import numpy as np
	x = data_list[0]
	for i in data_list[1:]:
		x = np.concatenate((x, i), axis = 0)
	return x


#loadmatlabfile('/home/anjie/data/', '97.mat')
