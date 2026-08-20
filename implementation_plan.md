# Notification Toggle & Formatting Plan

To address your feedback, here is my plan:

## 1. Why is the status "Pending"?
In the current system logic, if the "Summary" box is left empty, the notification falls back to showing the task's Status (e.g. `Pending`, `In Progress`, `Completed`). Because the summary was blank when the notification fired, it showed the default `Pending` status. Going forward, you can either update the status dropdown or type in the summary to change what appears!

## 2. Notification Toggle on Task Cards
I will add a new toggle switch directly on each task card on your dashboard.
- **Backend Changes**: I will add a `notify_enabled` boolean flag to the database (`DailyLogModel`) that defaults to `True`.
- **UI Changes**: I will add a switch/checkbox to the task cards. When you untoggle it, that specific task will be completely excluded from both the Morning Plan and Evening Summary Telegram notifications.
- **Cron Changes**: I will update the backend Python notification scripts to filter out any tasks where `notify_enabled` is set to false.

## 3. Proper Text Indentation
I will update the Telegram message formatting to include clear bullet points and spacing, so it looks like this:

**Morning Plan Example:**
```text
Daily Plan for 14/08/2026 - David Odigie

• Daily review of process maker report
• Password at rest detection
• Review of external threat advisory
```

**Evening Summary Example:**
```text
Daily Plan for 14/08/2026 - David Odigie

• Daily review of process maker report
  └ done

• Password at rest detection
  └ fine tuning still ongoing
```

> [!IMPORTANT]
> **Open Question for You:**
> The toggle we add to the dashboard will apply to the task for *that specific day*. Is that correct, or do you want the toggle to permanently disable that task from notifications on all future days as well?

Please review this plan. If the new indented layout and the toggle logic sound good to you, simply approve it and I will execute the changes!
