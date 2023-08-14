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
        self.numInput = self.X.size(0)
        self.params = self.X.dim()
        if len(self.X != 0):
            if self.params == 1:
                self.domain = [self.X[0].item(), self.X[-1].item()]
                self.range = self.domain[1]-self.domain[0]
            elif self.params == 2:
                self.domain = [[self.X[0][0].item(), self.X[-1][0].item()], [self.X[0][1].item(), self.X[-1][1].item()]]
                self.range1 = self.domain[0][1]-self.domain[0][0]
                self.range2 = self.domain[1][1]-self.domain[1][0]
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
        if kernelInput == "sek":
            self.kernel = gpytorch.kernels.RBFKernel()  

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
        self.prediction = self.likelihood(self.observedPred).mean.detach().numpy()

    def probabilityOfImprovement(self):
        if self.params == 1:
            exploreX = self.range*torch.rand(25)+self.domain[0]
            bestPoint = self.target(self.prediction)
            observedPred = (self.model(exploreX))
            exploreY = self.likelihood(observedPred).mean.detach().numpy()
            stdev = np.sqrt(observedPred.variance.detach().numpy())
            z = (exploreY - bestPoint)/stdev
            cdf = norm.cdf(z)
            if self.target == max:
                index = np.argmax(cdf)
            else:
                cdf = -cdf
                index = np.argmin(cdf)
            
            newX = exploreX[index]
            return newX.double(), torch.tensor([index])
        elif self.params == 2:
            exploreX1 = self.range1*torch.rand(int(5))+self.domain[0][0]
            exploreX2 = self.range2*torch.rand(int(5))+self.domain[1][0]
            exploreX = torch.cat((
                exploreX1.contiguous().view(exploreX1.numel(), 1),
                exploreX2.contiguous().view(exploreX2.numel(), 1)),
                dim=1
            )
            bestPoint = self.target(self.prediction)
            observedPred = (self.model(exploreX))
            exploreY = self.likelihood(observedPred).mean.detach().numpy()
            stdev = np.sqrt(observedPred.variance.detach().numpy())
            z = (exploreY - bestPoint)/stdev
            cdf = norm.cdf(z)
            if self.target == max:
                index = np.argmax(cdf)
            else:
                cdf = -cdf
                index = np.argmin(cdf)
            newX = exploreX[index]
            return newX, index
    def evaluateNext(self):
        if self.params == 1:
            newX, index = self.acquisition()
            self.X.index_add(0, index, newX)
        elif self.params == 2:
            newX, index = self.acquisition()
            self.X = torch.cat((self.X, newX.unsqueeze(0)), 0)
    def plot(self):
        if self.params == 1:
            figure = go.Figure(data = go.Scatter(x = self.X, y = self.prediction, name = "Prediction"))
            figure.add_trace(go.Scatter(x = self.X, y = self.y, name = "Training data", mode= "markers"))
            return figure
        elif self.params == 2:
            x, y = torch.meshgrid(torch.linspace(self.domain[0][0], self.domain[0][1], 10), torch.linspace(self.domain[1][0], self.domain[-1][1], 10), indexing="ij")
            X = torch.cat((
                x.contiguous().view(x.numel(), 1),
                y.contiguous().view(y.numel(), 1)),
                dim=1
            )
            prediction = self.likelihood(self.model(X)).mean.detach().numpy()
            prediction = prediction.reshape(10, 10)
            figure2 = go.Figure(data = go.Surface(z = prediction, x = x, y = y))
            figure2.update_layout(scene = dict(
                    xaxis_title='param1',
                    yaxis_title='param2',
                    zaxis_title='output'),)
            return figure2
    def result(self):
        if self.params == 1:
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
        elif self.params == 2:
            if self.target == max:
                index = self.prediction.argmax()
            else:
                index = self.prediction.argmin()
            bestX1 = self.X[index][0].item()
            bestX2 = self.X[index][1].item()
            bestY = self.prediction[index]
            bestX1 = round(bestX1, 4)
            bestX2 = round(bestX2, 4)
            if self.target == max:
                result = "Output maximized at param1 value of " + str(bestX1) + " and param2 value of " + str(bestX2) + " for a predicted output of " +  str(bestY)
            else:
                result = "Output minimized at param1 value of " + str(bestX1) + " and param2 value of " + str(bestX2) + " for a predicted output of " +  str(bestY)
            return result