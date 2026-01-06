# AWS Cognito Setup Guide

## Step 1: Configure Cognito (AWS Console)

### Create User Pool

1. Go to AWS Cognito → Create User Pool
2. **Sign-in options:** Email
3. **MFA:** Optional (recommended: Optional MFA)
4. **Self-service sign-up:** Enable if you want users to register themselves

### App Client Configuration

1. **App client name:** `mathwizard-web`
2. **Client secret:** Generate a client secret ✅
3. **Authentication flows:** Check "ALLOW_USER_PASSWORD_AUTH"

### Hosted UI Configuration

**Callback URLs (Allowed redirect URIs):**
```
http://localhost:8000/callback
https://mathwizard.nl/callback
```

**Sign out URLs:**
```
http://localhost:8000/login
https://mathwizard.nl/login
```

**OAuth 2.0 Grant Types:**
- ✅ Authorization code grant

**OAuth Scopes:**
- ✅ openid
- ✅ profile  
- ✅ email

### Domain Name

**Cognito domain:** Choose a prefix (e.g., `mathwizard-auth`)
- Your domain will be: `mathwizard-auth.auth.us-east-1.amazoncognito.com`

---

## Step 2: Update Your `.env` File

Add these variables to your `.env` file:

```bash
# Remove old password auth
# APP_PASSWORD=...  ← Delete this

# Add Cognito configuration
COGNITO_DOMAIN=mathwizard-auth.auth.us-east-1.amazoncognito.com
COGNITO_CLIENT_ID=<from-cognito-console>
COGNITO_CLIENT_SECRET=<from-cognito-console>
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxx
COGNITO_REGION=us-east-1

# For local development
COGNITO_REDIRECT_URI=http://localhost:8000/callback

# For production (set in AWS or Docker)
# COGNITO_REDIRECT_URI=https://mathwizard.nl/callback
```

---

## Step 3: Install Dependencies

```bash
uv sync
```

This installs:
- `authlib` - AWS-recommended OAuth library with automatic JWT verification

---

## Step 4: Test Locally

```bash
# Start the app
docker compose up
# Or: ./scripts/dev-local.sh

# Visit http://localhost:8000
# Click login → Should redirect to Cognito
# Enter credentials → Should redirect back and authenticate
```

---

## Step 5: Create Test User

In AWS Cognito Console:
1. Go to your User Pool
2. **Users** → Create user
3. Enter email and temporary password
4. User will be prompted to change password on first login

---

## How It Works

### Old Flow (Password):
```
1. Visit /login
2. Enter password
3. Check against APP_PASSWORD
4. Set session
```

### New Flow (Cognito + authlib):
```
1. Visit /login
2. authlib redirects to Cognito hosted UI
3. User logs in on Cognito
4. Cognito redirects to /callback with code
5. authlib exchanges code, verifies JWT automatically
6. User info stored in encrypted session cookie
7. Redirect to /
```

---

## Troubleshooting

### "Invalid redirect_uri"
- Check callback URL in Cognito matches COGNITO_REDIRECT_URI exactly
- Must include http:// or https://
- No trailing slash

### "Client authentication failed"
- Check COGNITO_CLIENT_SECRET is correct
- Make sure client secret was generated in Cognito

### "User does not exist"
- Create a test user in Cognito console
- Or enable self-service sign-up

### Local development not redirecting
- Make sure COGNITO_REDIRECT_URI=http://localhost:8000/callback (not https)
- Check Docker port mapping (8000:8000)

---

## Production Deployment

For AWS App Runner:

1. Set environment variables in App Runner:
   ```
   COGNITO_REDIRECT_URI=https://mathwizard.nl/callback
   ```

2. Update callback URL in Cognito to include production domain

3. Deploy:
   ```bash
   ./scripts/deploy.sh
   ```

---

## Security Notes

- ✅ **No password storage** - Handled by Cognito
- ✅ **Secure tokens** - JWT signed by AWS
- ✅ **Session expiration** - Still 24 hours max
- ✅ **MFA support** - Can enable in Cognito
- ✅ **Password reset** - Built into Cognito UI


