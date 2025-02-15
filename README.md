# Run Docker File
```bash
cd tds-project-1/
docker build -t tds-project-1 .
docker images 
podman run --rm -p 8000:8000 -e AIPROXY_TOKEN=$AIPROXY_TOKEN $IMAGE_NAME
```
$IMAGE_NAME will be whaterever here "tds-project-1"

# Troubleshoot
## Running the Container with Podman

To run the container using Podman, use the following command:

```sh
podman run --rm -p 8000:8000 -e AIPROXY_TOKEN="${AIPROXY_TOKEN}" "${IMAGE_NAME}"
Explanation:
--rm:
Automatically removes the container once it stops.

-p 8000:8000:
Maps port 8000 on your host to port 8000 in the container.
```

-e AIPROXY_TOKEN:
Passes the AIPROXY_TOKEN environment variable to the container.

${IMAGE_NAME}:
The name of the image you want to run.

Prerequisites:
Ensure Podman is installed on your system. For installation instructions, visit the Podman Installation Guide.

Make sure the environment variable AIPROXY_TOKEN is set in your shell. You can verify this by running:

sh
``` bash
echo $AIPROXY_TOKEN
```
The application inside the container should be listening on port 8000.


Example:
sh
``` bash
export AIPROXY_TOKEN="your_token_here"
export IMAGE_NAME="your_image_name_here"
podman run --rm -p 8000:8000 -e AIPROXY_TOKEN="${AIPROXY_TOKEN}" "${IMAGE_NAME}"
```
Troubleshooting:
If the container isn't starting or the environment variable isn't recognized, double-check the following:
The environment variable is correctly set.
Podman has permission to bind to port 8000.
The application inside the container is listening on port 8000.
