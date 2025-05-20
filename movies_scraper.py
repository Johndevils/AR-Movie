import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mkvcinemas.pet"

def search_movies(query):
    movies_list = []
    url_map = {}
    search_url = f"{BASE_URL}/?s={query.replace(' ', '+')}"

    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        movies = soup.find_all("a", {'class': 'ml-mask jt'})

        for idx, movie in enumerate(movies):
            title_tag = movie.find("span", {'class': 'mli-info'})
            if title_tag:
                movie_id = f"link{idx}"
                movie_title = title_tag.text.strip()
                movie_url = movie['href']
                movies_list.append({
                    "id": movie_id,
                    "title": movie_title
                })
                url_map[movie_id] = movie_url
    except Exception as e:
        print(f"Error during movie search: {e}")

    return movies_list, url_map

def get_movie(movie_id, url_map):
    movie_details = {}
    try:
        movie_url = url_map.get(movie_id)
        if not movie_url:
            return {"error": "Movie ID not found."}

        response = requests.get(movie_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("div", {'class': 'mvic-desc'}).h3.text.strip()
        img = soup.find("div", {'class': 'mvic-thumb'}).find("img")["src"]
        links = [a['href'] for a in soup.select("div.sbox > a")]

        movie_details = {
            "title": title,
            "image": img,
            "links": links
        }
    except Exception as e:
        movie_details = {"error": f"Error fetching movie details: {e}"}

    return movie_details
