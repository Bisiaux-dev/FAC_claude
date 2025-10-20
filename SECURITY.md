# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by emailing:

**Email**: bisiaux.pierre@outlook.fr

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work with you to resolve the issue.

## Security Best Practices

### For GitHub Actions Users

1. **Never commit credentials** to the repository
2. **Use GitHub Secrets** for all sensitive data:
   - CRM credentials
   - Email passwords
   - API keys
3. **Limit secret access** to specific workflows only
4. **Review workflow permissions** regularly
5. **Enable branch protection** on main/production branches

### For Local/Docker Users

1. **Use `.env` files** for credentials (never commit them)
2. **Set proper file permissions** on config files (chmod 600)
3. **Use environment variables** instead of hardcoded values
4. **Rotate credentials regularly**
5. **Use app-specific passwords** for email (Gmail, Outlook)

### CRM Access

1. **Use dedicated service accounts** for automation
2. **Limit account permissions** to read-only where possible
3. **Enable 2FA** on CRM accounts when available
4. **Monitor access logs** for unusual activity

### Docker Security

1. **Don't run containers as root**
2. **Scan images** for vulnerabilities regularly
3. **Use official base images** (python:3.11-slim)
4. **Keep dependencies updated**
5. **Limit container network access**

## Known Security Considerations

### ⚠️ Chrome/Selenium

- Running Selenium in headless mode reduces exposure
- Chrome is configured with `--no-sandbox` for Docker compatibility
- This is acceptable in controlled environments (GitHub Actions, private Docker)
- **Not recommended** for public-facing servers

### ⚠️ SSL Certificate Validation

- The extractor uses `--ignore-certificate-errors` for compatibility
- This is necessary for some CRM systems with self-signed certificates
- Only use with trusted CRM endpoints

### ⚠️ Data Storage

- Extracted SVG files may contain sensitive data
- Reports are stored as GitHub Artifacts (private repositories only)
- Set appropriate retention periods (default: 30 days for reports)
- Clean up local files after processing

## Security Updates

We regularly update dependencies to address security vulnerabilities:

```bash
# Check for outdated packages
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt

# Security audit
pip-audit
```

## Compliance

### GDPR Considerations

If processing personal data:
- Ensure CRM access is authorized
- Implement data retention policies
- Document data processing activities
- Provide data subject rights (access, deletion)

### Data Protection

- All credentials are encrypted in GitHub Secrets
- Email transmission uses TLS/STARTTLS
- CRM access uses HTTPS
- Reports contain only aggregate statistics (no PII by default)

## Incident Response

If a security incident occurs:

1. **Immediately**:
   - Disable affected workflows
   - Rotate compromised credentials
   - Review access logs

2. **Within 24 hours**:
   - Assess impact
   - Notify affected parties
   - Document incident

3. **Within 72 hours**:
   - Implement fixes
   - Update security measures
   - Publish post-mortem (if appropriate)

## Contact

For security concerns, contact:
- **Email**: bisiaux.pierre@outlook.fr
- **GitHub**: Create a private security advisory

---

Last updated: 2025-01-13
