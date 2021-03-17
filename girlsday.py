import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import astropy.units as u
#from astropy.cosmology import Planck15
import matplotlib.colors as colors
from scipy.optimize import curve_fit
import scipy.integrate as integrate
import numpy.random
from numpy.linalg import det
from mpl_toolkits import mplot3d
import matplotlib.ticker as ticker
from tqdm import tqdm

plt.rc('font', family='serif')
mpl.rcParams['ytick.labelsize'] = 24
mpl.rcParams['xtick.labelsize'] = 24
mpl.rcParams['axes.labelsize'] = 34
mpl.rcParams['legend.fontsize'] = 24
def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)
    return r'${}\!\times 10^{{{}}}$'.format(a, b)

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets


import sys, platform, os
import camb
from camb import model, initialpower


import warnings
warnings.filterwarnings('ignore')


pbar = tqdm(total=5)

########################## PART 1 #############################################################

#define plotting routines
def plotEarth(earthMapMoll):
    fig = plt.figure(figsize=(16,16))
    ax = fig.add_subplot(111)

    #plotting map
    im = ax.imshow(earthMapMoll,vmin=-8000, vmax=6705, cmap='gist_earth')
    
    #setting position and size of colorbar (xPos,yPos,width,height)
    cax = fig.add_axes([0.32, 0.25, 0.4, 0.018]) 
    cbar = fig.colorbar(im,orientation="horizontal",cax=cax)
    cbar.set_label('Höhe über N.N. [m]', size=24, labelpad=20)
    ax.axis('off')
        
def plotEarth3d(earthMapMoll,earth3d):
    
    fig = plt.figure(figsize=(18,16))
    gs = fig.add_gridspec(1, 2,width_ratios=[1,4])

    #ax1 = fig.add_subplot(gs[0,0], projection=ccrs.Orthographic(10, 37))
    #ax1.gridlines(color='#333333', linestyle='dotted')
    #ax1.imshow(earthMapCartview, origin="upper", extent=(-180, 180, -90, 90),
    #      transform=ccrs.PlateCarree(),cmap='gist_earth',
    #           vmin=-8000, vmax=6705) 
    ax1 = fig.add_subplot(gs[0,0])
    ax1.imshow(earth3d) 
    ax1.axis('off')

    #plotting map
    ax2 = fig.add_subplot(gs[0,1])
    im = ax2.imshow(earthMapMoll,cmap='gist_earth',vmin=-8000, vmax=6705)
   
    #setting position and size of colorbar (xPos,yPos,width,height)
    cax = fig.add_axes([0.41, 0.3, 0.4, 0.018]) 
    cbar = fig.colorbar(im,orientation="horizontal",cax=cax)
    cbar.set_label('Höhe über N.N. [m]', size=24, labelpad=20)
    ax2.axis('off')

def plotPowerspectrum(clCur,LMAX,isCMB=False):    
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)

    #split the ell and cl arrays it two halfes 
    # s.t. they can be plotted in two different plot styles 
    ellLeq = ell[ell<=LMAX]
    clDimlessLeq = ellLeq* (ellLeq + 1) * clCur[ell<=LMAX]
    ellGeq = ell[ell>=LMAX]
    clDimlessGeq = ellGeq * (ellGeq + 1) * clCur[ell>=LMAX]
    
    #plot the C_l power spectrum
    ax.plot(ellLeq, clDimlessLeq, c="#222222", lw=1.5)
    ax.plot(ellGeq, clDimlessGeq, c="#666666", lw=1.5)
    
    # add the vertical line and shaded region
    ax.axvline(x=LMAX,lw=2)
    xLim = np.array(ax.get_xlim())    
    xLim[1] = 210
    if (isCMB):
        xLim[1] = 1024

    ax.axvspan(LMAX, xLim[1], facecolor='0.2', alpha=0.2)

    # plot cosmetics
    if (not isCMB):
        ax.set_xscale("log")
    ax.set_xlim(xLim)
    ax.set_xlabel(r"$\ell$", size=24)
    if (not isCMB):
        ax.set_yscale("log")
    ax.set_ylabel(r"$\ell(\ell+1)C_{\ell}$", size=24)

    plt.title("Leistungsspektrum $C_{\ell}$",fontsize=24)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    ax.grid(True)


mollview = np.loadtxt("mollviewEarth.dat")
#cartview = np.loadtxt("cartviewEarth.dat")
earth3d = plt.imread('./Earth.png')

pbar.update(1)

########################## PART 2 #############################################################


LMAX = 1024
cl = np.loadtxt("data/clEarth.dat")
ell = np.arange(len(cl))


def plotAlmMap (LMAX):
    mollviewMapReconstr = np.loadtxt("data/mollviewEarth_recon_max%d.dat"%LMAX)
    plotEarth(mollviewMapReconstr)
    plotPowerspectrum(cl,LMAX)


int_wdgt = widgets.IntSlider(
    description=r'$\ell_\text{max}$:',
    fontsize=34,
    value=1,
    min=1, max=200, step=15,
    layout=widgets.Layout(width='90%'))

pbar.update(1)

########################## PART 3 #############################################################


#number of $\ell$-modes that are to be plotted in the triangular plot
#CAUTION: plot below has been formatted according to maxL = 8; 
#         maxL can be changed but then plot has to be reformatted 
maxL = 8



#DELETE mapArray = np.load("data/mapArray.npy")

mapCur = np.loadtxt("data/triangular00.dat")
shapeSummedMaps = np.append(maxL,np.shape(mapCur))
summedMaps = np.zeros(shapeSummedMaps)

#formatting paramters that need to be adjusted if maxL is changed
leftMarginEll       = -700 
leftMarginM         = 150
topMargMfirst       = -140
topMargMfollow      = 160

#triangular plot
def triangularPlot ():
    fig, axes = plt.subplots(figsize=(13, 13), sharex=True, sharey=True, ncols=maxL+1, nrows=maxL)
    fig.subplots_adjust(hspace = -0.8)
    mapCur = np.loadtxt("data/triangular00.dat")

    shapeMapArray = np.append([maxL,maxL],np.shape(mapCur))
    mapArray = np.zeros(shapeMapArray)

    pbarTriang = tqdm(total=maxL+1, position=0, leave=True)
    for i in range(maxL):
        summedMapsCur = np.zeros_like(mapCur)
        for j in range(maxL):
            if i<j:
                if(i==0):
                    axes[i, j].text(leftMarginM,topMargMfollow,"$m=%d$"%j,size=18)
                axes[i, j].axis('off')
            else:
                mapCur = np.loadtxt("data/triangular%d%d.dat"%(i,j)) 
                if(i==0):
                    axes[i, j].text(leftMarginM,topMargMfirst,"$m=%d$"%j,size=18)
                axes[i, j].imshow(mapCur,cmap="gist_earth")
                axes[i, j].axis('off')
                if(j==0):
                    axes[i, j].text(leftMarginEll,230,"$\ell=%d$:"%i,size=18)
                mapArray[i,j] = mapCur
        pbarTriang.update(1)
        
        
    axes[0, maxL].text(leftMarginM,topMargMfirst,r"$\Sigma_{\ell\leq\ell_{cur},m(\ell)}$",size=18)
    for curL in range(maxL):
        curSummedMap = np.zeros_like(mapArray[0,0])
        for j in range(curL+1):
            curSummedMap += np.sum(mapArray[j],axis=0)
        
        axes[curL, maxL].imshow(curSummedMap,cmap='gist_earth')
        axes[curL, maxL].axis('off')


pbar.update(1)


## Martina's 1st part

check_l0 = widgets.Checkbox(
    value=True,
    description='l=0',
    disabled=False,
    indent=False
)
check_l1 = widgets.Checkbox(
    value=False,
    description='l=1',
    disabled=False,
    indent=False
)
check_l2 = widgets.Checkbox(
    value=False,
    description='l=2',
    disabled=False,
    indent=False
)
check_l3 = widgets.Checkbox(
    value=False,
    description='l=3',
    disabled=False,
    indent=False
)
check_l4 = widgets.Checkbox(
    value=False,
    description='l=4',
    disabled=False,
    indent=False
)

def superpose_spherical_harmonics(l0, l1, l2, l3, l4):
    map00 = np.loadtxt("data/triangular00.dat")
    superposition = np.zeros_like(map00)
    if l0:
        superposition += map00
    if l1:
        m10 = np.loadtxt("data/triangular10.dat")
        m11 = np.loadtxt("data/triangular11.dat")
        superposition += m10+m11
    if l2:
        m20 = np.loadtxt("data/triangular20.dat")
        m21 = np.loadtxt("data/triangular21.dat")
        m22 = np.loadtxt("data/triangular22.dat")
        superposition += m20+m21+m22
    if l3:
        m30 = np.loadtxt("data/triangular30.dat")
        m31 = np.loadtxt("data/triangular31.dat")
        m32 = np.loadtxt("data/triangular32.dat")
        m33 = np.loadtxt("data/triangular33.dat")
        superposition += m30+m31+m32+m33
    if l4:
        m40 = np.loadtxt("data/triangular40.dat")
        m41 = np.loadtxt("data/triangular41.dat")
        m42 = np.loadtxt("data/triangular42.dat")
        m43 = np.loadtxt("data/triangular43.dat")
        m44 = np.loadtxt("data/triangular44.dat")
        superposition += m40+m41+m42+m43+m44
    plotEarth(superposition)


out1 = widgets.interactive_output(superpose_spherical_harmonics, {'l0':check_l0,'l1':check_l1, 'l2':check_l2, 'l3':check_l3, 'l4':check_l4})


## Martina's 2nd part

check_l0 = widgets.Checkbox(
    value=True,
    description='l=0',
    disabled=False,
    indent=False
)
check_l1m0 = widgets.Checkbox(
    value=False,
    description='l=1, m=0',
    disabled=False,
    indent=False
)
check_l1m1 = widgets.Checkbox(
    value=False,
    description='l=1, m=1',
    disabled=False,
    indent=False
)
check_l2m0 = widgets.Checkbox(
    value=False,
    description='l=2, m=0',
    disabled=False,
    indent=False
)
check_l2m1 = widgets.Checkbox(
    value=False,
    description='l=2, m=1',
    disabled=False,
    indent=False
)
check_l2m2 = widgets.Checkbox(
    value=False,
    description='l=2, m=2',
    disabled=False,
    indent=False
)
check_l3m0 = widgets.Checkbox(
    value=False,
    description='l=3, m=0',
    disabled=False,
    indent=False
)
check_l3m1 = widgets.Checkbox(
    value=False,
    description='l=3, m=1',
    disabled=False,
    indent=False
)
check_l3m2 = widgets.Checkbox(
    value=False,
    description='l=3, m=2',
    disabled=False,
    indent=False
)
check_l3m3 = widgets.Checkbox(
    value=False,
    description='l=3, m=3',
    disabled=False,
    indent=False
)

def superpose_spherical_harmonics(l0, l1m0, l1m1, l2m0, l2m1, l2m2, l3m0,l3m1,l3m2,l3m3):
    map00 = np.loadtxt("data/triangular00.dat")
    superposition = np.zeros_like(map00)
    if l0:
        superposition += map00
    if l1m0:
        superposition += np.loadtxt("data/triangular10.dat") 
    if l1m1:
        superposition += np.loadtxt("data/triangular11.dat")
    if l2m0:
        superposition += np.loadtxt("data/triangular20.dat")
    if l2m1:
        superposition += np.loadtxt("data/triangular21.dat")
    if l2m2:
        superposition += np.loadtxt("data/triangular22.dat")
    if l3m0:
        superposition += np.loadtxt("data/triangular30.dat")
    if l3m1:
        superposition += np.loadtxt("data/triangular31.dat")
    if l3m2:
        superposition += np.loadtxt("data/triangular32.dat")
    if l3m3:
        superposition += np.loadtxt("data/triangular33.dat")
    plotEarth(superposition)


out2 = widgets.interactive_output(superpose_spherical_harmonics, {'l0':check_l0,'l1m0':check_l1m0,'l1m1':check_l1m1,'l2m0':check_l2m0,'l2m1':check_l2m1,'l2m2':check_l2m2, 'l3m0':check_l3m0, 'l3m1':check_l3m1, 'l3m2':check_l3m2, 'l3m3':check_l3m3})




########################## PART 4 #############################################################


#define plotting routines for CMB

def plotCMB(cmbMap):
    fig = plt.figure(figsize=(16,16))
    ax = fig.add_subplot(111)

    #plotting map
    im = ax.imshow(cmbMap,vmin=-0.0005, vmax=0.0005)
    
    #setting position and size of colorbar (xPos,yPos,width,height)
    cax = fig.add_axes([0.32, 0.25, 0.4, 0.018]) 
    cbar = fig.colorbar(im,orientation="horizontal",cax=cax)
    cbar.set_label('$\Delta T$', size=24, labelpad=20)
    ax.axis('off')


    
def plotCMB3d(cmbMap,cmb3d):
        
    fig = plt.figure(figsize=(18,16))
    gs = fig.add_gridspec(1, 2,width_ratios=[1,4])

    ax1 = fig.add_subplot(gs[0,0])
    ax1.imshow(cmb3d) 
    ax1.axis('off')

    #plotting map
    ax2 = fig.add_subplot(gs[0,1])
    im = ax2.imshow(cmbMap,vmin=-0.0005, vmax=0.0005)
       
    #setting position and size of colorbar (xPos,yPos,width,height)
    cax = fig.add_axes([0.41, 0.3, 0.4, 0.018]) 
    cbar = fig.colorbar(im,orientation="horizontal",cax=cax)
    cbar.set_label('$\Delta T$', size=24, labelpad=20)
    ax2.axis('off')

CMBmollview = np.loadtxt("data/CMBmollview.dat")
cmb3d   = plt.imread('./CMB3d_1.png')

LMAX = 1024
clCMB = np.loadtxt("data/clCMB.dat")
ellCMB = np.arange(len(clCMB))[2:]


def plotPowerspectrumCMB(clCur,LMAX,isCMB=False):    
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)

    #split the ell and cl arrays it two halfes 
    # s.t. they can be plotted in two different plot styles 
    ellLeq = ellCMB[ellCMB<=LMAX]
    clDimlessLeq = ellLeq* (ellLeq + 1) * clCur[ellCMB<=LMAX]
    ellGeq = ellCMB[ellCMB>=LMAX]
    clDimlessGeq = ellGeq * (ellGeq + 1) * clCur[ellCMB>=LMAX]
    
    #plot the C_l power spectrum
    ax.plot(ellLeq, clDimlessLeq, c="#222222", lw=1.5)
    ax.plot(ellGeq, clDimlessGeq, c="#666666", lw=1.5)
    
    # add the vertical line and shaded region
    ax.axvline(x=LMAX,lw=2)
    xLim = np.array(ax.get_xlim())    
    xLim[1] = 210
    if (isCMB):
        xLim[1] = 1024

    ax.axvspan(LMAX, xLim[1], facecolor='0.2', alpha=0.2)

    # plot cosmetics
    if (not isCMB):
        ax.set_xscale("log")
    ax.set_xlim(xLim)
    ax.set_xlabel(r"$\ell$", size=24)
    if (not isCMB):
        ax.set_yscale("log")
    ax.set_ylabel(r"$\ell(\ell+1)C_{\ell}$", size=24)

    plt.title("Leistungsspektrum $C_{\ell}$",fontsize=24)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    ax.grid(True)

def plotAlmMapCMB (LMAX):
    mollviewMapReconstr = np.loadtxt("data/mollviewCMB_recon_max%d.dat"%LMAX)
    plotCMB(mollviewMapReconstr)
    plotPowerspectrumCMB(clCMB[2:],LMAX,True)

int_wdgtCMB = widgets.IntSlider(
    description=r'$\ell_\text{max}$:',
    fontsize=34,
    value=116,
    min=1, max=200, step=15,
    layout=widgets.Layout(width='90%'))

pbar.update(1)

########################## PART 4 #############################################################

#Set up a new set of parameters for CAMB
pars = camb.CAMBparams()
#This function sets up CosmoMC-like settings, with one massive neutrino and helium set using BBN consistency
pars.set_cosmology(H0=67.5, ombh2=0.022, omch2=0.122, mnu=0.06, omk=0, tau=0.06)
pars.InitPower.set_params(As=2e-9, ns=0.965, r=0)
pars.set_for_lmax(2500, lens_potential_accuracy=0);

results = camb.get_results(pars)
powers =results.get_cmb_power_spectra(pars, CMB_unit='muK')
totCL_fiducial=powers['total']
ls = np.arange(totCL_fiducial.shape[0])

def createCldata (oBar):
    pars = camb.CAMBparams()
    #This function sets up CosmoMC-like settings, with one massive neutrino and helium set using BBN consistency
    pars.set_cosmology(H0=67.5, ombh2=oBar, omch2=0.122, mnu=0.06, omk=0, tau=0.06)
    pars.InitPower.set_params(As=2e-9, ns=0.965, r=0)
    pars.set_for_lmax(2500, lens_potential_accuracy=0);

    results = camb.get_results(pars)
    powers =results.get_cmb_power_spectra(pars, CMB_unit='muK')
    totCL_new=powers['total']
    ls = np.arange(totCL.shape[0])    

    np.savetxt("data/Cl_%.3f.dat"%oBar,(ls,totCL_new[:,0]))

def plotCMBps (oBarPercent):
    
    
    oBar = oBarPercent/100.
    ls,clCur = np.loadtxt("data/Cl_%.3f.dat"%oBar)

    #print(clCur)
    
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)

    startI = 10
    ax.plot(ls[startI:],totCL_fiducial[startI:], color='k')
    ax.plot(ls[startI:],clCur[startI:], color='#2966a3')
    ax.set_xlim([0,2500])
    ax.set_ylim([0,15000])
    barPercent = oBar*100
    ax.text(1750,13000,"Atome: %.1f%%"%barPercent,size=28,color='#2966a3')
    ax.text(1750,11800,"Atome: 2.2%",size=28,color='k')

    
def checkData(minObar,maxObar,stepSize):
    oBar = minObar
    while oBar < maxObar:
        fileExists = os.path.isfile("data/Cl_%.3f.dat"%oBar)
        if(not fileExists):
            createCldata(oBar)
        oBar += stepSize

pbar.update(1)


# set parameters fro slider widget        
minObar = 0.002
maxObar = 0.2
stepSize = 0.01

#check if all necessary files are available
#create them if necessary
checkData(minObar,maxObar,stepSize)

#loadFiducial data
ls,totCL_fiducial = np.loadtxt("data/Cl_0.022.dat")

int_wdgtPowerSpec = widgets.FloatSlider(
    description=r'Atome [in %]:',
    fontsize=34,
    value=minObar,
    min=minObar*100, max=maxObar*100, step=stepSize*100,
    layout=widgets.Layout(width='90%'))


