# Deploy Django User Management API to Render.com

This guide walks you through deploying your Dockerized Django application to Render.com for public access.

## What Changed for Render Deployment

We made these modifications to make your app work on Render:

1. **Updated [playground/settings.py](playground/settings.py)**:
   - Now uses `DATABASE_URL` environment variable (Render's standard)
   - Falls back to individual `DB_*` variables for local Docker
   - Added `RENDER_EXTERNAL_HOSTNAME` to `ALLOWED_HOSTS`

2. **Updated [entrypoint.sh](entrypoint.sh)**:
   - Handles both `DATABASE_URL` (Render) and `DB_HOST` (local Docker)
   - Uses `PORT` environment variable that Render provides
   - Binds Gunicorn to `0.0.0.0:$PORT` instead of hardcoded `8000`

3. **Created [render.yaml](render.yaml)**:
   - Infrastructure-as-code for one-click deployment
   - Defines PostgreSQL database + web service
   - Auto-generates secrets and configures DATABASE_URL

## Prerequisites

- GitHub account with your code pushed
- Render account (free): https://render.com

## Deployment Options

You have **two ways** to deploy:

### **Option 1: Blueprint (render.yaml) - Recommended ✅**
One-click deployment using the render.yaml file.

### **Option 2: Manual Dashboard Setup**
Create services manually through Render Dashboard.

---

## Option 1: Deploy Using Blueprint (Easiest)

### Step 1: Push Code to GitHub

```bash
cd /Users/saurav/Developer/Backend-development/User_management/playground

# Make sure all files are committed
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create Blueprint on Render

1. Go to https://dashboard.render.com
2. Click **Blueprints** in the left sidebar
3. Click **New Blueprint Instance**
4. Select your GitHub repository: `komal2605-2026/playground`
5. Click **Connect**
6. Give your blueprint a name (e.g., "User Management API")
7. Click **Apply**

Render will now:
- Create a PostgreSQL database
- Build your Docker image
- Deploy the web service
- Set up environment variables automatically

### Step 3: Wait for Deployment

The build takes 3-5 minutes. You'll see:
- Database provisioning
- Docker image building
- Container deployment

### Step 4: Get Your Public URL

Once deployed, you'll see:
```
✅ Live: https://user-management-api-xxx.onrender.com
```

### Step 5: Create Superuser (Optional)

1. Go to your service dashboard on Render
2. Click **Shell** tab
3. Run:
```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

### Step 6: Test Your API

```bash
# Test base URL
curl https://your-app-name.onrender.com/

# Test your API endpoints
curl https://your-app-name.onrender.com/api/users/
```

---

## Option 2: Manual Deployment

### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `user-management-db`
   - **Plan**: Free
   - **Region**: Oregon (or closest to you)
4. Click **Create Database**
5. **Copy** the **Internal Database URL** (starts with `postgresql://`)

### Step 2: Create Web Service

1. Click **New** → **Web Service**
2. Connect your GitHub repo: `komal2605-2026/playground`
3. Configure:
   - **Name**: `user-management-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Language**: `Docker`
   - **Plan**: Free

4. Leave **Docker Command** empty (uses Dockerfile CMD)

### Step 3: Set Environment Variables

Click **Advanced** → **Add Environment Variable**

Add these:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Paste the Internal Database URL you copied |
| `SECRET_KEY` | Click **Generate** button |
| `DEBUG` | `False` |
| `WEB_CONCURRENCY` | `4` |

**Important**: Do NOT set `ALLOWED_HOSTS` - Render auto-injects `RENDER_EXTERNAL_HOSTNAME`

### Step 4: Deploy

1. Click **Create Web Service**
2. Wait for build (3-5 minutes)
3. Your app will be live at `https://your-app-name.onrender.com`

### Step 5: Run Initial Migrations

Go to **Shell** tab and run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Post-Deployment

### Access Your API

Your API is now publicly accessible:
- **Base URL**: `https://your-app-name.onrender.com`
- **Admin Panel**: `https://your-app-name.onrender.com/admin`
- **API Endpoints**: `https://your-app-name.onrender.com/api/...`

### View Logs

Render Dashboard → Your Service → **Logs** tab

### Update Deployment

Push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render auto-deploys on every push to `main` branch.

### Restart Service

Render Dashboard → Your Service → **Manual Deploy** → **Deploy latest commit**

---

## Troubleshooting

### "Application failed to respond"

**Cause**: App not binding to correct port or host.
**Solution**: Already fixed in entrypoint.sh (uses `PORT` env var)

### "Database connection failed"

**Cause**: Wrong DATABASE_URL or database not ready.
**Solutions**:
- Verify DATABASE_URL is set correctly
- Check database status on Render Dashboard
- Ensure database is in same region as web service

### "No migrations applied"

**Cause**: Migrations not run after deployment.
**Solution**: 
```bash
# In Render Shell
python manage.py migrate
```

### "Static files not loading"

**Cause**: STATIC_ROOT not configured or collectstatic not run.
**Solution**: Already handled in entrypoint.sh (runs `collectstatic --noinput`)

### "Too many database connections"

**Cause**: Free tier has connection limits.
**Solutions**:
- Reduce `WEB_CONCURRENCY` to 2
- Enable connection pooling (paid feature)

---

## Important Notes

### Free Tier Limitations

Render's free tier:
- ✅ Great for demos and learning
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds
- ⚠️ Limited to 750 hours/month
- ⚠️ Database has 90-day expiration

### Upgrade to Paid

For production:
- Web Service: $7/month (always on)
- PostgreSQL: $7/month (no expiration)

### Security Best Practices

Before going to production:
1. Generate new `SECRET_KEY`
2. Set `DEBUG=False`
3. Add custom domain to `ALLOWED_HOSTS`
4. Enable HTTPS (automatic on Render)
5. Set up monitoring and alerts

---

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Django secret key | Auto-generated |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | Auto-set by Render |
| `WEB_CONCURRENCY` | Gunicorn workers | `4` |
| `PORT` | Server port | `10000` (set by Render) |

---

## Testing Your Deployment

### Test API Endpoints

Replace `YOUR-APP-NAME` with your actual Render service name:

```bash
# Health check
curl https://YOUR-APP-NAME.onrender.com/

# Register user
curl -X POST https://YOUR-APP-NAME.onrender.com/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"secure123"}'

# Login
curl -X POST https://YOUR-APP-NAME.onrender.com/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"secure123"}'
```

### Use in Postman

1. Update your Postman collection base URL to:
   ```
   https://YOUR-APP-NAME.onrender.com
   ```

2. Test all endpoints

3. Share the public URL for demo purposes

---

## Next Steps

- [ ] Test all API endpoints on Render
- [ ] Update frontend to use Render URL
- [ ] Set up custom domain (optional)
- [ ] Configure CORS for frontend access
- [ ] Set up monitoring (Render has built-in metrics)
- [ ] Add SSL certificate (automatic on Render)

---

## Useful Commands

### View Logs
```bash
# In terminal (requires Render CLI)
render logs -f user-management-api
```

### Run Django Commands
```bash
# Via Render Dashboard Shell
python manage.py shell
python manage.py createsuperuser
python manage.py dbshell
```

### Scale Workers
Render Dashboard → Service → Instance Count

---

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Django Docs: https://docs.djangoproject.com

---

**🎉 Your API is now live and publicly accessible!**

Share your Render URL for demos and testing.
