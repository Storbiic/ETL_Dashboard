# 🚀 Quick Vercel Deployment Guide

## Immediate Steps (5 Minutes)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```
Follow the prompts to authenticate with your GitHub/GitLab/Bitbucket account.

### Step 3: Deploy from Your Project Directory
```bash
cd C:\Users\Saad\Desktop\Final_Project\ETL_Dashboard
vercel
```

**Answer the prompts:**
- Set up and deploy? **Y**
- Which scope? (select your account)
- Link to existing project? **N** 
- What's your project's name? **etl-dashboard**
- In which directory is your code located? **.** (current directory)

### Step 4: Your App is Live! 🎉
After deployment (2-3 minutes), you'll get:
- **Production URL**: `https://etl-dashboard-[hash].vercel.app`
- **Preview URL**: For testing

## Test Your Deployment

### Health Check
```bash
curl https://your-app-url.vercel.app/api/health
```
Should return:
```json
{
  "status": "healthy",
  "service": "etl-dashboard",
  "platform": "vercel"
}
```

### Main Page
Visit: `https://your-app-url.vercel.app`

## Features Available

✅ **File Upload**: `/api/upload` - Upload Excel files  
✅ **File Preview**: `/api/preview` - Preview Excel data  
✅ **Data Profiling**: `/api/profile` - Analyze data quality  
✅ **Transformation**: `/api/transform` - Process ETL workflows  
✅ **File Download**: `/api/files` - Download processed files  
✅ **Health Monitoring**: `/api/health` - System status  

## Automatic Features

🔄 **Auto-deployments** from Git pushes  
🌐 **Global CDN** for fast loading worldwide  
🔒 **HTTPS** automatically enabled  
📊 **Monitoring** built into Vercel dashboard  
⚡ **Serverless scaling** handles traffic spikes  

## Environment Variables (Optional)

Set in Vercel dashboard → Settings → Environment Variables:

```bash
PYTHONPATH=/var/task:/var/task/backend
UPLOAD_FOLDER=/tmp/uploads
PROCESSED_FOLDER=/tmp/processed
FLASK_SECRET_KEY=your-secure-secret
MAX_FILE_SIZE_MB=16
```

## What's Different on Vercel?

### ✅ Advantages
- **Zero server management** - fully serverless
- **Automatic scaling** - handles any traffic load
- **Global performance** - CDN in 100+ locations  
- **Free tier** - generous limits for development
- **Git integration** - deploy on every push
- **Preview deployments** - test branches safely

### ⚠️ Considerations
- **Function timeout**: 10s (free), 15s (pro), 900s (enterprise)
- **File storage**: Temporary (`/tmp`) - files deleted after execution
- **Memory limit**: 1GB (free), 3GB (pro)
- **Cold starts**: ~100ms-1s for first request

## Cost Structure

### Hobby (Free Forever)
- ✅ 100 GB bandwidth/month
- ✅ 100 function invocations/day
- ✅ Custom domains
- ✅ SSL certificates

### Pro ($20/month)
- ✅ 1 TB bandwidth
- ✅ Unlimited function invocations  
- ✅ Longer function timeouts (15s)
- ✅ Advanced monitoring

## Next Steps

### 1. Custom Domain (Optional)
```bash
vercel domains add yourdomain.com
```

### 2. Set up Automatic Deployments
- Connect your GitHub repository
- Every push to main → auto-deploy to production
- Every push to other branches → preview deployment

### 3. Monitor Performance
- Check Vercel dashboard for metrics
- Monitor function execution times
- Review error logs

### 4. Add Persistent Storage (If Needed)
For permanent file storage, consider:
- **Vercel Blob**: File storage service
- **AWS S3**: Object storage
- **Supabase**: Database + file storage

## Troubleshooting

### Build Issues
```bash
# Check build logs
vercel inspect [deployment-url]

# Test locally
vercel dev
```

### Function Errors
```bash
# View function logs
vercel logs [deployment-url]

# Test specific endpoint
curl -X POST https://your-app.vercel.app/api/health
```

### Import Errors
If you see import errors, ensure:
- `requirements-vercel.txt` has all dependencies
- Python path is set correctly in vercel.json
- Backend modules are properly structured

## Development Workflow

### Local Development
```bash
vercel dev
```
Your app runs at `http://localhost:3000`

### Deploy Changes
```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

Your ETL Dashboard is now running on Vercel's global infrastructure! 🌍

**Production URL**: Check your terminal output or Vercel dashboard  
**Dashboard**: https://vercel.com/dashboard