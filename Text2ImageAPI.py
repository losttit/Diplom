import json
import time
import requests


class Text2ImageAPI:
    def __init__(self, url, api_key='A76E51110C814D535B84232B1AFB3021', secret_key='5107BCE6311486302B7DEBC69F361E39'):
        # Инициализируем URL-адрес API и заголовки аутентификации
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        # Получаем список доступных моделей из API
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        # Возвращаем ID первой модели в списке
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        # Подготавливаем параметры для запроса генерации текста в изображение
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        # Подготавливаем данные запроса, включая ID модели и параметры
        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }

        # Отправляем запрос в API
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        # Возвращаем UUID запроса на генерацию
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        # Проверяем статус запроса на генерацию
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                # Возвращаем сгенерированные изображения, когда запрос будет выполнен
                return data['images']

            attempts -= 1
            # Ждем короткое время перед повторной проверкой
            time.sleep(delay)
