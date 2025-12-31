# Docker Setup and Workflow

## Overview

This project uses Docker for both local development and production deployment. Understanding the difference between `Dockerfile`, `docker-compose.yml`, and how they're used is important.

## Files

### `Dockerfile`
- **Purpose**: Defines the container image
- **Used for**: BOTH local development AND production
- **Contains**: Build instructions, dependencies, entry point
- **Creates**: A portable container image that runs the same everywhere

### `docker-compose.yml`
- **Purpose**: Local development convenience tool
- **Used for**: LOCAL DEVELOPMENT ONLY
- **Contains**: Development-specific overrides (hot-reload, volume mounts, etc.)
- **NOT used in production** (App Runner doesn't use it)

## Workflows

### Local Development

**Quick Start** (using helper scripts):

```bash
# Start dev environment with hot-reload
./scripts/dev_deploy.sh

# Rebuild image and start fresh
./scripts/dev_deploy.sh --rebuild

# View logs (if not already following)
./scripts/dev_logs.sh

# Stop the environment
./scripts/dev_stop.sh
```

**Manual Docker Compose** (same result):

```bash
# Start the app with hot-reload
docker compose up

# Stop the app
docker compose down

# Follow logs
docker compose logs -f
```

**What happens during dev start:**
1. Reads docker-compose.yml
2. Builds image using Dockerfile
3. Adds dev features:
   - Hot reload (code changes auto-restart)
   - Volume mounts (live code updates)
   - Loads .env.prod file
   - Mounts ~/.aws for SSM access
4. Runs on http://localhost:8000

**Development Features** (from `docker-compose.yml`):
- `--reload --reload-dir /app/src` - Auto-restart on code changes
- `./src:/app/src:ro` - Live code updates without rebuild
- `./data:/app/data:ro` - Access to local data files
- `~/.aws:/root/.aws:ro` - AWS credentials for SSM access

**Example Dev Workflow:**
1. Start: `./scripts/dev_deploy.sh`
2. Edit code in `src/exercise_finder/web/app/routes.py`
3. Save file → uvicorn auto-restarts → refresh browser
4. Stop: `Ctrl+C` or `./scripts/dev_stop.sh`

### Production Deployment

```bash
# 1. Build the production image
docker build --platform linux/amd64 -t exercise-finder:latest .

# 2. Tag for ECR
docker tag exercise-finder:latest <ecr-repo-url>:latest

# 3. Push to ECR
docker push <ecr-repo-url>:latest

# 4. Deploy to App Runner
# - App Runner fetches image from ECR
# - Uses ONLY the Dockerfile (docker-compose.yml is ignored)
# - Environment variables set in AWS console
# - IAM role provides AWS credentials (no ~/.aws needed)
```

**Production Differences**:
- ❌ No docker-compose.yml
- ❌ No volume mounts
- ❌ No hot reload
- ❌ No local .env file
- ✅ Environment variables from App Runner console
- ✅ AWS credentials from IAM instance role
- ✅ Data baked into image or fetched from S3

## Key Differences

| Feature | Local (docker-compose) | Production (App Runner) |
|---------|------------------------|-------------------------|
| Uses docker-compose.yml | ✅ Yes | ❌ No |
| Uses Dockerfile | ✅ Yes | ✅ Yes |
| Hot reload | ✅ Yes | ❌ No |
| Volume mounts | ✅ Yes | ❌ No |
| AWS credentials | ~/.aws mount | IAM role |
| Environment vars | .env.prod file | App Runner console |
| Code changes | Instant | Requires rebuild + redeploy |

## Environment Variables

### Local Development (.env.prod)
```bash
# Required
OPENAI_API_KEY=sk-proj-...
APP_PASSWORD=your-password
SESSION_SECRET_KEY=your-secret

# Optional (AWS credentials from ~/.aws/credentials)
USE_SSM=true
```

### Production (App Runner Console)
```bash
# Required
OPENAI_API_KEY=sk-proj-...
APP_PASSWORD=your-password
SESSION_SECRET_KEY=your-secret
USE_SSM=true

# AWS credentials NOT needed (IAM role provides them)
```

## AWS Credentials

### Local Development
Three options:
1. **Mount ~/.aws** (current setup):
   ```yaml
   volumes:
     - ~/.aws:/root/.aws:ro
   ```

2. **Environment variables** in .env.prod:
   ```bash
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **IAM role** (if running on EC2)

### Production (App Runner)
- **IAM instance role** (recommended)
- Set via: App Runner → Configuration → Security → Instance role
- Policy needed:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ],
        "Resource": "arn:aws:ssm:us-east-1:*:parameter/mathwizard-vector-store-id"
      }
    ]
  }
  ```

## Testing Production Build Locally

You can test the production build locally before deploying:

```bash
# 1. Build production image
docker build --platform linux/amd64 -t exercise-finder:test .

# 2. Run it (without docker-compose)
docker run -p 8080:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e APP_PASSWORD=$APP_PASSWORD \
  -e SESSION_SECRET_KEY=$SESSION_SECRET_KEY \
  -e USE_SSM=true \
  -v ~/.aws:/root/.aws:ro \
  exercise-finder:test

# 3. Test at http://localhost:8080
```

## Common Issues

### "Code changes not showing up"
- **Local**: Make sure docker-compose is running and volumes are mounted
- **Production**: You need to rebuild and redeploy the image

### "AWS credentials not found"
- **Local**: Check `~/.aws/credentials` exists and is mounted
- **Production**: Check IAM role is attached to App Runner service

### "Parameter not found in SSM"
- Check region is correct (parameter is in us-east-1)
- Check IAM permissions allow ssm:GetParameter
- Verify parameter name: `/mathwizard-vector-store-id`

## Best Practices

1. **Never commit credentials** - Use .env files and keep them in .gitignore
2. **Use IAM roles in production** - More secure than access keys
3. **Test production builds locally** - Catch issues before deploying
4. **Keep docker-compose simple** - It's just for dev convenience
5. **Document environment variables** - Use .env.example as template

## Further Reading

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AWS App Runner IAM Roles](https://docs.aws.amazon.com/apprunner/latest/dg/security-iam.html)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

