import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote
from typing import Dict, List, Optional

class UserSearchEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.platforms = {
            'github': {
                'url': 'https://github.com/{}',
                'validation': lambda soup: not soup.find('div', class_='js-profile-editable-replace')
            },
            'twitter': {
                'url': 'https://twitter.com/{}',
                'validation': lambda soup: soup.find('div', {'data-testid': 'emptyState'}) is not None
            },
            'instagram': {
                'url': 'https://www.instagram.com/{}/',
                'validation': lambda soup: 'Sorry, this page isn\'t available.' in str(soup)
            },
            'reddit': {
                'url': 'https://www.reddit.com/user/{}',
                'validation': lambda soup: 'Sorry, nobody on Reddit goes by that name.' in str(soup)
            }
        }
    
    def _check_platform(self, username: str, platform: str) -> Dict[str, str]:
        """Verifica si un usuario existe en una plataforma específica."""
        platform_data = self.platforms.get(platform)
        if not platform_data:
            return {'platform': platform, 'exists': False, 'error': 'Platform not supported'}
        
        try:
            url = platform_data['url'].format(quote(username))
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return {'platform': platform, 'exists': False, 'url': url}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if platform_data['validation'](soup):
                return {'platform': platform, 'exists': False, 'url': url}
            
            return {'platform': platform, 'exists': True, 'url': url}
        
        except Exception as e:
            return {'platform': platform, 'exists': False, 'error': str(e), 'url': url}

def buscar(usuario: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Busca un nombre de usuario en múltiples plataformas.
    
    Args:
        usuario (str): Nombre de usuario a buscar
        
    Returns:
        Dict: Diccionario con los resultados por plataforma
        Ejemplo:
        {
            "username": "ejemplo",
            "results": [
                {"platform": "github", "exists": True, "url": "https://github.com/ejemplo"},
                {"platform": "twitter", "exists": False, "url": "https://twitter.com/ejemplo"}
            ],
            "stats": {
                "total": 4,
                "found": 1,
                "not_found": 3
            }
        }
    """
    engine = UserSearchEngine()
    results = []
    
    for platform in engine.platforms:
        result = engine._check_platform(usuario, platform)
        results.append(result)
    
    stats = {
        'total': len(results),
        'found': sum(1 for r in results if r['exists']),
        'not_found': sum(1 for r in results if not r['exists'])
    }
    
    return {
        'username': usuario,
        'results': results,
        'stats': stats
    }
