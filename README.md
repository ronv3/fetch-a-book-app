# Fetch-a-Book App — Quick-Start Guide

This document walks you from **fresh machine → running three-service stack** in a few minutes.
---

## 1 · Prerequisites

* **Git** 2.30 +
* **Python** 3.8 + on your PATH (for local development only)
* **Docker Engine** 20 + & **Docker Compose** (plugin or standalone)
* GitHub account with write access to the repository

---

## 2 · Clone the repository

```bash
git clone git@github.com:ronv3/fetch-a-book-app.git
cd fetch-a-book-app
```

---

## 3 · (Optional) Create & activate a Python virtual environment  

Skip this whole step if you’ll run everything only inside Docker.

```bash
python3 -m venv .venv            # Windows:  py -3 -m venv .venv
source .venv/bin/activate        # Windows PS:  .venv\Scripts\Activate.ps1
pip install -r hs12-flask-api-raamatud/requirements.txt
pip install -r hs12-flask-api-raamatute-otsing/requirements.txt
```

---

## 4 · Build Docker images manually (one-off)

From the repo root:

```bash
# Books API
docker build -f hs12-flask-api-raamatud/Dockerfile \
             -t hs12-books-api:latest              \
             ./hs12-flask-api-raamatud

# Search API
docker build -f hs12-flask-api-raamatute-otsing/Dockerfile \
             -t hs12-books-search:latest                   \
             ./hs12-flask-api-raamatute-otsing

# Front-end
docker build -f hs12-frontend/Dockerfile \
             -t hs12-frontend:latest     \
             ./hs12-frontend
```

---

## 5 · Spin everything up with Docker Compose

A ready-made **`docker-compose.yml`** lives at the project root:

```yaml
version: "3.9"

services:
  api:
    build: ./hs12-flask-api-raamatud
    container_name: books-api
    environment:
      - FLASK_APP=hs12-flask-api-raamatud.py
      - FLASK_ENV=production
    ports: ["5000:5000"]
    networks: [backend]

  search:
    build: ./hs12-flask-api-raamatute-otsing
    container_name: books-search
    environment:
      - FLASK_APP=hs12-flask-api-raamatute-otsing.py
      - FLASK_ENV=production
    ports: ["5001:5000"]
    networks: [backend]

  frontend:
    build: ./hs12-frontend
    container_name: books-web
    depends_on: [api, search]
    ports: ["8080:80"]
    networks: [backend]

networks:
  backend:
```

Start the whole stack:

```bash
docker compose up --build -d
```

Verify:

* **Front-end:** <http://localhost:8080/>  
* **Books API:** <http://localhost:5001/>  
* **Search API:** <http://localhost:5002/>

Shut everything down & remove anonymous volumes:

```bash
docker compose down -v
```

---

## 6 · Live-reload while coding (optional)

Create **`docker-compose.override.yml`**; Docker Compose loads it automatically:

```yaml
services:
  api:
    volumes:
      - ./hs12-flask-api-raamatud:/app
    command: flask run --host=0.0.0.0 --reload

  search:
    volumes:
      - ./hs12-flask-api-raamatute-otsing:/app
    command: flask run --host=0.0.0.0 --reload
```

Now each save in the `hs12-*` folders triggers an automatic reload inside the running container.

---

## 7 · Everyday Docker Compose commands

| Task                              | Command                                                            |
|-----------------------------------|--------------------------------------------------------------------|
| Check container status            | `docker compose ps`                                                |
| Tail live logs                    | `docker compose logs -f`                                           |
| Rebuild only the Books API image  | `docker compose build api`                                         |
| Purge everything & reclaim space  | `docker compose down -v && docker system prune -f`                 |

---

## 8 · Troubleshooting cheat-sheet

| Symptom                                   | Likely fix                                                                                                      |
|-------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| **Port already in use**                   | Change the *host* half of any `ports:` mapping—e.g. `8081:80`, `5002:5000`.                                      |
| **ModuleNotFoundError when container up** | Add the missing package to that service’s `requirements.txt`, then `docker compose build <service>` again.       |
| **Frontend CORS errors**                  | Enable CORS in Flask via `flask_cors` *or* proxy API paths through Nginx (see `hs12-frontend/nginx.conf`).       |
| **Code changes not visible**              | Rebuild the image or enable live-reload with the override file (Section 6).                                      |

---

### 🎉 You’re ready!

Clone the repo, run `docker compose up --build -d`, and start hacking on **Fetch-a-Book** with an isolated, reproducible stack. Happy coding!
