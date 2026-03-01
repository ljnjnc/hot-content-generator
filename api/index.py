from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import ssl
import os

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        if self.path.startswith('/api/hot'):
            self.handle_hot_api()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/kimi':
            self.handle_kimi_api()
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def handle_hot_api(self):
        try:
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            platform = params.get('platform', ['douyin'])[0]
            api_key = params.get('key', [''])[0]
            
            if not api_key:
                self.send_error_response(400, '缺少API Key')
                return
            
            tianapi_url = f'https://apis.tianapi.com/{platform}hot/index?key={api_key}&num=20'
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(tianapi_url, method='GET')
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_kimi_api(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            api_key = data.get('apiKey', '')
            prompt = data.get('prompt', '')
            
            if not api_key or not prompt:
                self.send_error_response(400, 'Missing apiKey or prompt')
                return
            
            url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': api_key
            }
            body = {
                'model': 'glm-4-flash',
                'messages': [
                    {'role': 'system', 'content': '你是国学研究专家，擅长创作自媒体内容。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.8
            }
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                url,
                data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            if e.code == 429:
                self.send_error_response(429, 'API请求过于频繁，请稍后再试')
            elif e.code == 401:
                self.send_error_response(401, 'API Key无效')
            else:
                self.send_error_response(e.code, f'API错误: {e.code}')
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message, 'code': code}, ensure_ascii=False).encode('utf-8'))
