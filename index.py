import re
from ehunter import EHunter

regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def stripAttachmentURL(url):
    """
    Strip the attachment section from URL
    Parameters
    ----------
    url : str
        The URL to retrive the image set

    Returns
    -------
    str
    """
    if "attachment"in url:
        chunks = url.split("/")[0:-3]
        url = " ".join(chunks).replace(" ", "/")
    return url

if __name__ == '__main__':

    downImages = EHunter()

    while True:
        res = input("Multiple elements? (y/n): ")

        if res.lower().strip() == 'y':

            total = int(input("How many?: "))

            array_urls = []
            count = 0

            while count < total:
                url = input("URL to download images: ")
                if re.match(regex, url) is not None:
                    url = stripAttachmentURL(url)
                    array_urls.append(url)
                    count += 1
                else:
                    print("Please enter a valid URL")

            for url in array_urls:
                downImages.get_images(url)

            res = input("Another image set? (y/n): ")
            if res.lower().strip() != 'y':
                break
        else:
            res = input("Exit? (y/n): ")

            if res.lower().strip() == 'y':
                break;

            url = input("URL to download images: ")
            if re.match(regex, url) is not None:
                url = stripAttachmentURL(url)
                downImages.get_images(url)
                res = input("Another image set? (y/n): ")
                if res.lower().strip() != 'y':
                    break
            else:
                print("Please enter a valid URL")