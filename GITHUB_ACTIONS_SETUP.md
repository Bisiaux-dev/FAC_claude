# GitHub Actions Setup Guide

Complete guide to deploying CRM Automation with GitHub Actions.

## 📋 Prerequisites

- GitHub account
- CRM credentials
- Email account (Gmail recommended for SMTP)
- Git installed locally

## 🚀 Quick Start (5 minutes)

### Step 1: Create GitHub Repository

```bash
# Navigate to project directory
cd C:\Users\Pierre\Desktop\rs_crm_automation_V0.1

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CRM Automation v0.1 - GitHub Actions edition"

# Create repository on GitHub (via web interface)
# Then link it:
git remote add origin https://github.com/YOUR_USERNAME/rs_crm_automation.git
git branch -M main
git push -u origin main
```

### Step 2: Configure GitHub Secrets

Go to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets one by one:

#### CRM Secrets (Required)
```
Name: CRM_BASE_URL
Value: crm.isimcrm.fr

Name: CRM_USERNAME
Value: your_crm_username@example.com

Name: CRM_PASSWORD
Value: your_crm_password

Name: CRM_HTTP_AUTH_USER
Value: crm_isim

Name: CRM_HTTP_AUTH_PASSWORD
Value: your_http_auth_password
```

#### Email Secrets (Required for notifications)
```
Name: SMTP_SERVER
Value: smtp.gmail.com

Name: SMTP_PORT
Value: 587

Name: SMTP_USERNAME
Value: your_email@gmail.com

Name: SMTP_PASSWORD
Value: your_gmail_app_password

Name: EMAIL_RECIPIENTS
Value: recipient1@example.com,recipient2@example.com
```

### Step 3: Enable GitHub Actions

1. Go to **Repository → Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see two workflows:
   - `Daily CRM Report Generation`
   - `Test CRM Automation`

### Step 4: Test Manually

1. Go to **Actions** tab
2. Click on **"Daily CRM Report Generation"**
3. Click **"Run workflow"** button (top right)
4. Select options:
   - Branch: `main`
   - Extract only: `false` (to generate full report)
5. Click **"Run workflow"**

Wait 5-10 minutes for completion.

### Step 5: Check Results

After workflow completes:

1. **View logs**: Click on the workflow run to see detailed logs
2. **Download artifacts**: Scroll down to "Artifacts" section
   - `crm-report-XXX.pptx` - PowerPoint report
   - `svg-data-XXX.zip` - Raw SVG data
3. **Check email**: Verify report was sent to configured recipients

## 📅 Scheduled Execution

The workflow automatically runs:
- **Time**: 18:00 UTC (19:00 Paris winter, 20:00 summer)
- **Days**: Monday to Friday
- **Timezone**: UTC (adjust in `.github/workflows/daily_report.yml`)

### Adjusting Schedule

Edit `.github/workflows/daily_report.yml`:

```yaml
schedule:
  # Format: minute hour day month weekday
  # Examples:
  - cron: '0 18 * * 1-5'  # 18:00 UTC, Mon-Fri (current)
  - cron: '0 17 * * 1-5'  # 17:00 UTC, Mon-Fri
  - cron: '30 16 * * *'   # 16:30 UTC, every day
  - cron: '0 8,18 * * 1-5'  # 08:00 and 18:00 UTC, Mon-Fri
```

## 🔒 Security Best Practices

### Gmail App Password

For Gmail SMTP:

1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create app password for "Mail"
4. Use this password (not your regular password) as `SMTP_PASSWORD`

### Credential Rotation

Rotate credentials every 90 days:
1. Update passwords in CRM system
2. Update GitHub Secrets
3. Test workflow manually

### Repository Visibility

- **Private repository**: Recommended for production
- **Public repository**: Secrets are still safe, but logs are visible

## 🐛 Troubleshooting

### Workflow Fails with "Authentication Failed"

**Check**:
- CRM credentials in GitHub Secrets
- CRM website is accessible
- HTTP Auth credentials are correct

**Fix**:
1. Go to Settings → Secrets
2. Update `CRM_USERNAME` and `CRM_PASSWORD`
3. Re-run workflow

### Email Not Sent

**Check**:
- SMTP credentials in GitHub Secrets
- Gmail App Password (not regular password)
- Email recipients format: `email1@domain.com,email2@domain.com`

**Fix**:
1. Test SMTP credentials locally:
   ```python
   python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login('your@gmail.com','password'); print('OK')"
   ```
2. Update GitHub Secrets if needed

### Chrome/ChromeDriver Issues

**Error**: Chrome version mismatch

**Fix**: This is handled automatically by GitHub Actions. If issues persist:
- Check workflow logs for Chrome version
- Verify ChromeDriver installation step succeeded

### Workflow Doesn't Run on Schedule

**Check**:
- Repository is active (has recent commits)
- GitHub Actions are enabled
- Workflow file syntax is correct

**Fix**:
1. Make a small commit (e.g., update README)
2. Push to trigger Actions
3. Check Actions tab for status

### SVG Parsing Errors

**Error**: No data extracted from SVG

**Fix**:
1. Download SVG artifacts from failed run
2. Check SVG structure manually
3. Update parser in `src/parsers/svg_parser.py` if CRM changed format

## 📊 Monitoring

### View Execution History

1. Go to **Actions** tab
2. Select **"Daily CRM Report Generation"**
3. View all runs with status (success/failure)

### Download Historical Reports

1. Click on specific workflow run
2. Scroll to **Artifacts** section
3. Download reports (available for 30 days)

### Email Notifications

Configure email alerts for failures:

1. Edit `.github/workflows/daily_report.yml`
2. Update email notification step
3. Add `if: failure()` condition

## 🔄 Updates and Maintenance

### Updating Code

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push origin main

# Workflow will run automatically on next schedule
# Or trigger manually from Actions tab
```

### Updating Dependencies

Edit `requirements.txt`:
```
selenium==4.36.0  # Update version
python-pptx==1.0.3
```

Commit and push. Next run will use new versions.

### Updating Workflow

Edit `.github/workflows/daily_report.yml` for:
- Schedule changes
- Email settings
- Artifact retention periods
- Timeout adjustments

## 🎯 Advanced Configuration

### Running Multiple Times Per Day

```yaml
schedule:
  - cron: '0 9 * * 1-5'   # 09:00 UTC
  - cron: '0 18 * * 1-5'  # 18:00 UTC
```

### Adding Webhook Notifications (Slack/Teams)

Add step to workflow:
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {"text": "CRM Report completed: ${{ job.status }}"}
```

### Parallel Execution (Multiple CRMs)

Create separate workflows for each CRM or use matrix strategy:
```yaml
strategy:
  matrix:
    crm: [crm1, crm2, crm3]
```

## 📞 Support

If you encounter issues:

1. **Check workflow logs**: Detailed error messages
2. **Review GitHub Actions documentation**: https://docs.github.com/actions
3. **Open issue**: https://github.com/yourusername/rs_crm_automation/issues
4. **Email**: bisiaux.pierre@outlook.fr

## ✅ Verification Checklist

After setup, verify:

- [ ] Repository created and code pushed
- [ ] All GitHub Secrets configured
- [ ] GitHub Actions enabled
- [ ] Manual workflow run succeeds
- [ ] Report artifact downloadable
- [ ] Email notification received
- [ ] Schedule is correct for your timezone
- [ ] Secrets are secure (not visible in logs)

## 🎉 Success!

Your CRM Automation is now running on GitHub Actions!

**Next scheduled execution**: Check Actions tab for countdown timer

**Manual trigger anytime**: Actions → Daily CRM Report Generation → Run workflow

---

Generated: 2025-01-13
Version: 0.1.0
