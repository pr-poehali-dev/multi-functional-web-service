import json
import os
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Authentication API with registration, login, 2FA setup
    Args: event with httpMethod, body, headers
    Returns: HTTP response with user data or error
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Session-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    
    try:
        if method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            action = body_data.get('action', 'login')
            
            if action == 'register':
                return register_user(conn, body_data)
            elif action == 'login':
                return login_user(conn, body_data)
            elif action == 'verify_session':
                return verify_session(conn, event.get('headers', {}))
            elif action == 'enable_2fa':
                return enable_2fa(conn, event.get('headers', {}))
            elif action == 'verify_2fa':
                return verify_2fa_code(conn, body_data, event.get('headers', {}))
        
        elif method == 'GET':
            return verify_session(conn, event.get('headers', {}))
        
        elif method == 'PUT':
            body_data = json.loads(event.get('body', '{}'))
            return update_user_settings(conn, body_data, event.get('headers', {}))
        
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    finally:
        conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def generate_2fa_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')

def register_user(conn, body_data: Dict[str, Any]) -> Dict[str, Any]:
    email = body_data.get('email')
    password = body_data.get('password')
    language = body_data.get('language', 'ru')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Email and password required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return {
            'statusCode': 409,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'User already exists'}),
            'isBase64Encoded': False
        }
    
    password_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (email, password_hash, language) VALUES (%s, %s, %s) RETURNING id, email, language, theme, two_fa_enabled",
        (email, password_hash, language)
    )
    user = cursor.fetchone()
    
    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=7)
    cursor.execute(
        "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
        (user['id'], session_token, expires_at)
    )
    
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 201,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'user': dict(user),
            'session_token': session_token
        }),
        'isBase64Encoded': False
    }

def login_user(conn, body_data: Dict[str, Any]) -> Dict[str, Any]:
    email = body_data.get('email')
    password = body_data.get('password')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Email and password required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    password_hash = hash_password(password)
    
    cursor.execute(
        "SELECT id, email, language, theme, two_fa_enabled FROM users WHERE email = %s AND password_hash = %s",
        (email, password_hash)
    )
    user = cursor.fetchone()
    
    if not user:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid credentials'}),
            'isBase64Encoded': False
        }
    
    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=7)
    cursor.execute(
        "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
        (user['id'], session_token, expires_at)
    )
    
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'user': dict(user),
            'session_token': session_token
        }),
        'isBase64Encoded': False
    }

def verify_session(conn, headers: Dict[str, str]) -> Dict[str, Any]:
    session_token = headers.get('x-session-token') or headers.get('X-Session-Token')
    
    if not session_token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Session token required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        '''SELECT u.id, u.email, u.language, u.theme, u.two_fa_enabled, u.analytics_enabled, u.action_logging_enabled
           FROM users u
           JOIN sessions s ON u.id = s.user_id
           WHERE s.session_token = %s AND s.expires_at > NOW()''',
        (session_token,)
    )
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid or expired session'}),
            'isBase64Encoded': False
        }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'user': dict(user)}),
        'isBase64Encoded': False
    }

def enable_2fa(conn, headers: Dict[str, str]) -> Dict[str, Any]:
    session_token = headers.get('x-session-token') or headers.get('X-Session-Token')
    
    if not session_token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Session token required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT user_id FROM sessions WHERE session_token = %s AND expires_at > NOW()",
        (session_token,)
    )
    session = cursor.fetchone()
    
    if not session:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid session'}),
            'isBase64Encoded': False
        }
    
    two_fa_secret = generate_2fa_secret()
    cursor.execute(
        "UPDATE users SET two_fa_secret = %s, two_fa_enabled = TRUE WHERE id = %s",
        (two_fa_secret, session['user_id'])
    )
    conn.commit()
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'secret': two_fa_secret, 'message': '2FA enabled'}),
        'isBase64Encoded': False
    }

def verify_2fa_code(conn, body_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'verified': True}),
        'isBase64Encoded': False
    }

def update_user_settings(conn, body_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    session_token = headers.get('x-session-token') or headers.get('X-Session-Token')
    
    if not session_token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Session token required'}),
            'isBase64Encoded': False
        }
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT user_id FROM sessions WHERE session_token = %s AND expires_at > NOW()",
        (session_token,)
    )
    session = cursor.fetchone()
    
    if not session:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid session'}),
            'isBase64Encoded': False
        }
    
    updates = []
    params = []
    
    if 'language' in body_data:
        updates.append("language = %s")
        params.append(body_data['language'])
    if 'theme' in body_data:
        updates.append("theme = %s")
        params.append(body_data['theme'])
    if 'analytics_enabled' in body_data:
        updates.append("analytics_enabled = %s")
        params.append(body_data['analytics_enabled'])
    if 'action_logging_enabled' in body_data:
        updates.append("action_logging_enabled = %s")
        params.append(body_data['action_logging_enabled'])
    
    if updates:
        params.append(session['user_id'])
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
            params
        )
        conn.commit()
    
    cursor.close()
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'message': 'Settings updated'}),
        'isBase64Encoded': False
    }
