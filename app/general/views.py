from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from core.models import Song
import app.settings
from utils.spectrogram import get_spectrogram_data

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
    query_parms = request.GET
    if 'title' in query_parms:
        songs = Song.objects.values('file', 'title').filter(title=query_parms['title'])
    else:
        songs = Song.objects.all().values('file', 'title')
    if len(songs) == 0:
        return Response('no songs silly!', status=status.HTTP_204_NO_CONTENT)
    ret = []
    for song in songs:
        s = {}
        s["title"] = song["title"]
        file_path = app.settings.MEDIA_URL + song['file']
        if file_path[0] == '/':
            file_path = file_path[1:]
        if 'get_file_path' in query_parms:
            return JsonResponse(file_path, safe=False, status=status.HTTP_200_OK)
        spec = get_spectrogram_data(file_path)
        s["spectrogram"] = spec
        ret.append(s)
        return JsonResponse(s, safe=False, status=status.HTTP_200_OK)
            
    return JsonResponse(ret, safe=False, status=status.HTTP_200_OK)
