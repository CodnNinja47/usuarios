import requests
from bs4 import BeautifulSoup
import urllib.parse
import concurrent.futures
from typing import Dict, Union, List

def generar_dork_url(dork: str) -> str:
    """Genera la URL de búsqueda para un dork dado"""
    query = urllib.parse.quote_plus(dork)
    return f"https://html.duckduckgo.com/html/?q={query}"

def extraer_links(soup: BeautifulSoup, usuario: str, max_results: int = 5) -> Union[List[str], str]:
    """Extrae y filtra los links relevantes de los resultados de búsqueda"""
    links = soup.find_all('a', class_='result__url')
    encontrados = []
    
    for link in links[:max_results]:  # Limitar resultados desde el inicio
        href = link.get('href', '')
        if usuario.lower() in href.lower() or usuario.lower() in link.text.lower():
            encontrados.append(href)
    
    return encontrados if encontrados else "No se encontraron resultados"

def buscar_en_plataforma(plataforma: str, dork: str, usuario: str) -> Dict[str, Union[List[str], str]]:
    """Realiza la búsqueda para una plataforma individual"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = generar_dork_url(dork)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return {plataforma: extraer_links(soup, usuario)}
        
    except requests.exceptions.Timeout:
        return {plataforma: "Error: Tiempo de espera agotado"}
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
    
    # Búsqueda paralela
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(buscar_en_plataforma, plataforma, dork, usuario)
            for plataforma, dork in plataformas.items()
        ]
        
        for future in concurrent.futures.as_completed(futures):
            resultados.update(future.result())
    
    # Calcular estadísticas
    stats = {
        "total_platforms": len(plataformas),
        "total_found": sum(1 for v in resultados.values() if isinstance(v, list)),
        "total_errors": sum(1 for v in resultados.values() if isinstance(v, str) and "Error" in v),
        "total_not_found": sum(1 for v in resultados.values() if v == "No se encontraron resultados")
    }
    
    return {
        "username": usuario,
        "results": resultados,
        "stats": stats
    }
