from flask import Flask, request, jsonify

app = Flask(__name__)

# Хранилище последнего состояния выходов (по умолчанию все по нулям)
last_outputs = {f"d{i}": 0 for i in range(8)}

# Очередь символов для обработки пришедшего текста
char_queue = []

@app.route('/poll_chat', methods=['GET'])
def poll_chat():
    global last_outputs, char_queue
    
    # Пытаемся поймать текст из GET-запроса (например: /poll_chat?msg=Hello)
    incoming_msg = request.args.get('msg')
    
    if incoming_msg:
        # Если пришел новый текст, разбиваем его на массив символов
        char_queue = list(incoming_msg)
        print(f"[NEW TEXT RECEIVED]: '{incoming_msg}' -> Начало обработки.")

    # ПРОВЕРКА: Есть ли символы в очереди на обработку?
    if char_queue:
        # Извлекаем первый символ из очереди (работает как сдвиг каждые 0.5с)
        current_char = char_queue.pop(0)
        ascii_val = ord(current_char)
        
        # Переводим ASCII-число в 8-битную строку (например, '01001000')
        binary_str = f"{ascii_val:08b}"
        
        # Нарезаем строку на отдельные биты для выходов d0 - d7
        # Превращаем '0' или '1' в целые числа 0 или 1
        new_outputs = {f"d{i}": int(binary_str[7-i]) for i in range(8)}
        
        # ПРАВИЛО: Если пришел текст (символ обрабатывается), 7-й выход (d6) всегда равен 1
        new_outputs["d6"] = 1
        
        # Сохраняем это состояние как последнее известное
        last_outputs = new_outputs
        print(f"[PROCESSING]: '{current_char}' -> Выходы: {list(last_outputs.values())}")
    else:
        # Если текста в очереди нет, новые данные не генерируются.
        # Скрипт ничего не меняет и молча выдает сохраненный `last_outputs`.
        pass

    # Возвращаем JSON-пакет обратно в HTTP-трансмиттер игры Build Logic!
    return jsonify(last_outputs)

if __name__ == '__main__':
    # Запуск локального сервера на порту 5000
    app.run(host='0.0.0.0', port=5000)
  #ai generated idk python
