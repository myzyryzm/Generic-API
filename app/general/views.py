from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from core.models import Song
import app.settings
import librosa
import numpy as np

base_url = 'http://localhost:8000'
# this get request will have arguments in it such as the name of the song or maybe the song id and will find that song to do what it gotta do
@api_view(['GET'])
def index(request):
    query_params = request.GET
    # also can use query_params.getlist(NAME_OF_VARIABLE) to get a specific variable
    for key, item in query_params.items():
        print(key)
    return Response(None, status=status.HTTP_200_OK)

@api_view(['GET'])
def songs(request):
    songs = Song.objects.all().values('file', 'title')
    if len(songs) == 0:
        return Response('no songs silly!', status=status.HTTP_204_NO_CONTENT)
    ret = []
    for song in songs:
        s = {}
        file_path = app.settings.MEDIA_URL + song['file']
        if file_path[0] == '/':
            file_path = file_path[1:]
        samples, sampling_rate = librosa.load(file_path, sr=None, mono=True, offset=0.0, duration=None)
        s['title'] = song['title']
        s['file'] = file_path
        s['num_samples'] = len(samples)
        s['sampling_rate'] = sampling_rate
        spec = spectrogram(samples, sampling_rate, max_freq=sampling_rate//2)
        ret.append(s)
            
    return Response(ret, status=status.HTTP_200_OK)

def spectrogram(samples, sample_rate, stride_ms = 10.0, 
                          window_ms = 20.0, max_freq = None, eps = 1e-14):

    stride_size = int(0.001 * sample_rate * stride_ms)
    window_size = int(0.001 * sample_rate * window_ms)

    # Extract strided windows
    truncate_size = (len(samples) - window_size) % stride_size
    samples = samples[:len(samples) - truncate_size]
    nshape = (window_size, (len(samples) - window_size) // stride_size + 1)
    nstrides = (samples.strides[0], samples.strides[0] * stride_size)
    windows = np.lib.stride_tricks.as_strided(samples, 
                                          shape = nshape, strides = nstrides)
    
    assert np.all(windows[:, 1] == samples[stride_size:(stride_size + window_size)])

    # Window weighting, squared Fast Fourier Transform (fft), scaling
    weighting = np.hanning(window_size)[:, None]
    
    fft = np.fft.rfft(windows * weighting, axis=0)
    fft = np.absolute(fft)
    fft = fft**2
    
    scale = np.sum(weighting**2) * sample_rate
    fft[1:-1, :] *= (2.0 / scale)
    fft[(0, -1), :] /= scale
    
    # Prepare fft frequency list
    freqs = float(sample_rate) / window_size * np.arange(fft.shape[0])
    # print(freqs, freqs.shape)
    # Compute spectrogram feature
    # print(np.arange(fft.shape[0]))
    ind = np.where(freqs <= max_freq)[0][-1] + 1
    specgram = np.log(fft[:ind, :] + eps)
    return specgram
