from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os

headers = {"User-Agent": "Mozilla/5.0"}


def get_images(url):
    """
    Obtains the title of the image set and the static files url
    to get all the images

    Parameters
    ----------
    url : str
        The URL of the image set
    """
    request_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(request_text, 'lxml')
    # we get the attachment URL of the first image
    image_container = soup.find('div', class_ ="icon-overlay")
    url_set = image_container.find('a')
    chunk_url = url_set['href'].split("/")
    """
    We separate the attachment/number/ part of the first image, 
    because sometimes the set of images begins in the second image
    """
    attachment_url = f'{chunk_url[-3]}/{chunk_url[-2]}/'
    img_url = ""
    if not url[-1] == '/':
        img_url = f'{url}/{attachment_url}'
    else:
        img_url = f'{url}{attachment_url}'
    attachment_req = requests.get(img_url, headers=headers).text
    attachment_soup = BeautifulSoup(attachment_req, 'lxml')
    title = attachment_soup.find('h2').text
    total_images = get_total_images(title)
    download_images(img_url, title, total_images)


def get_total_images(title):
    """
    Get the amount of images to download from the title.
    The title is in the way:
    title_of_image_set - 1/n
    where n represents the total number of images.
    The part of title_of_image_set can be a long name
    with japanese ideograms or not.

    Parameters
    ----------
    title : str
        The title obtained from the page
    """
    total_images = int(title.split(' ')[-1].split('/')[1])
    print(f'Total images: {total_images}')
    return total_images


def clean_title(title):
    """
    Removes out the invalid characters for a windows directory
    name. In Windows the invalid characters are:
    <, >, : , /, |, ?, * and backslash

    Parameters
    ----------
    title : str
        The original title

    Returns
    -------
    str
        The title without the invalid characters
    """
    char_to_replace = {
        '<' : '-',
        '>' : '-',
        ':' : '-',
        '/' : '-',
        '\\': '-',
        '|' : '-',
        '?' : '-',
        "*" : '-'
    }
    for key, value in char_to_replace.items():
        title = title.replace(key, value)
    return title

def get_static_url_from_attachment(attachment_url, attach_num):
    """
    Obtains the URL to the file of each image.

    Parameters
    ----------
    attachment_url : str
        The base attachment URL in the way of:
        https://hentai-cosplays/image/name/attachment/attach_num/
    attach_num : int
        The number of the current attachment URL

    Returns
    -------
    str
        The URL of the file or the text "No available"
    """
    # We split the string to modify the attach number
    chunk_url = attachment_url.split("/")
    chunk_url[-2] = str(attach_num) # casted to string to avoid problems in the join
    attachment_url = " ".join(chunk_url).replace(" ", "/")
    attachment_req = requests.get(attachment_url, headers=headers).text
    soup = BeautifulSoup(attachment_req, 'lxml')
    # Each attachment page contains the image that is a link to the file
    img_container = soup.find('div', id = "display_image_detail")
    # Sometimes the request does not contains a image, in that case
    # we return a string to say "there is not an image"
    if not img_container:
        return "No available"
    img = img_container.find('a')
    # the URL to the file is in the way
    # https://static2.hentai-cosplays.com/upload/date/number/id/image_number.format
    static_url = img['href']
    return static_url

def download_images(base_url, title, total_images):
    """
    Creates the directory to store the images and
    downloads the images.

    Parameters
    ----------
    base_url : str
        The first attachment URL of the image set
    title : str
        The title of the set of images
    total_images : int
        The total number of images to download
    """
    # We get the name of the folder
    title = clean_title(title)
    # The title is in the way: a long or shot title - 1/92
    path = " ".join(title.split(' ')[0:-2])

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print(f"Cannot create directory {path}")
            return

    for i in range(1, total_images + 1):
        url_img = get_static_url_from_attachment(base_url, i)

        if url_img == "No available":
            continue

        img = url_img.split('/')[-1]

        image_res = requests.get(url_img, headers=headers, stream=True)
        img_status = image_res.status_code
        if img_status == 200:
            file_size = int(image_res.headers.get("content-length"))

            if file_size == 0:
                write_log(f'From {path} cannot download file {img}\n')
                continue

            image_path = f'{path}/{img}'
            chunk_size = 1024

            progress = tqdm(image_res.iter_content(chunk_size=chunk_size), f'Downloading {img}',
                            total=file_size / chunk_size, unit="KB")
            with open(image_path, "wb") as image:
                for data in progress:
                    image.write(data)
                    progress.update(len(data))
        else:
            write_log(f'From {path} cannot download file {img}\n')


def write_log(text):
    """
    Creates a log of errors with the text:
    "From path cannot download file filename"
    where path is the title of the image set and
    filename the number and format of the file

    Parameters
    -----------
    text : str
        The text to put in the log file
    """
    log = "log.txt"
    with open(log, "a+") as filetext:
        filetext.write(text)
        filetext.close()


if __name__ == '__main__':

    while True:
        url = input("URL to download images: ")
        if "attachment"in url:
            chunks = url.split("/")[0:-3]
            url = " ".join(chunks).replace(" ", "/")
        get_images(url)
        res = input("Another image set? (y/n): ")
        if res.lower() != 'y':
            break