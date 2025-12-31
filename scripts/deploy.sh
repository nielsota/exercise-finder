#!/bin/bash
set -e

ECR_URL="841835632701.dkr.ecr.us-east-1.amazonaws.com/mathwizard/exercise-finder"

echo "🔨 Building..."
docker build --platform linux/amd64 -t exercise-finder .

echo "🏷️  Tagging..."
docker tag exercise-finder:latest $ECR_URL:latest

echo "🚀 Pushing..."
docker push $ECR_URL:latest

echo "✅ Done! App Runner will auto-deploy."