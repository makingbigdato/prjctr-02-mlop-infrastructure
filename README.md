# Infrastructure for the course

## 01 Dockerfile

PR 1: write a dummy docker file with a simple server and push it to your docker hub registry

Docker image is hosted on the Docker hub:

https://hub.docker.com/repository/docker/yevhenk10s/prjctr02-infrastructure

### Quick Start

1. Pull the image
```bash
docker pull yevhenk10s/prjctr02-infrastructure:latest
```

2. Start server manually
```bash
docker run -p 5000:5000 yevhenk10s/prjctr02-infrastructure:latest
```

3. Test server status
```bash
curl localhost:5000
curl -X POST localhost:5000 -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentence"]}'
```

