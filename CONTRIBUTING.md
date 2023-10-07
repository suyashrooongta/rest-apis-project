# CONTRIBUTING

## How to run the Dockerfile locally

```
docker build -t rest-apis-flask-python .                        

docker run -dp 5000:5000 -w /app -v "$(pwd):/app" rest-apis-flask-python sh -c "flask run --host 0.0.0.0" 
```
