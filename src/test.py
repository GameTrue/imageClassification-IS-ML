import requests
import os
import time
import threading

def fetch_photos(queries):
    with open('image-GameTrue/src/apis.txt', 'r') as f:
        api_keys = [line.strip().split(' - ')[-1] for line in f.readlines()]
    
    per_page = 30 
    semaphore = threading.Semaphore(3)  # Ограничиваем одновременно выполняемые потоки до 3
    
    def download_photos(query):
        semaphore.acquire()
        try:
            save_dir = os.path.join('image-GameTrue', 'src', 'dataset', "-".join(query.split()))
            os.makedirs(save_dir, exist_ok=True)
            existing_files = os.listdir(save_dir) 

            start_page = (len(existing_files)) // per_page + 1  
            count = (start_page - 1) * per_page + 1 

            api_key_index = 0
            page = start_page

            while count <= 2000:
                url = f'https://api.unsplash.com/search/photos?page={page}&per_page={per_page}&query={query}'
                headers = {
                    'Authorization': f'Client-ID {api_keys[api_key_index]}'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    photos = [result['urls']['regular'] for result in data['results']]
                    if not photos:
                        print(f'Нет больше фото для "{query}" на странице {page}')
                        break
                    print(f'Загружено {len(photos)} фото для "{query}" на странице {page}')
                    for photo_url in photos:
                        if count > 2000:
                            break
                        img_data = requests.get(photo_url).content
                        with open(os.path.join(save_dir, f'{count}.jpg'), 'wb') as handler:
                            handler.write(img_data)
                        count += 1
                    page += 1
                else:
                    print(f'Ошибка API ключа {api_keys[api_key_index]}, переключаюсь на следующий.')
                    api_key_index = (api_key_index + 1) % len(api_keys)
                    if api_key_index == 0:
                        print('Все API ключи исчерпаны.')
                        time.sleep(30)
        finally:
            semaphore.release()
    
    threads = []
    for query in queries:
        thread = threading.Thread(target=download_photos, args=(query,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

queries = [
    'modern architecture',
    'baroque architecture',
    'gothic architecture',
    'renaissance architecture',
    'romanesque architecture',
    'victorian architecture',
    'ancient architecture',
    'classical architecture',
]

print(fetch_photos(queries))
