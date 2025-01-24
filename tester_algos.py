import numpy as np
import pandas as pd

def smaAlgo(data):
    data.dropna(inplace=True)

    SMA1=42
    SMA2=252

    data['SMA1']=data['Close'].rolling(SMA1).mean()
    data['SMA2']=data['Close'].rolling(SMA2).mean()
    data['Position'] = np.where(data['SMA1']>data['SMA2'], 1, -1)

    data.dropna(inplace=True)
    return data