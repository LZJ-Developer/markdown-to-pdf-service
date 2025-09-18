#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown转DOCX API服务 - 调用后端的MinIO上传接口
"""
import os
import sys
import tempfile
import base64
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import traceback
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加你的模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入你的转换器函数
from markdown_converter_api import convert_markdown_file

# 创建FastAPI应用
app = FastAPI(
    title="Markdown转DOCX API",
    description="将Markdown转换为DOCX并通过后端接口上传",
    version="1.0.0"
)

# ========== 配置区域 ==========
# 后端服务配置
BACKEND_CONFIG = {
    'base_url': os.getenv('MINIO_URL', 'http://47.92.52.125:8089/api/'),
    'upload_endpoint': 'uploadFile',
    'download_endpoint': 'downloadFile',
    'api_token': os.getenv('SANDBOX_API_TOKEN', '')  # 如果需要token认证
}

# ========== 请求/响应模型 ==========
class ConvertRequest(BaseModel):
    """转换请求"""
    session_id: str
    file: str  # Base64编码的markdown内容
    filename: Optional[str] = None  # 可选的文件名
    title: Optional[str] = None  # 可选的文档标题

class ResponseData(BaseModel):
    """响应数据"""
    session_id: str
    file: str  # 文件下载URL

class ConvertResponse(BaseModel):
    """标准响应格式"""
    code: int
    data: Optional[ResponseData] = None
    msg: str

# ========== 核心功能函数 ==========
def markdown_to_docx(markdown_content: str, filename: str = "document", title: Optional[str] = None) -> str:
    """
    将Markdown内容转换为DOCX文件
    
    Args:
        markdown_content: Markdown文本内容
        filename: 输出文件名（不含扩展名）
        title: 文档标题
    
    Returns:
        生成的DOCX文件路径
    """
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 保存markdown文件
        markdown_filename = f"{filename}.md"
        markdown_path = os.path.join(temp_dir, markdown_filename)
        
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # 准备转换选项
        template_options = {}
        if title:
            template_options["title"] = title
        
        # 执行转换
        result = convert_markdown_file(
            markdown_path=temp_dir,
            markdown_filename=markdown_filename,
            output_format="docx",
            template_options=template_options
        )
        
        if not result["success"]:
            raise Exception(result.get("error_msg", "转换失败"))
        
        return result["output_path"]
        
    except Exception as e:
        # 清理临时文件
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

async def upload_file_to_backend(session_id: str, filepath: str) -> dict:
    """
    调用后端的上传接口上传文件到MinIO
    
    Args:
        session_id: 会话ID
        filepath: 本地文件路径
    
    Returns:
        后端返回的响应数据
    """
    filename = os.path.basename(filepath)
    url = BACKEND_CONFIG['base_url'] + BACKEND_CONFIG['upload_endpoint']
    
    data = {
        'session_id': session_id
    }
    
    # 如果有API Token，添加到headers
    headers = {}
    if BACKEND_CONFIG.get('api_token'):
        headers['Authorization'] = f"Bearer {BACKEND_CONFIG['api_token']}"
    
    try:
        # 读取文件
        with open(filepath, 'rb') as f:
            files = {
                'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url, 
                    files=files, 
                    data=data,
                    headers=headers
                )
                
        response.raise_for_status()
        response_data = response.json()
        print(f"上传响应: {response_data}")
        
        return response_data
        
    except httpx.HTTPStatusError as e:
        raise Exception(f"上传失败，HTTP状态码: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"调用后端上传接口失败: {str(e)}")

async def get_download_url(session_id: str, filename: str) -> str:
    """
    从后端获取真正的OSS下载URL
    
    Args:
        session_id: 会话ID
        filename: 文件名
    
    Returns:
        OSS签名下载URL
    """
    download_api = f"{BACKEND_CONFIG['base_url']}{BACKEND_CONFIG['download_endpoint']}"
    params = {
        'session_id': session_id,
        'file_name': filename
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(download_api, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0 and result.get('data'):
                # 返回真正的OSS URL
                return result['data']
            else:
                # 如果获取失败，返回原始的API URL
                return f"{download_api}?session_id={session_id}&file_name={filename}"
                
    except Exception as e:
        print(f"获取下载URL失败: {e}")
        # 失败时返回原始URL
        return f"{download_api}?session_id={session_id}&file_name={filename}"

# ========== API端点 ==========
@app.get("/")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Markdown to DOCX Converter",
        "version": "1.0.0",
        "backend_url": BACKEND_CONFIG['base_url']
    }

@app.post("/api/markdown/convert", response_model=ConvertResponse)
async def convert_markdown_to_docx(request: ConvertRequest):
    """
    将Base64编码的Markdown转换为DOCX并上传到后端
    
    处理流程：
    1. 解码Base64获取Markdown内容
    2. 转换Markdown为DOCX
    3. 调用后端上传接口
    4. 返回下载地址
    """
    docx_path = None
    temp_dir = None
    
    try:
        # 1. 解码Base64内容
        try:
            markdown_content = base64.b64decode(request.file).decode('utf-8')
        except Exception as e:
            return ConvertResponse(
                code=1,
                data=None,
                msg=f"解码失败: 无法解码Base64内容 - {str(e)}"
            )
        
        # 2. 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = request.filename or f"document_{timestamp}"
        # 移除可能的.md扩展名
        if filename.endswith('.md'):
            filename = filename[:-3]
        
        # 3. 转换Markdown为DOCX
        print(f"开始转换: {filename}")
        docx_path = markdown_to_docx(
            markdown_content=markdown_content,
            filename=filename,
            title=request.title
        )
        print(f"转换成功: {docx_path}")
        
        # 4. 调用后端上传接口
        print(f"开始上传到后端...")
        upload_response = await upload_file_to_backend(request.session_id, docx_path)
        
        # 5. 解析后端返回的数据
        # 假设后端返回格式为: {"code": 0, "data": "filename或其他信息", "msg": "ok"}
        if upload_response.get('code') != 0:
            return ConvertResponse(
                code=upload_response.get('code', 1),
                data=None,
                msg=upload_response.get('msg', '后端上传失败')
            )
        
        # 6. 获取真正的下载URL
        file_info = upload_response.get('data')
        # 如果返回的是文件名，需要调用downloadFile接口获取真正的URL
        if isinstance(file_info, str) and not file_info.startswith('http'):
            download_url = await get_download_url(request.session_id, file_info)
        else:
            # 如果已经是URL，直接使用
            download_url = file_info
        
        print(f"文件下载URL: {download_url}")
        
        # 7. 返回成功响应
        return ConvertResponse(
            code=0,
            data=ResponseData(
                session_id=request.session_id,
                file=download_url
            ),
            msg="ok"
        )
        
    except Exception as e:
        traceback.print_exc()
        return ConvertResponse(
            code=1,
            data=None,
            msg=f"处理失败: {str(e)}"
        )
    finally:
        # 清理临时文件
        if docx_path and os.path.exists(docx_path):
            try:
                # 获取临时目录
                temp_dir = os.path.dirname(docx_path)
                import shutil
                shutil.rmtree(temp_dir)
                print(f"清理临时文件: {temp_dir}")
            except:
                pass

@app.get("/api/test")
async def test_api():
    """测试API连通性和配置"""
    tests = {
        "api_status": "running",
        "backend_url": BACKEND_CONFIG['base_url'],
        "converter_available": False
    }
    
    # 测试转换器是否可用
    try:
        from common.base_converter import MarkdownConverter
        converter = MarkdownConverter()
        tests["converter_available"] = True
        tests["supported_formats"] = converter.get_supported_formats()
    except:
        pass
    
    # 测试后端连通性
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 尝试访问后端
            response = await client.get(BACKEND_CONFIG['base_url'].replace('/api/', ''))
            tests["backend_reachable"] = response.status_code < 500
    except:
        tests["backend_reachable"] = False
    
    return tests

if __name__ == "__main__":
    # 启动服务器
    port = int(os.getenv("PORT", 8089))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 50)
    print(f"启动 Markdown转DOCX API 服务")
    print(f"访问地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"健康检查: http://{host}:{port}/")
    print(f"测试端点: http://{host}:{port}/api/test")
    print(f"后端地址: {BACKEND_CONFIG['base_url']}")
    print("=" * 50)
    
    uvicorn.run(app, host=host, port=port, reload=False)