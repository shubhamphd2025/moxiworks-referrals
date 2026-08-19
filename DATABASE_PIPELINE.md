# Candidate Database & Referral Pipeline Setup Guide

This guide explains how to connect your personal referral portal directly to a **Google Sheets Database** (100% free, automated, and real-time).

---

## 📊 Live Database Pipeline Architecture

```
[Candidate on LinkedIn]
       ↓
[Shubham's Referral Portal] 
       ↓ (Clicks "Apply for Referral")
[Interactive Intake Form Modal]
       ↓ (Submits Name, Email, Phone, Exp, LinkedIn URL, Resume Link)
[Google Apps Script Webhook]
       ↓
[Shubham's Private Google Sheet Database] + [Instant Email Notification to Shubham]
```

---

## ⚡ 2-Minute Google Sheets Setup Instructions

### Step 1: Create a Google Sheet
1. Open [sheets.new](https://sheets.new) in your browser.
2. Name your spreadsheet: **`MoxiWorks Referral Applications`**.
3. In **Row 1**, set up the following column headers:
   - `A1`: **Timestamp**
   - `B1`: **Role**
   - `C1`: **Candidate Name**
   - `D1`: **Email**
   - `E1`: **Phone**
   - `F1`: **Experience**
   - `G1`: **LinkedIn Profile**
   - `H1`: **Resume Link**
   - `I1`: **Notes**

---

### Step 2: Add the Google Apps Script Webhook
1. In your Google Sheet, click **Extensions** → **Apps Script** (top menu).
2. Delete any default code and paste the following script:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Append candidate application row
    sheet.appendRow([
      new Date(),
      data.role || '',
      data.name || '',
      data.email || '',
      data.phone || '',
      data.experience || '',
      data.linkedin || '',
      data.resumeUrl || '',
      data.notes || ''
    ]);
    
    // Optional: Send instant email notification to your inbox
    // GmailApp.sendEmail("your-email@example.com", "New MoxiWorks Referral: " + data.name, "Role: " + data.role + "\nLinkedIn: " + data.linkedin + "\nResume: " + data.resumeUrl);

    return ContentService.createTextOutput(JSON.stringify({"status": "success"}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

3. Click the 💾 **Save** icon.

---

### Step 3: Deploy as Web App
1. In the top right of Apps Script, click **Deploy** → **New deployment**.
2. Click the ⚙️ gear icon next to "Select type" and choose **Web app**.
3. Configure the deployment settings:
   - **Description**: `Referral Intake Webhook`
   - **Execute as**: `Me`
   - **Who has access**: `Anyone` *(Crucial so candidates can submit without logging in)*
4. Click **Deploy**.
5. Copy the **Web App URL** (looks like `https://script.google.com/macros/s/.../exec`).

---

### Step 4: Plug URL into your Portal
Paste your Web App URL into `REFERRAL_WEBHOOK_URL` inside `index.html` (or share it here and I will connect and push it to GitHub Pages for you!).
