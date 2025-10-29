# Deployment Guide: Vercel + Railway

This guide will help you deploy the Trippy travel planner application with the frontend on Vercel and the backend on Railway.

## Prerequisites

- GitHub account
- Vercel account (sign up at https://vercel.com)
- Railway account (sign up at https://railway.app)
- All required API keys (OpenAI, Tavily, Google Maps, Arize)

---

## Part 1: Deploy Backend to Railway

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your `trippy3.0` repository

### Step 3: Configure Railway Environment Variables

In the Railway dashboard, go to your project → **Variables** tab and add:

```
OPENAI_API_KEY=your-openai-api-key
ARIZE_SPACE_ID=your-space-id
ARIZE_API_KEY=your-arize-api-key
ARIZE_PROJECT_NAME=trippy-decentralized
TAVILY_API_KEY=your-tavily-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
ENVIRONMENT=production
LOG_LEVEL=INFO
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.5
FRONTEND_URL=https://your-app.vercel.app
```

**Important:** You'll update `FRONTEND_URL` after deploying to Vercel in Part 2.

### Step 4: Configure Railway Build Settings

Railway should auto-detect your Python app. If needed, verify:

- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 5: Deploy

1. Railway will automatically deploy your backend
2. Wait for deployment to complete (~2-5 minutes)
3. Copy your Railway URL (e.g., `https://your-app.railway.app`)

### Step 6: Test Backend

Visit your Railway URL to verify:
- `/` - Should show API info
- `/health` - Should return `{"status": "healthy"}`
- `/docs` - Should show FastAPI documentation

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Configuration

Before deploying, update `frontend/env-config.js` with your Railway backend URL:

```javascript
window.ENV = {
    API_URL: 'https://your-app.railway.app'  // Replace with your Railway URL
};
```

Commit this change:

```bash
git add frontend/env-config.js
git commit -m "Update API URL for production"
git push
```

### Step 2: Create Vercel Project

1. Go to https://vercel.com
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset:** Other
   - **Root Directory:** `frontend`
   - **Build Command:** (leave empty)
   - **Output Directory:** (leave empty)
   - **Install Command:** (leave empty)

### Step 3: Deploy to Vercel

1. Click **"Deploy"**
2. Wait for deployment (~1-2 minutes)
3. Copy your Vercel URL (e.g., `https://trippy.vercel.app`)

### Step 4: Update Railway CORS Settings

1. Go back to Railway dashboard
2. Update the `FRONTEND_URL` environment variable with your Vercel URL:
   ```
   FRONTEND_URL=https://trippy.vercel.app
   ```
3. Railway will automatically redeploy with the new CORS settings

---

## Part 3: Testing

### Test the Complete Flow

1. Visit your Vercel URL (e.g., `https://trippy.vercel.app`)
2. Fill out the trip planning form
3. Submit and verify:
   - Loading indicator appears
   - Results are displayed
   - No CORS errors in browser console

### Troubleshooting

#### CORS Errors
- Verify `FRONTEND_URL` in Railway matches your Vercel URL exactly
- Check Railway logs: `railway logs`
- Ensure Railway redeployed after updating environment variables

#### Backend Not Responding
- Check Railway deployment logs
- Verify all environment variables are set correctly
- Test backend endpoints directly at your Railway URL

#### Frontend Not Loading
- Check Vercel deployment logs
- Verify `env-config.js` has the correct Railway URL
- Check browser console for errors

---

## Environment Variables Reference

### Railway (Backend)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ Yes |
| `ARIZE_SPACE_ID` | Arize Phoenix space ID | ✅ Yes |
| `ARIZE_API_KEY` | Arize Phoenix API key | ✅ Yes |
| `ARIZE_PROJECT_NAME` | Project name in Arize | ✅ Yes |
| `TAVILY_API_KEY` | Tavily search API key | ✅ Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | ✅ Yes |
| `ENVIRONMENT` | Set to `production` | ✅ Yes |
| `LOG_LEVEL` | Logging level (`INFO` recommended) | ✅ Yes |
| `OPENAI_MODEL` | OpenAI model to use | No (defaults to `gpt-4o-mini`) |
| `OPENAI_TEMPERATURE` | Model temperature | No (defaults to `0.5`) |
| `FRONTEND_URL` | Your Vercel URL for CORS | ✅ Yes |

### Vercel (Frontend)

No environment variables needed if you hardcode the Railway URL in `env-config.js`.

Alternatively, you can use Vercel environment variables:

1. In Vercel project → **Settings** → **Environment Variables**
2. Add `VITE_API_URL` = your Railway URL
3. Update `env-config.js` to use Vercel env vars (requires build step)

---

## Monitoring & Logs

### Railway Logs

View real-time logs:
```bash
railway logs
```

Or in the Railway dashboard → **Deployments** → Click deployment → **View Logs**

### Vercel Logs

View logs in Vercel dashboard → **Deployments** → Click deployment → **Function Logs**

### Arize Phoenix Monitoring

1. Go to https://app.arize.com
2. Select your project: `trippy-decentralized`
3. View traces and performance metrics

---

## Updating Your Application

### Backend Updates

1. Make changes to backend code
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update backend"
   git push
   ```
3. Railway auto-deploys on push to main branch

### Frontend Updates

1. Make changes to frontend code
2. If API URL changes, update `frontend/env-config.js`
3. Commit and push:
   ```bash
   git add .
   git commit -m "Update frontend"
   git push
   ```
4. Vercel auto-deploys on push to main branch

---

## Cost Estimates

### Railway
- **Free Tier:** $5/month in credits (sufficient for development/testing)
- **Pro Plan:** $20/month (recommended for production)

### Vercel
- **Hobby Plan:** Free (perfect for this static frontend)
- **Pro Plan:** $20/month (only needed for teams)

### APIs
- **OpenAI:** Pay per use (~$0.15 per request with gpt-4o-mini)
- **Google Maps:** $200/month free credits
- **Tavily:** Check pricing at tavily.com
- **Arize Phoenix:** Free tier available

---

## Production Checklist

- [ ] All API keys configured in Railway
- [ ] `ENVIRONMENT=production` set in Railway
- [ ] `FRONTEND_URL` points to Vercel URL
- [ ] Frontend `env-config.js` points to Railway URL
- [ ] Test complete flow (form submission → results)
- [ ] Check CORS - no errors in browser console
- [ ] Monitor Railway logs for errors
- [ ] Verify Arize Phoenix traces are being recorded
- [ ] Test on mobile devices
- [ ] Set up custom domain (optional)

---

## Custom Domains (Optional)

### Vercel Domain

1. Go to Vercel project → **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. Update `FRONTEND_URL` in Railway

### Railway Domain

1. Go to Railway project → **Settings** → **Domains**
2. Add custom domain
3. Update DNS records
4. Update `env-config.js` in frontend

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Issues: Open an issue in your GitHub repo

---

**🎉 Congratulations!** Your Trippy app is now deployed and accessible worldwide!
