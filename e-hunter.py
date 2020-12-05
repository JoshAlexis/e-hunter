from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os

headers = {"User-Agent": "Mozilla/5.0"}


def get_images(request_text):
    """
    Retrieves the title of the image set and the static files url
    to get all the images

    Parameters
    ----------
    request_text : str
        A string in unicode with the content of the page
    """
    soup = BeautifulSoup(request_text, 'lxml')
    title = soup.find('h2').text
    image_container = soup.find('div', id="display_image_detail")
    img = image_container.find('a')
    img_url = img['href']

    total_images = get_total_images(title)
    images_urls = create_static_urls(img_url, total_images)
    download_images(images_urls, title)


def get_total_images(title):
    """
    Retrieves the amount of images to download from the title

    Parameters
    ----------
    title : str
        The title retrieved from the page
    """
    total_images = int(title.split(' ')[-1].split('/')[1])
    print(f'Total images: {total_images}')
    return total_images


def create_static_urls(base_url, number_images):
    """
    Creates a list with the urls for each image

    Parameters
    ----------
    base_url : str
        The URL of the page to create the static URL's
    number_images : int
    """
    images_urls = []
    for i in tqdm(range(1, number_images + 1), "Creating URLs"):
        chunks = base_url.split('/')
        chunks[-1] = f'{i}.jpg'
        new_url = " ".join(chunks).replace(' ', '/')
        images_urls.append(new_url)
    return images_urls


def download_images(images_urls, title):
    """
    Creates the directory to store the images and
    downloads the images.

    Parameters
    ----------
    images_urls : list
        A list with the URL's of the images
    title : str
        The title of the set of images
    """
    # We get the name of the folder
    path = " ".join(title.split(' ')[0:-2])

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print(f"Cannot create directory {path}")
            return

    for url_img in images_urls:
        # number of the image
        img = url_img.split('/')[-1]
        # We retrieve the stream of the file
        image_res = requests.get(url_img, headers=headers, stream=True)
        img_status = image_res.status_code
        if img_status == 200:  # If we have a ok response
            file_size = int(image_res.headers.get("content-length"))
            # We verify the response has an image
            if file_size == 0:
                write_log(f'From {path} cannot download image {img}\n')
                continue
            # We create the image file
            image_path = f'{path}/{img}'
            chunk_size = 1024
            # progress bar
            progress = tqdm(image_res.iter_content(chunk_size=chunk_size), f'Downloading {img}',
                            total=file_size / chunk_size, unit="KB")
            with open(image_path, "wb") as image:
                for data in progress:
                    image.write(data)
                    progress.update(len(data))
        else:
            write_log(f'From {path} cannot download image {img}\n')


def write_log(text):
    """
    To create a log of errors - images that cannot be downloaded

    Parameters
    -----------
    text : str
        The text to put in the log file
    """
    log = "log.txt"
    with open(log, "a+") as log:
        log.write(text)
        log.close()


if __name__ == '__main__':

    while True:
        url = input("URL to download images: ")
        if "attachment/1/" not in url:
            url = f'{url}attachment/1/'
        hmtl_text = requests.get(url, headers=headers)
        status_code = hmtl_text.status_code
        if status_code == 200:
            get_images(hmtl_text.text)
        res = input("Another image set? (y/n): ")
        if res.lower() != 'y':
            break