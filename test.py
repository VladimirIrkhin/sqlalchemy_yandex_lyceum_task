from requests import get, post, delete


# получаем список работ
print(get('http://localhost:8080/api/v2/jobs').json())

# получаем одну работу
print(get('http://localhost:8080/api/v2/jobs/3').json())
# некорректный запрос получения одной работы
print(get('http://localhost:8080/api/v2/jobs/999').json())
# удаление работы
print(delete('http://localhost:8080/api/v2/jobs/3').json())
# получаем список работ, чтобы удостовериться, что работа удалена
print(get('http://localhost:8080/api/v2/jobs').json())

# тестирование корректного post запроса
print(post('http://localhost:8080/api/v2/jobs',
           json={'team_leader': 1, 'job': 'qwe', 'about': 'asd',
                 'work_size': 3, 'collaborators': '1, 2, 3', 'is_finished': False}).json())
# тестирование неполного post запроса
print(post('http://localhost:8080/api/v2/jobs',
           json={'team_leader': 1}).json())
# тестирование пустого post запроса
print(post('http://localhost:8080/api/v2/jobs',
           json={}).json())
# получаем список работ, чтобы удостовериться, что работа добавлен
print(get('http://localhost:8080/api/v2/jobs').json())
