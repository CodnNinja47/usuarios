import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import quote_plus
import hashlib
import datetime

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.140 DuckDuckGo/5 Safari/537.36"
]

PLATFORMS = {
    "Facebook": ["facebook.com", "fb.com"],
    "YouTube": ["youtube.com", "youtu.be"],
    "Instagram": ["instagram.com"],
    "TikTok": ["tiktok.com"],
    "GitHub": ["github.com"],
    "Telegram": ["t.me", "telegram.org"],
    "Twitter": ["twitter.com", "x.com"],
    "Reddit": ["reddit.com"],
    "LinkedIn": ["linkedin.com"],
    "Pinterest": ["pinterest.com"],
    "Snapchat": ["snapchat.com"],
    "Twitch": ["twitch.tv"],
    "Steam": ["steamcommunity.com", "steampowered.com"],
    "DeviantArt": ["deviantart.com"],
    "Medium": ["medium.com"],
    "Flickr": ["flickr.com"]
}

TIMEOUT = 15
MAX_RESULTS = 30

def buscar(usuario):
    """Main search function that takes a username and returns search results"""
    variations = generate_username_variations(usuario)
    all_results = []
    
    for variation in variations:
        results = search_duckduckgo(variation)
        all_results.extend(results)
    
    classified = classify_results(all_results)
    classified = remove_duplicates(classified)
    
    return {
        "username": usuario,
        "date": datetime.datetime.now().isoformat(),
        "variations": variations,
        "results": classified
    }

def generate_username_variations(username):
    """Generate different username variations for more comprehensive searching"""
    variations = {
        username,
        username.replace(' ', ''),
        username.replace(' ', '_'),
        username.replace(' ', '.'),
        username.replace(' ', '-'),
        f"{username}_",
        f"{username}-",
        f"{username}.",
        f"{username}1",
        f"{username}123",
        f"{username}2023",
        f"{username}2024",
        username.replace('a', '4').replace('e', '3').replace('i', '1').replace('o', '0'),
        username.lower(),
        username.upper(),
        username.title(),
        username[::-1],  # reversed
        f"real{username}",
        f"official{username}",
        f"the{username}",
        f"{username}official"
    }
    return [v for v in variations if v and len(v) <= 30]

def search_duckduckgo(query):
    """Perform actual search using DuckDuckGo dorks"""
    session = requests.Session()
    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result', limit=MAX_RESULTS):
            title = result.find('a', class_='result__a').get_text(strip=True)
            link = parse_ddg_link(result.find('a', class_='result__a')['href'])
            
            if link and not link.startswith('https://duckduckgo.com'):
                results.append({
                    "title": title,
                    "url": link,
                    "variation": query,
                    "hash": create_result_hash(title, link)
                })
        
        return results
    except Exception as e:
        print(f"Error searching for {query}: {str(e)}")
        return []

def parse_ddg_link(link):
    """Parse DuckDuckGo redirect links to get the final URL"""
    if link.startswith('//'):
        link = 'https:' + link
        
    if link.startswith('/l/?uddg='):
        # Extraer la URL codificada
        match = re.search(r'/l/\?uddg=(.*?)(?:&|$)', link)
        if match:
            link = unquote(match.group(1))
        else:
            return None
    
    # Limpiar parámetros de tracking comunes
    clean_link = re.sub(r'(&|\?)utm_[^&]+', '', link)
    clean_link = re.sub(r'(&|\?)fbclid=[^&]+', '', clean_link)
    clean_link = re.sub(r'(&|\?)ref=[^&]+', '', clean_link)
    
    return clean_link.split('&')[0].split('?')[0]

def classify_results(results):
    """Classify results by platform"""
    classification = {platform: [] for platform in PLATFORMS}
    classification["Others"] = []
    
    for result in results:
        url = result["url"].lower()
        found = False
        
        for platform, domains in PLATFORMS.items():
            if any(domain.lower() in url for domain in domains):
                classification[platform].append(result)
                found = True
                break
        
        if not found:
            classification["Others"].append(result)
    
    return classification

def remove_duplicates(classified_results):
    """Remove duplicate results based on URL/title hash"""
    unique_results = {platform: [] for platform in classified_results}
    seen_hashes = set()
    
    for platform, results in classified_results.items():
        for result in results:
            if result["hash"] not in seen_hashes:
                unique_results[platform].append(result)
                seen_hashes.add(result["hash"])
    
    return unique_results

def create_result_hash(title, url):
    """Create unique hash for a result to identify duplicates"""
    return hashlib.md5(f"{title}{url}".encode()).hexdigest()
