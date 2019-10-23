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
    else:
        x = None
        for i in range(20):
            x1 = data['X'+fname+'_DE_time'][int(random.random()*slice_length) :]
            a1 = int(x1.shape[0]/slice_length)*slice_length
            x1 = np.array(x1[:a1]).reshape(-1, slice_length)
        
            x2 = data['X'+fname+'_FE_time'][int(random.random()*slice_length) :]
            a2 = int(x2.shape[0]/slice_length)*slice_length
            x2 = np.array(x2[:a2]).reshape(-1, slice_length)
            
            x_ = np.concatenate((x1,x2), axis = 0)
            if i == 0:
                x = x_
            else:
                x = np.concatenate((x, x_), axis = 0)
                
            y = np.array([[1,0] for i in range(x.shape[0])])

    print(x.shape)
    print(y.shape)
    return x, y 

x1=load_and_slice_data('driverend', 105, 1797, [0,1])
x2 =load_and_slice_data('fanend', 278, 1797, [0,1])
load_and_slice_data('nornal', 97, 1797, [0,1])


