import numpy as np
import pandas as pd
import math

def filter_RRs(RRs, artifact_correction_threshold):
  filtered_RRs = []
  for i in range(len(RRs)):
    if RRs[(i-1)]*(1-artifact_correction_threshold) < RRs[i] < RRs[(i-1)]*(1+artifact_correction_threshold):
      filtered_RRs.append(RRs[i])
  print(f'{len(RRs) - len(filtered_RRs)} artifacts removed, ~{round((len(RRs) - len(filtered_RRs)) / len(RRs), 2) * 100}% of the raw data')
  return filtered_RRs

def DFA(pp_values, lower_scale_limit, upper_scale_limit):
  scaleDensity = 30 # scales DFA is conducted between lower_scale_limit and upper_scale_limit
  m = 1 # order of polynomial fit (linear = 1, quadratic m = 2, cubic m = 3, etc...)

  # initialize, we use logarithmic scales
  start = np.log(lower_scale_limit) / np.log(10)
  stop = np.log(upper_scale_limit) / np.log(10)
  scales = np.floor(np.logspace(start, stop, scaleDensity))
  # equivalent to np.floor(np.logspace(np.log10(math.pow(10, start)), np.log10(math.pow(10, stop)), scaleDensity))
  F = np.zeros(len(scales))
  count = 0

  for s in scales:
    rms = []
    # Step 1: Determine the "profile" (integrated signal with subtracted offset)
    x = pp_values
    y_n = np.cumsum(x - np.mean(x))
    # Step 2: Divide the profile into N non-overlapping segments of equal length s
    L = len(x)
    shape = [int(s), int(np.floor(L/s))]
    nwSize = int(shape[0]) * int(shape[1])
    # beginning to end, here we reshape so that we have a number of segments based on the scale used at this cycle
    Y_n1 = np.reshape(y_n[0:nwSize], shape, order="F")
    Y_n1 = Y_n1.T
    # end to beginning
    Y_n2 = np.reshape(y_n[len(y_n) - (nwSize):len(y_n)], shape, order="F")
    Y_n2 = Y_n2.T
    # concatenate
    Y_n = np.vstack((Y_n1, Y_n2))

    # Step 3: Calculate the local trend for each 2Ns segments by a least squares fit of the series
    for cut in np.arange(0, 2 * shape[1]):
      xcut = np.arange(0, shape[0])
      pl = np.polyfit(xcut, Y_n[cut,:], m)
      Yfit = np.polyval(pl, xcut)
      arr = Yfit - Y_n[cut,:]
      rms.append(np.sqrt(np.mean(arr * arr)))

    if (len(rms) > 0):
      F[count] = np.power((1 / (shape[1] * 2)) * np.sum(np.power(rms, 2)), 1/2)
    count = count + 1

  pl2 = np.polyfit(np.log2(scales), np.log2(F), 1)
  alpha = pl2[0]
  return alpha

def compute_features(df):
  features = []
  window_length = 120 # seconds
  for index in range(0, int(round(df['timestamp'].max()/window_length))):
    array_rr = df.loc[(df['timestamp'] >= (index*window_length)) & (df['timestamp'] <= (index+1)*window_length), 'RR']*1000
    curr_features = compute_curr_features(array_rr)
    curr_features.update({'timestamp': index})
    features.append(curr_features)

  features_df = pd.DataFrame(features)
  return features_df

def compute_last_window_features(df, window_length=120):
  array_rr = df.loc[((df['timestamp'].max() - df['timestamp']) <= window_length), 'RR']*1000
  curr_features = compute_curr_features(array_rr)
  return curr_features  

def compute_curr_features(array_rr):
  # compute heart rate
  heartrate = round(60000/np.mean(array_rr), 2)
  # compute rmssd
  NNdiff = np.abs(np.diff(array_rr))
  rmssd = round(np.sqrt(np.sum((NNdiff * NNdiff) / len(NNdiff))), 2)
  # compute sdnn 
  sdnn = round(np.std(array_rr), 2)
  #dfa, alpha 1
  alpha1 = DFA(array_rr.to_list(), 4, 16)

  return {
  'heartrate': heartrate,
  'rmssd': rmssd,
  'sdnn': sdnn,
  'alpha1': alpha1,
  }
