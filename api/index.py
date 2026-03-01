# Vercel Serverless Function
from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import ssl
import os

# 导入敏感词模块
import sys
sys.path.insert(0, os.path.dirname(__file__))
from sensitive_words import get_prompt_addition, clean_for_douyin

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
        """处理热点数据请求"""
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
            print(f"[热点API错误] {e}")
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
            
            # 添加合规要求
            prompt_with_compliance = prompt + get_prompt_addition()
            
            # 调用智谱AI
            response_data = call_zhipu_api(api_key, prompt_with_compliance)
            
            # 过滤敏感词
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                cleaned_result = clean_for_douyin(content)
                response_data['choices'][0]['message']['content'] = cleaned_result['cleaned_text']
            
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[错误] API处理异常: {e}")
            print(f"[错误详情] {error_detail}")
            self.send_error_response(500, str(e))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}, ensure_ascii=False).encode('utf-8'))

def call_zhipu_api(api_key, prompt):
    """调用智谱AI API"""
    url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': api_key
    }
    
    data = {
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
        data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"[智谱API错误] HTTP {e.code}: {error_body}")
        
        if e.code == 429:
            raise Exception('API请求过于频繁，请稍后再试')
        elif e.code == 401:
            raise Exception('API Key无效，请检查Key是否正确')
        else:
            raise Exception(f'API错误: HTTP {e.code}')
