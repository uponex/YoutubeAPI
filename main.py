import time
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import uvicorn
import os
from pytube import YouTube
from pytube import Playlist
from pytube.cli import on_progress


app = FastAPI()


class Info(BaseModel):
    author: str
    title: str
    view: float
    length: int
    description: str
    thumbnail: str
    fileSizeHD: str


@app.get("/")
async def hello():
    return {"result": "Its working YES! This is a miracle!"}


@app.get("/info")
async def info(url: str = None):
    try:
        yt = YouTube(url)
        videoSize = yt.streams.get_highest_resolution()
        Info.author = yt.author
        Info.title = yt.title
        Info.view = yt.views
        Info.length = ("%.2f" % float(yt.length / 60))
        Info.description = yt.description
        Info.thumbnail = yt.thumbnail_url
        Info.fileSizeHD = str(round(videoSize.filesize * 0.000001, 2)) + " Mb"
        res = {None}
        for i in yt.streams:
            res.add(i.resolution)
        res.remove(None)
        res = [int(i) for i in [sub.replace('p', '') for sub in res]]
        sres = sorted(res)
        return { "Title": Info.title, "Resolution": sres, "Author": Info.author, "Thumbnail": Info.thumbnail, "View": Info.view,
                "Length": Info.length, "Description": Info.description,
                 "File size": Info.fileSizeHD}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': str(e)})
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": 'success'})


@app.get("/video")
async def video(url: str = None):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        yd = yt.streams.get_highest_resolution()
        folder_name = "FILE_NAME"
        file_path = os.getcwd() + "/" + folder_name
        video = yd.download(file_path)
        yt.title
        print(file_path)
        headers = {'success': f'video is ready, filename= {yt.title}'}
        return FileResponse(path=video, headers=headers, media_type='application/mp4', filename=(yt.title + ".mp4"))

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': str(e)}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": 'success, video is ready'}
        )


@app.get("/audio")
async def audio(url: str = None):
    try:
        ya = YouTube(url)
        folder_name = "FILE_NAME"
        # DEPENDS ON WHERE YOUR FILE LOCATES
        file_path = os.getcwd() + "/" + folder_name
        video = ya.streams.filter(only_audio=True).first()
        downloaded_file = video.download(file_path)
        base, ext = os.path.splitext(downloaded_file)
        audio = base + 'Audio.mp3'
        os.rename(downloaded_file, audio)
        ya.title
        print(file_path)
        print(audio)
        headers = {'success': f'audio is ready, filename= {ya.title}'}
        return FileResponse(path=audio, headers=headers, media_type='application/mp4', filename=(ya.title+".mp3"))
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': str(e)}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": 'success, audio is ready'}
        )


@app.get("/delete")
async def delete_files(min: int = 10):
    try:
        response_msg = []
        folder_name = "FILE_NAME"
        file_path = os.getcwd() + "/" + folder_name
        path = file_path
        files = os.listdir(file_path)
        print(files)
        print(f"file_path: {file_path}")
        file_name_delete = []
        dir_name = file_path
        # Get list of all files only in the given directory
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                               os.listdir(dir_name))
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files,
                               key=lambda x: os.path.getmtime(os.path.join(dir_name, x))
                               )
        for file_name in list_of_files:
            file_path = os.path.join(dir_name, file_name)
            timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(file_path)))
            print(timestamp_str, ' -->', file_name)
            #filter by minite
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            f = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(f)
            file_date_age = file_date + timedelta(minutes=min)
            duration = now - file_date_age
            duration_in_s = duration.total_seconds()
            minut = (int(round(duration_in_s / 60, 0)))
            print(f"duration: {minut}")
            if minut > min:
                file_name_delete.append(file_name)
        ### create a list of old file by date
        print(f"file_name_delete {len(file_name_delete)}, {file_name_delete}")
        #print(os.listdir(path))
        for i in file_name_delete:
        #for file_name_delete in os.listdir(path):
            print(f"file_name: {file_name_delete}")
            #print(f"path: {path}")
            # construct full file path
            del_file = path + "/" + i
            #print(f"file: {del_file}")
            if os.path.isfile(del_file):
                response_msg.append(f"Deleting file: {del_file}")
                print('Deleting file:', del_file)
                os.remove(del_file)
                print(len(del_file))
        if len(response_msg) < 1:
        #     response_msg.clear()
            response_msg.append(f"no files to delete after: {min} min")
        return response_msg
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': str(e)})
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": 'success'})


@app.get("/aws")
async def aws_files():
    folder_name = "FILE_NAME"
    file_path = os.getcwd() + "/" + folder_name
    files = os.listdir(file_path)
    result = []
    dir_name = file_path
    # Get list of all files only in the given directory
    list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                           os.listdir(dir_name))
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted(list_of_files,
                           key=lambda x: os.path.getmtime(os.path.join(dir_name, x))
                           )
    for file_name in list_of_files:
        file_path = os.path.join(dir_name, file_name)
        size = ("%.2f" % float(os.path.getsize(file_path)*0.000001))
        timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(file_path)))
        result.append(f"({timestamp_str}, ' -->', {file_name}, ' -->', {size}' MB')")
    return result


def raise_exception():
    return HTTPException(status_code=404,
                         detail="Input is Not valid!",
                         headers={"X-Header_Error":
                                  f"Nothing to be seen"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True, log_level="info", workers=2)

print('Download Complete')
