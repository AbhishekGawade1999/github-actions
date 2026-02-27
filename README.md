# Telegram Job Alerts

This repository contains a GitHub Actions workflow (`.github/workflows/scrape_and_notify.yml`) that automates scraping job boards and sending alerts via Telegram.

## Workflow Overview: `scrape_and_notify.yml`

The **Telegram Job Alerts** workflow runs a Python-based job scraper and notifies users of new postings through a Telegram bot.

### Triggers
- **Scheduled runs**: Executes every hour (`0 */1 * * *`).
- **Manual runs**: Can be triggered manually via the `workflow_dispatch` event in the GitHub Actions UI.

### Environment & Dependencies
- **Environment**: Runs on `ubuntu-latest`.
- **Python Version**: Uses Python 3.10.
- **Python Packages**: Installs `python-jobspy` (for scraping jobs), `pandas` (for data processing), and `requests` (for sending Telegram messages).

### Required GitHub Secrets
To run the scraper and send notifications, the following secrets must be configured in your repository settings (`Settings > Secrets and variables > Actions`):
- `TELEGRAM_TOKEN`: The API token for your Telegram bot (obtained from BotFather).
- `TELEGRAM_CHAT_ID`: The ID of the Telegram chat or channel where the bot will send the alerts.

### State Management
To prevent duplicate notifications for jobs that have already been sent, the workflow tracks the state using a file named `notified_jobs.txt`.
At the end of a successful run, the workflow:
1. Commits any changes made to `notified_jobs.txt`.
2. Pushes the updated file back to the repository using the `github-actions[bot]` credentials.
*(Note: For this step to work, the workflow is granted `contents: write` permissions.)*