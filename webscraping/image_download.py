# image_download.py

# Takes CSV file of products with 'Variant SKU' and 'Product Image' fields and downloads and saves images for each product.

import requests
import pandas as pd
import time

MODEL_KEY = 'Variant SKU'
IMAGE_KEY = 'Product Image'
INPUT_FILE = 'PA150_output.csv'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_images_from_csv(input_file, model_key, image_key, headers):
    df = pd.read_csv(input_file)

    for _, row in df.iterrows():
        model = row[model_key]
        img_url = row[image_key]
        file_name = f'{model}.jpg'

        print(model, img_url)
        
        try:
            res = requests.get(img_url, headers=headers, stream=True)
            if res.status_code == 200:
                with open(file_name, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                print('Image downloaded:', file_name)
            else:
                print('Image could not be downloaded:', res.status_code)
            res.close()
            time.sleep(1)  # sleep for 1 second
        except requests.RequestException as e:
            print(f"Error downloading {img_url}. Error: {e}")

if __name__ == "__main__":
    download_images_from_csv(INPUT_FILE, MODEL_KEY, IMAGE_KEY, HEADERS)
