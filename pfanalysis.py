import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter
import streamlit as st
import pydicom as pdm

#st.set_page_config(layout="wide")

@st.cache_data
def load_image(f):
    pass
    f_dcm= pdm.dcmread(f)
    return f_dcm,(f_dcm.pixel_array*f_dcm.RescaleSlope +f_dcm.RescaleIntercept)

profile=[]
def peak_finder(profile):
  peaks =[]

  for i in range(len(profile)):

    if i==0 | i ==len(profile)-1:
      continue

    elif profile[i] ==0:

      continue


    else:
      if profile[i-1]<profile[i] >=profile[i+1]:

       peaks.append(i)
  return peaks


def bkgsubtracted(dframe,percent):
  bkgsubtracted =dframe-np.percentile(dframe,percent)
  bkgsubtracted = bkgsubtracted[bkgsubtracted>0]
  bkgsubtracted.fillna(0,inplace=True)
  return bkgsubtracted

def peaks(bkgsub):
  peaks= []
  leng =[]
  for i in range(round(0.1*bkgsub.shape[0]),round(0.9*bkgsub.shape[0]),2):
    peak_loc=peak_finder(bkgsub.iloc[:,i].values)

    leng.append(len(peak_loc))
    peaks.append(peak_loc)
  leng= pd.Series(leng)
  no_of_peaks=(leng[leng !=0]).mode().values[0]
  peakpositions = np.array([j[:no_of_peaks] for j in peaks if len(j)==no_of_peaks])
  return (pd.DataFrame(peakpositions).mode(axis=0))







dcmfile= st.file_uploader("Upload the Measured EPID response DICOM File here ",type =["dcm"])

col1,col2 = st.columns([1,1])

if dcmfile is not None:

    with col1:
      dcm,epidim = load_image(dcmfile)
    
      

    
    
      fig,ax = plt.subplots()
    
      
      plt.style.use("bmh")

      ps = 1000*dcm.ImagePlanePixelSpacing[0]/dcm.RTImageSID
      
      
      col=dcm.BeamLimitingDeviceAngle
      percent=95
      bkgsub = bkgsubtracted(pd.DataFrame(epidim),percent)
      if (col==0) or (col==180) :
          bkgsub = bkgsubtracted(pd.DataFrame(epidim.T),percent)
          # does transpose conserve the directions wrt to which we are numbering the pixels

      p=peaks(bkgsub)
 
      ax.imshow(epidim,cmap="jet")
    
      ax.set_xlabel("Pixels along X direction")
      ax.set_ylabel("Pixels along Y direction")
      ax.grid(False)
      ax.set_aspect(1.19)
      st.pyplot(fig)

      

      
      dictionary = {
        "Size of image (pixels)": f"{epidim.shape[0]} x {epidim.shape[1]}",
        "Source to Imager Distance (mm)": dcm.RTImageSID,
        "Pixel Spacing (mm x mm)": f"{dcm.ImagePlanePixelSpacing[0]} x {dcm.ImagePlanePixelSpacing[1]}",
        "Collimator Angle":dcm.BeamLimitingDeviceAngle,
        "Number of Peaks" :p.shape[1],
        "Average Gap (mm)": round(ps*np.diff(p).mean(),2)
        }
      tab1=pd.DataFrame(data=list(dictionary.values()),index=list(dictionary.keys()))
      tab1.reset_index(inplace=True)
      tab1.columns = ["Parameter","Value"]

     
      
      st.write(tab1)

     
      
    with col2:
  
      
      fig,ax = plt.subplots() 
      
  
      for i in range(round(0.1*bkgsub.shape[0]),round(0.9*bkgsub.shape[0]),20):
        ax.plot(np.arange(0,epidim.shape[0],1)*ps,epidim[:,i])


      
      
      ax.vlines(x=p.to_numpy()*ps,ymax=epidim.max(),ymin=0,colors=["cyan"],
                linestyles=":")

        
    
      ax.set_title("Line Profiles along MLC direction")
      ax.set_xlabel("Distance along along MLC direction (mm)")
    
      ax.grid(True)
      plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)


      
      st.pyplot(fig)
    
     
      st.write("Peak Locations and Gaps")
      tab2=np.round(p*ps,1)
      tab2.columns=[f"Peak {i+1}" for i in range(p.shape[1])]
      tab2.index=["(mm)"]
      st.write(tab2)
      tab3=pd.DataFrame(np.round(np.diff(p*ps),1))
      tab3.index=["(mm)"]
      tab3.columns=[f"Gap {i+1}" for i in range(tab3.shape[1])]
      st.write(tab3)

# what if the uploaded file is not of varian portal dosimetry( elekta mlc leaves move longitudinally)
# didnot account for possible offsets
# add more measurements like fwhm, error vs no error
      

