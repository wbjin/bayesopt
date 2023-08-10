import pandas as pd
import torch
import gpytorch
from .model import ExactGPModel
import plotly.graph_objects as go

class Optimizer:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.optimizationResults = []

    def setOptimizationTarget(self, target):
        if target == "Maximize":
            self.target = max
        else:
            self.target = min

    def trainGP(self, trainIter = 10):
        self.kernel = gpytorch.kernels.MaternKernel(nu=0.5, ard_nums = 1)
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
        self.observedPred = self.likelihood(self.model(self.X))
        self.prediction = self.observedPred.mean.detach().numpy() 
    
    def run(self):
        self.trainGP()
        return self.plot()
    
    def plot(self):
        figure = go.Figure(data = go.Scatter(x = self.X, y = self.prediction, name = "Prediction"))
        figure.add_trace(go.Scatter(x = self.X, y = self.y, name = "Training data", mode= "markers"))
        return figure
