import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Streaming platforms CRUD API
    Args: event with httpMethod, body, headers
    Returns: HTTP response with platforms data
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
            return get_platforms(conn, user_id)
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            return create_platform(conn, user_id, body_data)
        elif method == 'PUT':
            body_data = json.loads(event.get('body', '{}'))
            return update_platform(conn, user_id, body_data)
        elif method == 'DELETE':
            body_data = json.loads(event.get('body', '{}'))
            return delete_platform(conn, user_id, body_data)
        
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

def get_platforms(conn, user_id: int) -> Dict[str, Any]:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, icon, color, status, created_at FROM streaming_platforms WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    platforms = cursor.fetchall()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'platforms': [dict(p) for p in platforms]}, default=str),
        'isBase64Encoded': False
    }

def create_platform(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    name = body_data.get('name')
    icon = body_data.get('icon', 'Tv')
    color = body_data.get('color', 'bg-primary')
    
    if not name:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Platform name required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO streaming_platforms (user_id, name, icon, color) VALUES (%s, %s, %s, %s) RETURNING id, name, icon, color, status, created_at",
        (user_id, name, icon, color)
    )
    platform = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'platform': dict(platform)}, default=str),
        'isBase64Encoded': False
    }

def update_platform(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    platform_id = body_data.get('id')
    if not platform_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Platform ID required'}),
            'isBase64Encoded': False
        }
    
    updates = []
    params = []
    
    if 'name' in body_data:
        updates.append("name = %s")
        params.append(body_data['name'])
    if 'icon' in body_data:
        updates.append("icon = %s")
        params.append(body_data['icon'])
    if 'color' in body_data:
        updates.append("color = %s")
        params.append(body_data['color'])
    if 'status' in body_data:
        updates.append("status = %s")
        params.append(body_data['status'])
    
    if not updates:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No fields to update'}),
            'isBase64Encoded': False
        }
    
    params.extend([platform_id, user_id])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        f"UPDATE streaming_platforms SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING id, name, icon, color, status",
        params
    )
    platform = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    if not platform:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Platform not found'}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'platform': dict(platform)}),
        'isBase64Encoded': False
    }

def delete_platform(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    platform_id = body_data.get('id')
    if not platform_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Platform ID required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE streaming_platforms SET status = 'deleted' WHERE id = %s AND user_id = %s",
        (platform_id, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    
    if affected == 0:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Platform not found'}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'message': 'Platform deleted'}),
        'isBase64Encoded': False
    }
