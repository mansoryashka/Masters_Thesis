import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import torch
from torch import nn
from torch.autograd import grad

<<<<<<< HEAD
=======
import matplotlib
matplotlib.rcParams['figure.dpi'] = 350
>>>>>>> 5631b203f55e0aad458a11e55ce16ca1b711e427

import sys
sys.path.insert(0, "../../3DBeam")
sys.path.insert(0, "../..")
<<<<<<< HEAD
sys.path.insert(0, "../problem1")
from DemBeam3D import DeepEnergyMethodBeam, train_and_evaluate, MultiLayerNet, write_vtk_v2, dev
from problem1 import energy
plt.style.use('default')
import matplotlib
matplotlib.rcParams['figure.dpi'] = 200
# C = 10E3
# bf = bt = bfs = 1

def define_domain(N=15, M=5):
    K = N
    num_duplicates = int(K/M)
    middle = int(np.floor(num_duplicates/2))
    assert N % M == 0, 'N must be divisible by M!'

    rs_endo = 7
    rl_endo = 17
    u_endo = np.linspace(-np.pi, -np.arccos(5/17), N)
    v_endo = np.linspace(-np.pi, np.pi, N)

    rs_epi = 10
    rl_epi = 20
    u_epi = np.linspace(-np.pi, -np.arccos(5/20), N)
    v_epi = np.linspace(-np.pi, np.pi, N)

    u = np.linspace(u_endo, u_epi, K)
    v = np.linspace(-np.pi, np.pi, N)
    rs = np.linspace(rs_endo, rs_epi, M)
    rl = np.linspace(rl_endo, rl_epi, M)

    RS = np.ones(N*K)
    RL = np.ones(N*K)
    for i in range(M):
        # print(f'fra: {int(N*K/M)*i} til: {int(N*K/M)*(i+1)-1}')
        RS[int(N*K/M)*i:int(N*K/M)*(i+1)] = rs[i]
        RL[int(N*K/M)*i:int(N*K/M)*(i+1)] = rl[i]


    x = RS*np.outer(np.cos(v), np.sin(u))
    y = RS*np.outer(np.sin(v), np.sin(u))
    z = RL*np.outer(np.ones(np.size(v)), np.cos(u))

    """ Finn ut hvorfor max(z) = 5.10!!! """
    # set z_max to 5
    z = np.where(np.abs(z - 5) < 0.1, 5, z)

    # define Dirichlet and Neumann BCs
    dir_BC = lambda z: np.abs(z - 5) < .5
    neu_BC = RS == rs_endo

    # define inner points
    # x0 = x[:, ~neu_BC]
    # y0 = y[:, ~neu_BC]
    # z0 = z[:, ~neu_BC]
    # x0 = x0[~dir_BC(z0)]
    # y0 = y0[~dir_BC(z0)]
    # z0 = z0[~dir_BC(z0)]
    x0 = np.copy(x)
    y0 = np.copy(y)
    z0 = np.copy(z)
    # print(x.shape)
    # define points on Dirichlet boundary
    x1 = x[dir_BC(z)]
    y1 = y[dir_BC(z)]
    z1 = z[dir_BC(z)]

    # define points on Neumann boundary
    x2 = x[:, neu_BC]
    y2 = y[:, neu_BC]
    z2 = z[:, neu_BC]
    # x2 = x2[~dir_BC(z2)]
    # y2 = y2[~dir_BC(z2)]
    # z2 = z2[~dir_BC(z2)]

    # define endocardium surface for illustration
    x_endo = rs_endo*np.outer(np.cos(v_endo), np.sin(u_endo))
    y_endo = rs_endo*np.outer(np.sin(v_endo), np.sin(u_endo))
    z_endo = rl_endo*np.outer(np.ones(np.size(v_endo)), np.cos(u_endo))

    # define epicardium surface for illustration
    x_epi = rs_epi*np.outer(np.cos(v_epi), np.sin(u_epi))
    y_epi = rs_epi*np.outer(np.sin(v_epi), np.sin(u_epi))
    z_epi = rl_epi*np.outer(np.ones(np.size(v_epi)), np.cos(u_epi))

    x_perp = np.copy(x_endo[:, :])
    y_perp = np.copy(y_endo[:, :])
    z_perp = np.copy(z_endo[:, :])
    # x_perp[1:, 0] = 0
    # y_perp[1:, 0] = 0
    # z_perp[1:, 0] = 0

    # define perpendicular surface
    # dx = -rs_endo*np.outer(
    #     np.sin(v_endo),
    #     np.sin(u_endo), 
    # )
    # dy = rs_endo*np.outer(
    #     np.sin(v_endo),
    #     np.cos(u_endo),
    # )
    # dz = -rl_endo*np.outer(
    #     np.ones(np.size(v_endo)),
    #     np.sin(u_endo),
    # )
 
    # x_perp = - dz * dy
    # y_perp = - dx * dz
    # z_perp = dx * dy


    # reshape to have access to different dimentsions
    # dimension 0 is angle
    # dimension 1 is depth layer
    # dimension 2 is which of N/M duplicate. try to use only middle duplicate or all
    # dimension 3 is vertical level
    # x0 = x0.reshape((N, M-1, int(K/M), N-1))[..., middle, :]
    # y0 = y0.reshape((N, M-1, int(K/M), N-1))[..., middle, :]
    # z0 = z0.reshape((N, M-1, int(K/M), N-1))[..., middle, :]
    x0 = x0.reshape((N, M, int(K/M), N))[..., middle, :]
    y0 = y0.reshape((N, M, int(K/M), N))[..., middle, :]
    z0 = z0.reshape((N, M, int(K/M), N))[..., middle, :]

    x1 = x1.reshape((N, M, int(K/M), 1))[..., middle, :]
    y1 = y1.reshape((N, M, int(K/M), 1))[..., middle, :]
    z1 = z1.reshape((N, M, int(K/M), 1))[..., middle, :]

    # x2 = x2.reshape((N, 1, int(K/M), N-1))[..., middle, :]
    # y2 = y2.reshape((N, 1, int(K/M), N-1))[..., middle, :]
    # z2 = z2.reshape((N, 1, int(K/M), N-1))[..., middle, :]
    x2 = x2.reshape((N, 1, int(K/M), N))[..., middle, :]
    y2 = y2.reshape((N, 1, int(K/M), N))[..., middle, :]
    z2 = z2.reshape((N, 1, int(K/M), N))[..., middle, :]

    # plot domain
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_aspect('equal')
    ax.scatter(x0, y0, z0, s=1, c='tab:blue', alpha=.1)
    ax.scatter(x1, y1, z1, s=2, c='tab:green')
    ax.scatter(x2, y2, z2, s=2, c='tab:red')
    # plot epicardial and endocardial surfaces
    ax.plot_surface(x_endo, y_endo, z_endo, cmap='autumn', alpha=.1)
    ax.plot_surface(x_epi, y_epi, z_epi, cmap='autumn', alpha=.1)
    # ax.scatter(dx, dy, dz)
    # ax.scatter(x_perp, y_perp, z_perp)
    # ax.quiver(x_endo[:, :-1], y_endo[:, :-1], z_endo[:, :-1], x_perp, y_perp, z_perp, alpha=.1)

    # plt.show()
    plt.savefig('ventricle.pdf')


    x0 = np.expand_dims(x0.flatten(), 1)
    y0 = np.expand_dims(y0.flatten(), 1)
    z0 = np.expand_dims(z0.flatten(), 1)
    domain = np.concatenate((x0, y0, z0), -1)

    x1 = np.expand_dims(x1.flatten(), 1)
    y1 = np.expand_dims(y1.flatten(), 1)
    z1 = np.expand_dims(z1.flatten(), 1)
    d_cond = 5
    db_pts = np.concatenate((x0, y0, z0), -1)
    db_vals = np.ones(np.shape(db_pts)) * d_cond

    x_perp = np.expand_dims(x_perp.flatten(), 1)
    y_perp = np.expand_dims(y_perp.flatten(), 1)
    z_perp = np.expand_dims(z_perp.flatten(), 1)

    n_cond = np.concatenate((x_perp, y_perp, z_perp), -1)

    x2 = np.expand_dims(x2.flatten(), 1)
    y2 = np.expand_dims(y2.flatten(), 1)
    z2 = np.expand_dims(z2.flatten(), 1)
    nb_pts = np.concatenate((x2, y2, z2), -1)
    nb_vals = n_cond

    dirichlet = {
        'coords': db_pts,
        'values': db_vals
    }

    neumann = {
        'coords': nb_pts,
        'values': nb_vals
    }

    return domain, dirichlet, neumann

class DeepEnergyMethodLV(DeepEnergyMethodBeam):
    def getU(self, model, x):
        u = model(x).to(dev)
        Ux, Uy, Uz = (x[:, 2] - 5) * u.T.unsqueeze(1)
        u_pred = torch.cat((Ux.T, Uy.T, Uz.T), dim=-1)
        return u_pred
    
    def evaluate_model(self, x, y, z, return_pred_tensor=False):
        Nx = len(x)
        Ny = len(y)
        Nz = len(z)

        x1D = np.expand_dims(x.flatten(), 1)
        y1D = np.expand_dims(y.flatten(), 1)
        z1D = np.expand_dims(z.flatten(), 1)
        xyz = np.concatenate((x1D, y1D, z1D), axis=-1)

        xyz_tensor = torch.from_numpy(xyz).float().to(dev)
        xyz_tensor.requires_grad_(True)

        u_pred_torch = self.getU(self.model, xyz_tensor)
        u_pred = u_pred_torch.detach().cpu().numpy()
        surUx = u_pred[:, 0].reshape(Ny, Nx, Nz)
        surUy = u_pred[:, 1].reshape(Ny, Nx, Nz)
        surUz = u_pred[:, 2].reshape(Ny, Nx, Nz)

        U = (np.float64(surUx), np.float64(surUy), np.float64(surUz))
        return U

if __name__ == '__main__':
    rs_endo = 7
    rl_endo = 17
    rs_epi = 10
    rl_epi = 20
    N = 8; M = 2
    domain, dirichlet, neumann = define_domain(N, M)
    shape = [N, N, M]
    LHD = [rs_epi-rs_endo, rs_epi-rs_endo, rl_epi-rl_endo]
    model = MultiLayerNet(3, 40, 40, 40, 3)
    DemLV = DeepEnergyMethodLV(model, energy)
    DemLV.train_model(domain, dirichlet, neumann, shape=shape, LHD=LHD, lr=.5, epochs=2, fb=np.array([[0, 0, 0]]))

    K = N
    rs_endo = 7
    rl_endo = 17
    u_endo = np.linspace(-np.pi, -np.arccos(5/17), N)
    v_endo = np.linspace(-np.pi, np.pi, N)

    rs_epi = 10
    rl_epi = 20
    u_epi = np.linspace(-np.pi, -np.arccos(5/20), N)
    v_epi = np.linspace(-np.pi, np.pi, N)

    u = np.linspace(u_endo, u_epi, K)
    v = np.linspace(-np.pi, np.pi, N)
    rs = np.linspace(rs_endo, rs_epi, M)
    rl = np.linspace(rl_endo, rl_epi, M)

    RS = np.ones(N*K)
    RL = np.ones(N*K)
    for i in range(M):
        # print(f'fra: {int(N*K/M)*i} til: {int(N*K/M)*(i+1)-1}')
        RS[int(N*K/M)*i:int(N*K/M)*(i+1)] = rs[i]
        RL[int(N*K/M)*i:int(N*K/M)*(i+1)] = rl[i]


    x = RS*np.outer(np.cos(v), np.sin(u))
    y = RS*np.outer(np.sin(v), np.sin(u))
    z = RL*np.outer(np.ones(np.size(v)), np.cos(u))

    U_pred = DemLV.evaluate_model(x, y, z)
    write_vtk_v2('output/DemLV', x, y, z, U_pred)