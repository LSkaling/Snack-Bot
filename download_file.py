import requests

def download_file(file_url, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download file: ", response.status_code)
        return None 