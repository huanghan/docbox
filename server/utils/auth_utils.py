"""
认证工具函数
"""

from typing import Optional


def verify_api_key(api_key: Optional[str], valid_keys: list = None) -> bool:
    """验证API密钥"""
    if not valid_keys:
        # 如果没有设置密钥要求，则不验证
        return True
    
    if not api_key:
        return False
    
    return api_key in valid_keys


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """从Authorization头中提取Bearer token"""
    if not authorization:
        return None
    
    if authorization.startswith("Bearer "):
        return authorization[7:]  # 去掉"Bearer "前缀
    
    return None


def generate_api_key() -> str:
    """生成API密钥"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32)) 