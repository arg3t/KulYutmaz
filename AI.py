import pickle
import numpy

def aiPredict(data):  # 32 lik liste yada deste alir.
    with open("AIModel", "rb") as m:
        aiModel = pickle.load(m)
    return aiModel.predict(numpy.reshape(data,(1, 32)))    
