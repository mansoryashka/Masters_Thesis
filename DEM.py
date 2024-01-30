import time
import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.autograd import grad
import matplotlib
matplotlib.rcParams['figure.dpi'] = 350
# np.random.seed(2023)
torch.manual_seed(2023)
rng = np.random.default_rng(2023)
dev = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

class MultiLayerNet(nn.Module):
    def __init__(self, *neurons):
        super(MultiLayerNet, self).__init__()
        #### throw error if depth < 3 ####

        # self.depth = len(neurons)
        # input_dim = neurons[0]
        # output_dim = neurons[-1]
        # self.hidden_layers = []

        # self.first_layer = nn.Linear(input_dim, neurons[1])

        # for i in range(1, self.depth-2):
        #     exec(
        #         f'self.hidden_layer{i} = nn.Linear(neurons[{i}], neurons[{i+1}])'
        #     )
        #     self.hidden_layers.append(eval(f'self.hidden_layer{i}'))

        # self.last_layer = nn.Linear(neurons[-2], output_dim)
        self.linears = nn.ModuleList([nn.Linear(neurons[i-1], neurons[i]) for i in range(1, len(neurons))])

    def forward(self, x):
        # x = torch.tanh(self.first_layer(x))
        # for i in range(self.depth-3):
        #     x = torch.tanh(self.hidden_layers[i](x))
        # x = self.last_layer(x)
        for layer in self.linears:
            x = torch.tanh(layer(x))
        return x

class DeepEnergyMethod:
    def __init__(self, model, energy, dim):
        self.model = model.to(dev)
        self.energy = energy
        
    def train_model(self, data, dirichlet, neumann, LHD, lr=0.5, max_it=20, epochs=20):
        # data
        x = torch.from_numpy(data).float().to(dev)
        x.requires_grad_(True)
        optimizer = torch.optim.LBFGS(self.model.parameters(), lr=lr, max_iter=max_it)

        # boundary
        dirBC_coords = torch.from_numpy(dirichlet['coords']).float().to(dev)
        dirBC_coords.requires_grad_(True)
        dirBC_values = torch.from_numpy(dirichlet['values']).float().to(dev)

        neuBC_coords = torch.from_numpy(neumann['coords']).float().to(dev)
        neuBC_coords.requires_grad_(True)
        neuBC_values = torch.from_numpy(neumann['values']).float().to(dev)

        self.losses = {}
        start_time = time.time()
        for i in range(epochs):
            def closure():
                # internal loss
                u_pred = self.getU(self.model, x)
                u_pred.double()

                IntEnergy = self.energy(u_pred, x)
                internal_loss = LHD[0]*LHD[1]*LHD[2]*penalty(IntEnergy)

                # boundary loss
                dir_pred = self.getU(self.model, dirBC_coords)
                # print(torch.norm(dir_pred))
                bc_dir = LHD[1]*LHD[2]*loss_squared_sum(dir_pred, dirBC_values)
                boundary_loss = torch.sum(bc_dir)

                # external loss
                neu_pred = self.getU(self.model, neuBC_coords)
                bc_neu = torch.matmul((neu_pred + neuBC_coords).unsqueeze(1), neuBC_values.unsqueeze(2))
                external_loss = LHD[1]*LHD[2]*penalty(bc_neu)
                # print(neu_pred.shape, neuBC_coords.shape, neuBC_values.shape)
                # print(bc_neu.shape); exit()
                energy_loss = internal_loss - torch.sum(external_loss)
                loss = internal_loss - torch.sum(external_loss) + boundary_loss

                optimizer.zero_grad()
                loss.backward()
                
                if self.losses.get(i+1):
                    self.losses[i+1] += loss.item() / max_it
                else:
                    self.losses[i+1] = loss.item() / max_it

                #       + f'loss: {loss.item():10.5f}')
                print(f'Iter: {i+1:2d}, Energy: {energy_loss.item():10.5f}')
                return loss

            optimizer.step(closure)
        # return self.model

    def getU(self, model, x):
        u = model(x).to(dev)
        Ux, Uy, Uz = x[:, 0] * u.T.unsqueeze(1)
        u_pred = torch.cat((Ux.T, Uy.T, Uz.T), dim=-1)
        return u_pred

    def evaluate_model(self, x, y, z):
        Nx = len(x)
        Ny = len(y)
        Nz = len(z)
        xGrid, yGrid, zGrid = np.meshgrid(x, y, z)
        x1D = xGrid.flatten()
        y1D = yGrid.flatten()
        z1D = zGrid.flatten()
        xyz = np.concatenate((np.array([x1D]).T, np.array([y1D]).T, np.array([z1D]).T), axis=-1)
        xyz_tensor = torch.from_numpy(xyz).float().to(dev)
        xyz_tensor.requires_grad_(True)
        # u_pred_torch = self.model(xyz_tensor)
        u_pred_torch = self.getU(self.model, xyz_tensor)
        u_pred = u_pred_torch.detach().cpu().numpy()
        surUx = u_pred[:, 0].reshape(Ny, Nx, Nz)
        surUy = u_pred[:, 1].reshape(Ny, Nx, Nz)
        surUz = u_pred[:, 2].reshape(Ny, Nx, Nz)
        U = (np.float64(surUx), np.float64(surUy), np.float64(surUz))
        return U


def loss_squared_sum(input, target):
    return torch.sum((input - target)**2, dim=1) / input.shape[1]*input.data.nelement()

def penalty(input):
    return torch.sum(input) / input.data.nelement()