# FastAPI Model Serving

1. Follow the [documentation](https://fastapi.tiangolo.com/) to install fastapi
2. Start the server

```bash
uvicorn app:app --reload
```

3. Test the server

```bash
curl -X POST localhost:8000 -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentance"]}'

curl 127.0.0.1:8000
```

4. Check the generated docs: http://127.0.0.1:8000/docs

5. Run tests

```bash
python -m pytest
```

