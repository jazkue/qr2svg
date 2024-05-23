import sys, os, requests
from sys import platform
from subprocess import call

FOR_VERSION = 2

def open_tab(url):
    if platform == "darwin":
        call(['open', url])
    elif platform == "win32":
        call(['cmd.exe', '/c', 'start', url])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py /path/to/svg/folder")
        sys.exit(1)

    folder_path = sys.argv[-1]
    if not os.path.isdir(folder_path):
        print("Error: Invalid folder path")
        sys.exit(1)

    # Get a sorted list of SVG files in the folder
    svg_files = sorted([os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".svg")])

    for filename in svg_files:
        # Send file to the API
        with open(filename, 'rb') as f:
            response = requests.post('http://compress-or-die.com/api-v2', data=f, headers={'X-DOCUMENT-NAME': os.path.basename(filename)})
        
        # Parse the answer to get the session id
        lines = response.text.splitlines()
        answer = {}
        for line in lines:
            parts = line.split(':', 1)
            answer[parts[0]] = parts[1]
        print(answer['_VERSION'])

        # Check version
        if int(answer['_VERSION']) != FOR_VERSION:
            print('Aborting: This script is for version ' + str(FOR_VERSION) + ', but the current version is ' + answer['_VERSION'] + '.', file=sys.stderr)
            exit(1)

        # Open the browser to show the image on compress-or-die.com
        open_tab(answer['_URL'] + '?session=' + answer['_SESSION'] + "&precision=1")
