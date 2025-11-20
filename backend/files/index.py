import json
import os
import base64
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: File manager API with upload, download, list, delete
    Args: event with httpMethod, body, headers
    Returns: HTTP response with files data
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
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
            query_params = event.get('queryStringParameters', {}) or {}
            file_id = query_params.get('id')
            if file_id:
                return download_file(conn, user_id, file_id)
            return list_files(conn, user_id)
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            return upload_file(conn, user_id, body_data)
        
        elif method == 'DELETE':
            body_data = json.loads(event.get('body', '{}'))
            return delete_file(conn, user_id, body_data)
        
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

def list_files(conn, user_id: int) -> Dict[str, Any]:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, size, type, created_at FROM files WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    files = cursor.fetchall()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'files': [dict(f) for f in files]}, default=str),
        'isBase64Encoded': False
    }

def upload_file(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    name = body_data.get('name')
    size = body_data.get('size')
    file_type = body_data.get('type', 'unknown')
    content = body_data.get('content', '')
    
    if not name or size is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'File name and size required'}),
            'isBase64Encoded': False
        }
    
    storage_key = f"user_{user_id}/{name}"
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO files (user_id, name, size, type, storage_key) VALUES (%s, %s, %s, %s, %s) RETURNING id, name, size, type, created_at",
        (user_id, name, size, file_type, storage_key)
    )
    file_record = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'file': dict(file_record)}, default=str),
        'isBase64Encoded': False
    }

def download_file(conn, user_id: int, file_id: str) -> Dict[str, Any]:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, name, size, type, storage_key FROM files WHERE id = %s AND user_id = %s",
        (file_id, user_id)
    )
    file_record = cursor.fetchone()
    cursor.close()
    
    if not file_record:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'File not found'}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'file': dict(file_record),
            'downloadUrl': f"/api/files?id={file_id}"
        }),
        'isBase64Encoded': False
    }

def delete_file(conn, user_id: int, body_data: Dict[str, Any]) -> Dict[str, Any]:
    file_id = body_data.get('id')
    if not file_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'File ID required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT storage_key FROM files WHERE id = %s AND user_id = %s",
        (file_id, user_id)
    )
    file_record = cursor.fetchone()
    
    if not file_record:
        cursor.close()
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'File not found'}),
            'isBase64Encoded': False
        }
    
    cursor.execute(
        "UPDATE files SET type = 'deleted' WHERE id = %s AND user_id = %s",
        (file_id, user_id)
    )
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'message': 'File deleted'}),
        'isBase64Encoded': False
    }
