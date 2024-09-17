import numpy as np 
import matplotlib.pyplot as plt 
from pathlib import Path
import torch

import seaborn as sns
sns.set()

from matplotlib.patches import Rectangle

import sys
from problem1 import C, bf, bt, bfs
sys.path.insert(0, "../..")
from DEM import MultiLayerNet, write_vtk_v2, models_path, arrays_path
from EnergyModels import GuccioneTransverseEnergyModel
sys.path.insert(0, "../../3Dbeam")
from DemBeam import DeepEnergyMethodBeam

import matplotlib
matplotlib.rcParams['figure.dpi'] = 150

if __name__ == '__main__':
    L = 10; H = 1; D = 1

    N = 50
    N_test = 10
    middle = int(np.floor(5*N_test))
    middle_z = int(np.floor(N_test))
    x_test = np.linspace(0, L, 10*N_test+1)
    y_test = np.linspace(0, H, N_test+1)
    z_test = np.linspace(0, D, N_test+1)
    U_pred = np.load(f'stored_arrays/U_pred{N}.npy')
    
    model = MultiLayerNet(3, 40, 40, 40, 3)
    energy = GuccioneTransverseEnergyModel(C, bf, bt, bfs)
    DemBeam = DeepEnergyMethodBeam(model, energy)
    DemBeam.model.load_state_dict(torch.load(Path('trained_models') / 'run1' / 'model1'))
    # U_pred = DemBeam.evaluate_model(x_test, y_test, z_test)
    X, Y, Z = np.meshgrid(x_test, y_test, z_test)
    X_cur, Y_cur, Z_cur = X + U_pred[0], Y + U_pred[1], Z + U_pred[2]

    pts_x = np.zeros((10, 3))
    pts_x_cur = np.zeros((10, 3))
    pts_y = np.zeros((10, 3))
    pts_y_cur = np.zeros((10, 3))
    pts_z = np.zeros((10, 3))
    pts_z_cur = np.zeros((10, 3))

    for i in range(10):
        condition1 = np.logical_and(np.logical_and(Z==0.5, Y==0.5), X==i)
        pts_x[i] = X[condition1][0], Y[condition1][0], Z[condition1][0]
        pts_x_cur[i] = X_cur[condition1][0], Y_cur[condition1][0], Z_cur[condition1][0]

        condition2 = np.logical_and(np.logical_and(Z==0.5, Y==0.9), X==i)
        pts_y[i] = X[condition2][0], Y[condition2][0], Z[condition2][0]
        pts_y_cur[i] = X_cur[condition2][0], Y_cur[condition2][0], Z_cur[condition2][0]

        condition3 = np.logical_and(np.logical_and(Z==0.9, Y==0.5), X==i)
        pts_z[i] = X[condition3][0], Y[condition3][0], Z[condition3][0]
        pts_z_cur[i] = X_cur[condition3][0], Y_cur[condition3][0], Z_cur[condition3][0]

    condition4 = np.logical_and(Y==0.5, Z==0.5)
    line_x, line_y, line_z = X[condition4], Y[condition4], Z[condition4]
    line_x_cur, line_y_cur, line_z_cur = X_cur[condition4], Y_cur[condition4], Z_cur[condition4]

    condition5 = np.logical_and(np.logical_and(X==10, Y==0.5), Z==1)
    end_x, end_y, end_z = X[condition5], Y[condition5], Z[condition5]
    end_x_cur, end_y_cur, end_z_cur = X_cur[condition5], Y_cur[condition5], Z_cur[condition5]

    strain_x = (np.linalg.norm(pts_x_cur[:-1] - pts_x_cur[1:], axis=1)
                / np.linalg.norm(pts_x[:-1] - pts_x[1:], axis=1)
                - 1) * 100
    strain_y = (np.linalg.norm(pts_x_cur - pts_y_cur, axis=1)
                / np.linalg.norm(pts_x - pts_y, axis=1)
                - 1) * 100
    strain_z = (np.linalg.norm(pts_x_cur - pts_z_cur, axis=1)
                / np.linalg.norm(pts_x - pts_z, axis=1)
                - 1) * 100
    
    fig, ax = plt.subplots(1, 3, figsize=(13, 5))
    # fig.tight_layout()
    ax[0].plot(strain_x, '-x')
    ax[0].set_ylabel('strain [%]')
    ax[0].set_title('$x$-axis')
    ax[0].set_xticks(np.arange(9))
    ax[0].set_xticklabels(['p1', '', 'p3', '', 'p5', '', 'p7', '', 'p9'])

    ax[1].plot(strain_y, '-x')
    ax[1].set_title('$y$-axis')
    ax[1].set_xticks(np.arange(10))
    ax[1].set_xticklabels(['p1', '', 'p3', '', 'p5', '', 'p7', '', 'p9', ''])

    ax[2].plot(strain_z, '-x')
    ax[2].set_title('$z$-axis')
    ax[2].set_xticks(np.arange(10))
    ax[2].set_xticklabels(['p1', '', 'p3', '', 'p5', '', 'p7', '', 'p9', ''])
    fig.savefig(f'figures/strain_plot{N}.pdf')
    plt.show()


    fig = plt.figure(figsize=(14, 8))
    plt.style.use('seaborn-v0_8-darkgrid')
    ax11 = plt.subplot2grid((2,3), (0,0), colspan=3, rowspan=1)
    ax12 = plt.subplot2grid((2,3), (1,0))
    ax13 = plt.subplot2grid((2,3), (1,1))
    ax14 = plt.subplot2grid((2,3), (1,2))

    u_pred_fem = np.load('stored_arrays/u_predFEM.npy')
    X_fem, Y_fem, Z_fem = X + u_pred_fem[0], Y + u_pred_fem[1], Z + u_pred_fem[2]
    line_x_fem, line_z_fem = X_fem[condition4], Z_fem[condition4]
    ax11.plot(line_x_fem, line_z_fem, label='FEM')


    # ax11.set_xlabel('$x$ [mm]')
    # ax11.set_ylabel('$z$ [mm]')
    # fig.savefig(f'figures/line_plot{N}.pdf')
    p1 = 5; p2 = -5

    ax11.plot(line_x_cur, line_z_cur, # c=colors[i],
             linestyle='--', linewidth=0.8, 
             alpha=0.9, label=f'N = {N}')
    ax12.plot(line_x_cur[:p1], line_z_cur[:p1], # c=colors[i],
             linestyle='--', linewidth=0.8, 
             alpha=0.9, label=f'N = {N}')
    ax13.plot(line_x_cur[middle-2:middle+3], line_z_cur[middle-2:middle+3], # c=colors[i],
             linestyle='--', linewidth=0.8, 
             alpha=0.9, label=f'N = {N}')
    ax14.plot(line_x_cur[p2:], line_z_cur[p2:], # c=colors[i],
             linestyle='--', linewidth=0.8, 
             alpha=0.9, label=f'N = {N}')
    
    y1_fem = line_z_cur
    x1_fem = line_x_cur

    ax11.set_xlabel('$x$ [m]')
    ax11.set_ylabel('$z$-deflection [m]')
    ax11.legend()

    ax12.set_xlabel('$x$ [m]')
    ax12.set_ylabel('$z$-deflection [m]')
    ax12.set_ylim(top=y1_fem[p1-1])
    ax12.set_xlim(right=x1_fem[p1-1])

    ticks1 = ax12.get_yticks()
    ax12.set_yticks([ticks1[0], ticks1[-1]])
    ax12.set_yticklabels([f'{x:.3f}' for x in [ticks1[0], ticks1[-1]]])

    ax13.set_ylim((y1_fem[middle-2], y1_fem[middle+2]))
    ax13.set_xlim((x1_fem[middle-2], x1_fem[middle+2]))
    ax13.set_xlabel('$x$ [m]')

    ticks1 = ax13.get_yticks()
    ax13.set_yticks([ticks1[0], ticks1[-1]])
    ax13.set_yticklabels([f'{x:.3f}' for x in [ticks1[0], ticks1[-1]]])

    ax14.set_ylim(bottom=y1_fem[p2])
    ax14.set_xlim(left=x1_fem[p2])
    ax14.set_xlabel('$x$ [m]')
    
    ticks1 = ax14.get_yticks()
    ax14.set_yticks([ticks1[0], ticks1[-1]])
    ax14.set_yticklabels([f'{x:.3f}' for x in [ticks1[0], ticks1[-1]]])

    patch1_limx = ax12.get_xlim()
    patch1_limy = ax12.get_ylim()

    patch2_limx = ax13.get_xlim()
    patch2_limy = ax13.get_ylim()

    patch3_limx = ax14.get_xlim()
    patch3_limy = ax14.get_ylim()

    ax11.add_patch(Rectangle([patch1_limx[0], patch1_limy[0]], 
                             patch1_limx[1] - patch1_limx[0], 
                             patch1_limy[1] - patch1_limy[0],
                             facecolor='None', edgecolor='tab:blue',
                             linestyle='--'
                             ))
    ax12.add_patch(Rectangle([patch1_limx[0], patch1_limy[0]], 
                             patch1_limx[1] - patch1_limx[0], 
                             patch1_limy[1] - patch1_limy[0],
                             facecolor='None', edgecolor='tab:blue',
                             linestyle='--', linewidth=3
                             ))
    
    ax11.add_patch(Rectangle([patch2_limx[0], patch2_limy[0]], 
                             patch2_limx[1] - patch2_limx[0], 
                             patch2_limy[1] - patch2_limy[0],
                             facecolor='None', edgecolor='tab:green',
                             linestyle='--'
                             ))
    ax13.add_patch(Rectangle([patch2_limx[0], patch2_limy[0]], 
                             patch2_limx[1] - patch2_limx[0], 
                             patch2_limy[1] - patch2_limy[0],
                             facecolor='None', edgecolor='tab:green',
                             linestyle='--', linewidth=3
                             ))

    ax11.add_patch(Rectangle([patch3_limx[0], patch3_limy[0]], 
                             patch3_limx[1] - patch3_limx[0], 
                             patch3_limy[1] - patch3_limy[0],
                             facecolor='None', edgecolor='tab:red',
                             linestyle='--'
                             ))
    ax14.add_patch(Rectangle([patch3_limx[0], patch3_limy[0]], 
                             patch3_limx[1] - patch3_limx[0], 
                             patch3_limy[1] - patch3_limy[0],
                             facecolor='None', edgecolor='tab:red',
                             linestyle='--', linewidth=3
                             ))

    plt.show()