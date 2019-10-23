import numpy as np
import random
def load_and_slice_data(end, fname, rpm, target):
    data = loadmat('data/'+str(fname)+'.mat')
    if fname < 100:
        fname = '0'+str(fname)
    else:
        fname = str(fname)
        
    slice_length = int((60*5*12000)/rpm)
    print('slice_length:', slice_length)
    
    if end == 'driverend':
        x = data['X'+fname+'_DE_time']
        a = int(x.shape[0]/slice_length)*slice_length
        x = np.array(x[:a]).reshape(-1, slice_length)
        y = np.array([[0,1] for i in range(x.shape[0])])
        
    elif end == 'fanend':
        x = data['X'+fname+'_FE_time']
        a = int(x.shape[0]/slice_length)*slice_length
        x = np.array(x[:a]).reshape(-1, slice_length)
        y = np.array([[0,1] for i in range(x.shape[0])])
