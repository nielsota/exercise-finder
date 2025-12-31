# Scripts

Helper scripts for development and deployment.

## Development Scripts

### `dev_deploy.sh`
Start local development environment with hot-reload.

```bash
# Start normally
./scripts/dev_deploy.sh

# Rebuild image and start fresh
./scripts/dev_deploy.sh --rebuild
```

**Features:**
- Auto-restart on code changes
- Logs follow by default (Ctrl+C to exit)
- Container keeps running after exiting logs
- Access at http://localhost:8000

**Use when:**
- Starting a dev session
- Testing route changes in Docker
- Debugging container issues

### `dev_stop.sh`
Stop the development environment.

```bash
./scripts/dev_stop.sh
```

### `dev_logs.sh`
View logs from running container.

```bash
./scripts/dev_logs.sh
```

## Production Scripts

### `deploy.sh`
Deploy to AWS App Runner via ECR.

```bash
./scripts/deploy.sh
```

**What it does:**
1. Builds Docker image for linux/amd64
2. Tags image for ECR
3. Pushes to ECR
4. App Runner auto-deploys

**Prerequisites:**
- AWS CLI configured
- ECR repository created
- App Runner service configured

## Quick Reference

| Task | Command |
|------|---------|
| Start dev | `./scripts/dev_deploy.sh` |
| Stop dev | `./scripts/dev_stop.sh` |
| View logs | `./scripts/dev_logs.sh` |
| Deploy to prod | `./scripts/deploy.sh` |
| Rebuild dev image | `./scripts/dev_deploy.sh -r` |

## Tips

- **Hot-reload**: Changes to `src/` auto-restart the server
- **Logs**: Container keeps running after `Ctrl+C` in logs
- **Stop**: Always use `dev_stop.sh` to clean up properly
- **Rebuild**: Use `-r` flag if dependencies changed

