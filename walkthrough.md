# Telegram Notification Crons

## Summary of Changes
- **Morning Plan Endpoint:** Implemented `/api/cron/morning-plan` to run every day at 8:00 AM (7:00 UTC). This endpoint pulls all of the day's tasks for all users and sends a Telegram message formatted as a simple "Plan" list (just the task titles).
- **Evening Summary Endpoint:** Implemented `/api/cron/evening-summary` to run every day at 5:00 PM (16:00 UTC). This endpoint pulls all of the day's tasks, loops through them, and sends a Telegram message appending the inputted summary (or status) next to each task title.
- **Username Formatting:** Automatically converts the system username (e.g. `david.odigie`) into a formatted name (e.g. `David Odigie`) for the header of the Telegram message.
- **Vercel Config:** Updated `vercel.json` to trigger these two new endpoints at the required times.
- **Deployment:** The backend changes have been deployed to production.

## Verification
- Deployed successfully to Vercel.
- Cron schedules verified to trigger at the exact expected intervals.
- The new Python notification formatting exactly mimics the requested output styles.
