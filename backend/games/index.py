import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Games library CRUD API
    Args: event with httpMethod, body, headers
    Returns: HTTP response with games data
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Session-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    
    try:
        user_id = get_user_from_session(conn, event.get('headers', {}))
        if not user_id:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unauthorized'}),
                'isBase64Encoded': False
            }
        
        if method == 'GET':
            return get_games(conn, user_id)
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            return create_game(conn, user_id, body_data)
        elif method == 'PUT':
            body_data = json.loads(event.get('body', '{}'))
            return update_game(conn, user_id, body_data)
        
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    finally:
        conn.close()

def get_user_from_session(conn, headers: Dict[str, str]) -> int:
    session_token = headers.get('x-session-token') or headers.get('X-Session-Token')
    if not session_token:
        return None
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT user_id FROM sessions WHERE session_token = %s AND expires_at > NOW()",
        (session_token,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result['user_id'] if result else None

def get_games(conn, user_id: int) -> Dict[str, Any]:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, hours, status, created_at FROM games WHERE user_id = %s ORDER BY updated_at DESC",
        (user_id,)
    )
    games = cursor.fetchall()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'games': [dict(g) for g in games]}, default=str),
        'isBase64Encoded': False
    }

def create_game(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    name = body_data.get('name')
    hours = body_data.get('hours', 0)
    status = body_data.get('status', 'playing')
    
    if not name:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Game name required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO games (user_id, name, hours, status) VALUES (%s, %s, %s, %s) RETURNING id, name, hours, status, created_at",
        (user_id, name, hours, status)
    )
    game = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'game': dict(game)}, default=str),
        'isBase64Encoded': False
    }

def update_game(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    game_id = body_data.get('id')
    if not game_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Game ID required'}),
            'isBase64Encoded': False
        }
    
    updates = []
    params = []
    
    if 'name' in body_data:
        updates.append("name = %s")
        params.append(body_data['name'])
    if 'hours' in body_data:
        updates.append("hours = %s")
        params.append(body_data['hours'])
    if 'status' in body_data:
        updates.append("status = %s")
        params.append(body_data['status'])
    
    updates.append("updated_at = NOW()")
    
    if len(updates) <= 1:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No fields to update'}),
            'isBase64Encoded': False
        }
    
    params.extend([game_id, user_id])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        f"UPDATE games SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING id, name, hours, status",
        params
    )
    game = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    if not game:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Game not found'}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'game': dict(game)}),
        'isBase64Encoded': False
    }
