# boolean-ms
Boolean™ micro service

## Docker Deployment

This project is automatically built and deployed to Docker Hub when tags are pushed to the repository.

### Docker Hub Repository

Images are published to: [https://hub.docker.com/repository/docker/adrian4096/prpo-app/](https://hub.docker.com/repository/docker/adrian4096/prpo-app/)

### Creating a Release

To trigger a deployment:

1. Create and push a git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. The GitHub Actions workflow will automatically:
   - Build a multi-architecture Docker image (amd64, arm64)
   - Push the image to Docker Hub with the following tags:
     - The exact git tag (e.g., `v1.0.0`)
     - Semantic version tags (e.g., `1.0.0`, `1.0`, `1`) for semver-compatible tags
     - `latest` tag for releases from the default branch

### Required Secrets

The following GitHub secrets must be configured in the repository settings for deployment to work:

- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - A Docker Hub access token (create at https://hub.docker.com/settings/security)

### Running the Docker Image

```bash
docker pull adrian4096/prpo-app:latest
docker run -p 8000:8000 adrian4096/prpo-app:latest
```

The service will be available at http://localhost:8000
