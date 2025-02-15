# Run Docker File
```bash
cd tds-project-1/
docker build -t tds-project-1 .
docker images 
podman run --rm -p 8000:8000 -e AIPROXY_TOKEN=$AIPROXY_TOKEN $IMAGE_NAME
```
$IMAGE_NAME will be whaterever here "tds-project-1"
