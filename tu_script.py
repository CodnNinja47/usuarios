import requests
import urllib.parse
import concurrent.futures
import random
import time
from typing import Dict, Union, List

def generar_dork(dork: str) -> str:
    """Genera el query de búsqueda para la API"""
    return urllib.parse.quote_plus(dork)

def buscar_en_plataforma(plataforma: str, dork: str, usuario: str) -> Dict[str, Union[List[str], str]]:
    """Realiza la búsqueda para una plataforma individual usando la API de DuckDuckGo"""
    try:
        # Configuración avanzada de headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Referer': 'https://duckduckgo.com/',
            'DNT': '1'
        }
        
        # Pequeño delay aleatorio para evitar bloqueos
        time.sleep(random.uniform(0.5, 1.5))
        
        # Usar la API oficial de DuckDuckGo en lugar de scraping HTML
        api_url = f"https://api.duckduckgo.com/?q={generar_dork(dork)}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Procesar resultados de la API
        resultados = []
        if 'Results' in data and data['Results']:
            for result in data['Results']:
                if usuario.lower() in result['FirstURL'].lower():
                    resultados.append(result['FirstURL'])
        
        # También verificar en RelatedTopics si existen
        if 'RelatedTopics' in data and data['RelatedTopics']:
            for topic in data['RelatedTopics']:
                if 'FirstURL' in topic and usuario.lower() in topic['FirstURL'].lower():
                    resultados.append(topic['FirstURL'])
        
        return {plataforma: resultados if resultados else "No se encontraron resultados"}
        
    except requests.exceptions.Timeout:
        return {plataforma: "Error: Tiempo de espera agotado"}
    except requests.exceptions.HTTPError as e:
        return {plataforma: f"Error HTTP: {str(e)}"}
    except Exception as e:
        return {plataforma: f"Error en la búsqueda: {str(e)}"}

def buscar(usuario: str) -> Dict[str, Union[str, Dict]]:
    """Función principal que busca un usuario en múltiples plataformas"""
    plataformas = {
        'GitHub': f'site:github.com "{usuario}"',
        'Twitter': f'site:twitter.com "{usuario}"',
        'Instagram': f'site:instagram.com "{usuario}"',
        'Facebook': f'site:facebook.com "{usuario}"',
        'LinkedIn': f'site:linkedin.com "{usuario}"',
        'Reddit': f'site:reddit.com "{usuario}"',
        'YouTube': f'site:youtube.com "{usuario}"',
        'Pinterest': f'site:pinterest.com "{usuario}"',
        'TikTok': f'site:tiktok.com "@{usuario}"',
        'Twitch': f'site:twitch.tv "{usuario}"',
        'Telegram': f'site:t.me "{usuario}"',
        'Medium': f'site:medium.com "@{usuario}"',
        'Dev.to': f'site:dev.to "{usuario}"',
        'Flickr': f'site:flickr.com "{usuario}"'
    }
    
    resultados = {}
    
    # Búsqueda paralela con límite de workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i, (plataforma, dork) in enumerate(plataformas.items()):
            futures.append(executor.submit(buscar_en_plataforma, plataforma, dork, usuario))
            # Pequeña pausa cada 3 solicitudes para evitar bloqueos
            if i % 3 == 0:
                time.sleep(random.uniform(1, 2))
        
        for future in concurrent.futures.as_completed(futures):
            resultados.update(future.result())
    
    # Calcular estadísticas
    stats = {
        "total_platforms": len(plataformas),
        "total_found": sum(1 for v in resultados.values() if isinstance(v, list) and v),
        "total_errors": sum(1 for v in resultados.values() if isinstance(v, str) and "Error" in v),
        "total_not_found": sum(1 for v in resultados.values() if v == "No se encontraron resultados")
    }
    
    return {
        "username": usuario,
        "results": resultados,
        "stats": stats
    }
