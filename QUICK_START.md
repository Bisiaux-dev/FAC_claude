# ⚡ Quick Start Guide - 5 Minutes to Deploy

Get your CRM Automation running on GitHub Actions in 5 minutes!

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] GitHub account
- [ ] Git installed on your computer
- [ ] CRM credentials (username, password, HTTP auth)
- [ ] Email account for notifications (Gmail recommended)

## 🚀 Step-by-Step Deployment

### Step 1: Create GitHub Repository (2 minutes)

1. **Go to GitHub**: https://github.com/new

2. **Create new repository**:
   - Name: `crm-automation` (or your preferred name)
   - Visibility: **Private** (recommended)
   - Don't initialize with README, .gitignore, or license
   - Click **"Create repository"**

3. **Note the repository URL** (you'll need it in Step 2)
   ```
   https://github.com/YOUR_USERNAME/crm-automation.git
   ```

### Step 2: Push Code to GitHub (1 minute)

Open terminal/command prompt:

```bash
# Navigate to project directory
cd C:\Users\Pierre\Desktop\rs_crm_automation_V0.1

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: CRM Automation v0.1"

# Add remote repository (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/crm-automation.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**✅ Checkpoint**: Verify files are on GitHub by refreshing your repository page.

### Step 3: Configure GitHub Secrets (2 minutes)

1. **Go to repository Settings**:
   ```
   Your Repository → Settings → Secrets and variables → Actions
   ```

2. **Click "New repository secret"** and add these ONE BY ONE:

#### CRM Credentials (5 secrets)
```
Name: CRM_BASE_URL
Value: crm.isimcrm.fr
---
Name: CRM_USERNAME
Value: your_crm_username@example.com
---
Name: CRM_PASSWORD
Value: your_crm_password
---
Name: CRM_HTTP_AUTH_USER
Value: crm_isim
---
Name: CRM_HTTP_AUTH_PASSWORD
Value: your_http_auth_password
```

#### Email Configuration (5 secrets)

For Gmail (recommended):

```
Name: SMTP_SERVER
Value: smtp.gmail.com
---
Name: SMTP_PORT
Value: 587
---
Name: SMTP_USERNAME
Value: your_email@gmail.com
---
Name: SMTP_PASSWORD
Value: xxxx xxxx xxxx xxxx (Gmail App Password - see below)
---
Name: EMAIL_RECIPIENTS
Value: recipient1@example.com,recipient2@example.com
```

**How to get Gmail App Password**:
1. Enable 2FA on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create password for "Mail"
4. Copy the 16-character password (with spaces)
5. Use this as `SMTP_PASSWORD`

**✅ Checkpoint**: You should have 10 secrets configured.

### Step 4: Test Your Setup (30 seconds)

1. **Go to Actions tab** in your repository

2. **Click "Daily CRM Report Generation"**

3. **Click "Run workflow"** (button on the right)

4. **Keep defaults** and click green **"Run workflow"** button

5. **Wait 5-10 minutes** for completion

**✅ Checkpoint**: Workflow completes with green checkmark ✅

### Step 5: Verify Results (30 seconds)

1. **Click on the completed workflow run**

2. **Scroll down to "Artifacts" section**

3. **Download**:
   - `crm-report-XXX` - PowerPoint report
   - `svg-data-XXX` - Raw data (optional)

4. **Check your email** for the report

**✅ Success!** Your CRM Automation is now running on GitHub Actions!

---

## 🎯 What Happens Next?

### Automatic Execution

Your workflow will now run automatically:
- **When**: Every weekday at 18:00 UTC
- **What**: Extracts data + Generates report + Sends email
- **Where**: View in Actions tab

### Manual Execution

You can trigger it anytime:
1. Go to **Actions** tab
2. Select **"Daily CRM Report Generation"**
3. Click **"Run workflow"**

---

## 🔧 Troubleshooting

### Workflow Fails

**Check workflow logs**:
1. Click on failed workflow run
2. Click on red ❌ step
3. Read error message

**Common issues**:

| Error | Solution |
|-------|----------|
| "Authentication failed" | Check CRM credentials in Secrets |
| "SMTP authentication error" | Use Gmail App Password, not regular password |
| "No SVG files found" | CRM website may be down, try again |
| "ChromeDriver error" | This is rare, re-run workflow |

### Email Not Received

1. **Check spam folder**
2. **Verify SMTP_USERNAME and SMTP_PASSWORD**
3. **For Gmail**: Must use App Password (16 characters)
4. **Check EMAIL_RECIPIENTS format**: comma-separated, no spaces

### Need Help?

- **Documentation**: Check [README.md](README.md)
- **Setup Guide**: Check [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- **Security**: Check [SECURITY.md](SECURITY.md)
- **Email**: bisiaux.pierre@outlook.fr

---

## 📊 Understanding the Workflow

### What It Does

```
1. Setup Python & Chrome
   ↓
2. Login to CRM
   ↓
3. Extract 11 SVG charts
   ↓
4. Parse data from SVGs
   ↓
5. Generate PowerPoint (12 slides)
   ↓
6. Send email with report
   ↓
7. Upload artifacts to GitHub
```

### Execution Time
- ⏱️ **5-10 minutes** total
- Extraction: 3-5 min
- Report generation: 30-60 sec
- Email sending: 10-30 sec

### Artifacts
- **Report**: Available for 30 days
- **SVG data**: Available for 7 days
- **Logs**: Available forever

---

## ⚙️ Customization (Optional)

### Change Schedule

Edit `.github/workflows/daily_report.yml`:

```yaml
schedule:
  # Current: 18:00 UTC, Monday-Friday
  - cron: '0 18 * * 1-5'

  # Options:
  # - cron: '0 17 * * 1-5'   # 17:00 UTC
  # - cron: '30 9 * * 1-5'   # 09:30 UTC
  # - cron: '0 8,18 * * 1-5' # Twice daily: 08:00 and 18:00
```

After editing, commit and push:
```bash
git add .github/workflows/daily_report.yml
git commit -m "Update schedule"
git push
```

### Change Email Recipients

1. Go to **Settings → Secrets**
2. Click on **EMAIL_RECIPIENTS**
3. Click **"Update"**
4. Change value: `new1@email.com,new2@email.com`
5. Click **"Update secret"**

### Disable Workflow

1. Go to **Actions** tab
2. Click **"Daily CRM Report Generation"**
3. Click **"⋯"** (three dots) → **"Disable workflow"**

---

## 📱 Monitoring

### View Execution History

**Actions Tab** → **Daily CRM Report Generation**

You'll see:
- ✅ Successful runs (green)
- ❌ Failed runs (red)
- 🟡 Running (yellow)

### Email Notifications on Failure

Already configured! You'll receive an email if the workflow fails.

---

## 🎉 You're Done!

Your CRM automation is now:
- ✅ Running automatically every weekday at 18:00 UTC
- ✅ Generating PowerPoint reports
- ✅ Sending reports via email
- ✅ Storing artifacts on GitHub
- ✅ Logging everything for debugging

**No more manual work needed!**

---

## 🚀 Next Steps (Optional)

Want to do more?

1. **Add more recipients**: Update EMAIL_RECIPIENTS secret
2. **Change schedule**: Edit workflow file
3. **Customize reports**: Modify `src/main.py` SLIDE_CONFIG
4. **Add more charts**: Update extraction logic
5. **Deploy with Docker**: Use `docker-compose.yml`

---

## 📞 Support

**Something not working?**

1. Check [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for detailed troubleshooting
2. Review workflow logs in Actions tab
3. Open an issue on GitHub
4. Email: bisiaux.pierre@outlook.fr

---

**Total Setup Time**: ⏱️ **5 minutes**

**Deployment Status**: ✅ **COMPLETE**

**Next Automatic Run**: Check Actions tab for countdown

---

*Made with ❤️ for automated CRM reporting*

Version: 0.1.0 | Date: 2025-01-13
