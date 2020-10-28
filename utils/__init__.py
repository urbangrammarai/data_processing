"""
Utilities for the data_processing module
"""

from tqdm import tqdm
import requests
import warnings

def download(url, filename=None, progressbar=True, buffer_size=1024):
    """
    Download a file
    
    Inspired by:
            https://www.thepythoncode.com/article/download-files-python
    ...
    
    Arguments
    ---------
    url : str
          Path to the source file to download
    filename : None/str
               [Optional. Default=None] Local destination of the file. If no
               new name is specified, the file is written on the same folder
               with the name from `url`
    progressbar : Boolean
                  [Optional. Default=True] If True, progress is tracked with 
                  a tqdm bar
    buffer_size : int
                  [Optional. Default=1024] Size of each chunk to write from 
                  the streamed file
    
    
    Returns
    -------
    None
    """
    url_filename = url.split("/")[-1]
    if filename is None:
        filename = url_filename
    if url.split(".")[-1] != filename.split(".")[-1]:
        warnings.warn("the file format in `url` and `filename` do not match!")
    response = requests.get(url, stream=True)
    if progressbar:
        file_size = int(response.headers.get("Content-length", 0))
        progress = tqdm(
            response.iter_content(buffer_size),
            f"Downloading {url_filename} into {filename}",
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024
        )
    else:
        progress = response.iter_content(buffer_size)
    with open(filename, "wb") as f:
        for chunk in progress:
            f.write(chunk)
            if progressbar:
                progress.update(len(chunk))
    return None
