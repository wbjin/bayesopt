import pandas as pd
import torch
import gpytorch
from .model import ExactGPModel
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm

class Optimizer:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        if len(self.X != 0):
            self.domain = [self.X[0].item(), self.X[-1].item()]
            self.range = self.domain[1]-self.domain[0]

    def run(self):
        self.trainGP()
        for i in range(5):
            self.modelSurrogate()
            self.evaluateNext()
        return self.plot()

    def setOptimizationTarget(self, target):
        if target == "Maximize":
            self.target = max
            self.targetIndex = np.argmax
        else:
            self.target = min
            self.targetIndex = np.argmin
    
    def setKernel(self, kernelInput):
        self.kernel = gpytorch.kernels.MaternKernel(nu=0.5, ard_nums = 1)
        if kernelInput == "matern":
            self.kernel = gpytorch.kernels.MaternKernel(nu=0.5, ard_nums = 1) 

    def setAcquisition(self, acquisitionInput):
        self.acquisition = self.probabilityOfImprovement 
        if acquisitionInput == "pi":
            self.acquisition = self.probabilityOfImprovement 
        
    def trainGP(self, trainIter = 10):
        self.likelihood = gpytorch.likelihoods.GaussianLikelihood()
        self.model = ExactGPModel(self.X, self.y, self.likelihood, self.kernel)
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(self.likelihood, self.model)

        self.model.train()
        self.likelihood.train()

        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.1)
        for i in range(trainIter):
            optimizer.zero_grad()
            output = self.model(self.X)
            loss = -mll(output, self.y)
            loss.backward()
            optimizer.step()

        self.model.eval()
        self.observedPred = (self.model(self.X))
    
    def modelSurrogate(self):
        self.observedPred = self.model(self.X)
        self.prediction = self.likelihood(self.observedPred).mean.detach().numpy()

    def probabilityOfImprovement(self):
        exploreX = self.range*torch.rand(int(self.range*10))+self.domain[0]
        bestPoint = self.target(self.prediction)
        observedPred = (self.model(exploreX))
        exploreY = self.likelihood(observedPred).mean.detach().numpy()
        stdev = np.sqrt(observedPred.variance.detach().numpy())
        z = (exploreY - bestPoint)/stdev
        cdf = norm.cdf(z)
        cdf[stdev<0] == 0.0
        if self.target == max:
            index = np.argmax(cdf)
            newX = exploreX[index]
        else:
            cdf = -cdf
            index = np.argmin(cdf)
            newX = exploreX[index]
        return newX.double(), torch.tensor([index])
    
    def evaluateNext(self):
        newX, index = self.acquisition()
        self.X.index_add(0, index, newX)

    def plot(self):
        figure = go.Figure(data = go.Scatter(x = self.X, y = self.prediction, name = "Prediction"))
        figure.add_trace(go.Scatter(x = self.X, y = self.y, name = "Training data", mode= "markers"))
        return figure
    
    def result(self):
        if self.target == max:
            index = self.prediction.argmax()
        else:
            index = self.prediction.argmin()
        bestX = self.X[index].item()
        bestY = self.prediction[index]
        bestX = round(bestX, 4)
        bestY = round(bestY, 4)
        if self.target == max:
            result = "Output maximized at param1 value of " + str(bestX) + " for a predicted output of " +  str(bestY)
        else:
            result = "Output minimized at param1 value of " + str(bestX) + " for a predicted output of " +  str(bestY)
        return result
