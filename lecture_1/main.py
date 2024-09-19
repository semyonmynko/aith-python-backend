import json
from urllib.parse import parse_qs

async def app(scope, receive, send):
    assert scope['type'] == 'http'

    path = scope['path']
    query_string = scope['query_string'].decode()
    query_params = parse_qs(query_string)

    if path.startswith('/factorial'):
        response = factorial_handler(query_params)
    elif path.startswith('/fibonacci'):
        response = fibonacci_handler(path)
    elif path.startswith('/mean'):
        response = mean_handler(await receive_body(receive))
    else:
        response = {
            'status': 404,
            'body': json.dumps({'detail': 'Not Found'})
        }

    await send({
        'type': 'http.response.start',
        'status': response['status'],
        'headers': [(b'content-type', b'application/json')]
    })

    await send({
        'type': 'http.response.body',
        'body': response['body'].encode()
    })


async def receive_body(receive):
    """Функция для получения полного тела запроса."""
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


def factorial_handler(params):
    try:
        n = int(params.get('n', [None])[0])
        if n is None or n < 0:
            return {'status': 400, 'body': json.dumps({'detail': 'Input must be a non-negative integer'})}
    except (ValueError, TypeError):
        return {'status': 422, 'body': json.dumps({'detail': 'Invalid input for factorial'})}

    result = 1
    for i in range(2, n + 1):
        result *= i

    return {'status': 200, 'body': json.dumps({'number': n, 'result': result})}


def fibonacci_handler(path):
    try:
        n_str = path.split('/')[-1]
        n = int(n_str)
        if n < 0:
            return {'status': 400, 'body': json.dumps({'detail': 'Input must be a non-negative integer'})}
    except (ValueError, TypeError):
        return {'status': 422, 'body': json.dumps({'detail': 'Invalid input for fibonacci'})}

    fib_seq = [0, 1]
    for _ in range(2, n):
        next_fib = fib_seq[-1] + fib_seq[-2]
        fib_seq.append(next_fib)

    return {'status': 200, 'body': json.dumps({'n': n, 'result': fib_seq[:n]})}


def mean_handler(params):
    try:
        numbers = json.loads(params)
        
        if not isinstance(numbers, list):
            raise ValueError

        if not numbers:
            return {'status': 400, 'body': json.dumps({'detail': 'The list of numbers cannot be empty'})}

        numbers = list(map(float, numbers))
    except (ValueError, TypeError, json.JSONDecodeError):
        return {'status': 422, 'body': json.dumps({'detail': 'Invalid input for mean'})}

    result = sum(numbers) / len(numbers)
    return {'status': 200, 'body': json.dumps({'numbers': numbers, 'result': result})}