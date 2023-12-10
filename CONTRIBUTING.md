# CONTRIBUTING

## How to run the dockerfile manually

```
Build container
	docker build -t rest-apis-flask-python .

Run docker using container mapped to a volume
	docker run -dp 5000:5000 -w /app -v "$(pwd):/app" rest-apis-flask-python sh -c "flask run --host 0.0.0.0"
	
```
