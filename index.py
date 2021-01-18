import re
from ehunter import EHunter

regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if __name__ == '__main__':

    while True:
        url = input("URL to download images: ")
        if re.match(regex, url) is not None:
            if "attachment"in url:
                chunks = url.split("/")[0:-3]
                url = " ".join(chunks).replace(" ", "/")
            downImages = EHunter()
            downImages.get_images(url)
            res = input("Another image set? (y/n): ")
            res = res.strip()
            if res.lower() != 'y':
                break
        else:
            print("Please enter a valid URL")