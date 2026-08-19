# Automated Resume Upload Pipeline (Google Drive + Google Sheets)

This document details how candidates can upload their **PDF/DOCX resume file directly**, and how it automatically gets saved into your **Google Drive** with a clickable link inserted into your **Google Sheet**.

---

## 🔄 How the Resume Upload Pipeline Works

```
1. Candidate clicks "Apply for Referral" on your portal
                   ↓
2. Candidate selects their Resume file (PDF / DOCX) from their computer/phone
                   ↓
3. The Portal converts the file to Base64 and sends it to your Webhook
                   ↓
4. Google Apps Script receives the payload:
   ├── Creates/finds a folder in your Google Drive: "MoxiWorks Referral Resumes"
   ├── Saves the resume file into that Drive folder
   └── Inserts the candidate details + Clickable Drive Link into your Google Sheet!
                   ↓
5. You open Google Sheets: Click the link in column "Resume Link" to view their CV!
```

---

## 📋 What Your Google Sheet Will Look Like

| Timestamp | Role | Candidate Name | Email | Phone | Exp | LinkedIn | Resume (Clickable Link) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `19/08/2026 17:15` | `Director of Engineering` | `Amit Verma` | `amit@...` | `+91 98...` | `11 Yrs` | `linkedin.com/in/...` | [📄 View Resume (PDF)](https://drive.google.com/file/d/...) | `Strong squad lead...` |

---

## ⚡ 3-Minute Setup Guide

### Step 1: Create a Google Sheet
1. Open **[sheets.new](https://sheets.new)**.
2. Name it **`MoxiWorks Referral Applications`**.
3. In Row 1, add these headers:
   `A1`: **Timestamp** | `B1`: **Role** | `C1`: **Name** | `D1`: **Email** | `E1`: **Phone** | `F1`: **Experience** | `G1`: **LinkedIn** | `H1`: **Resume Link** | `I1`: **Notes**

---

### Step 2: Add the Google Apps Script Code
1. In your Google Sheet, click **Extensions** → **Apps Script**.
2. Replace all code with this complete file-uploader script:

```javascript
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    var resumeUrl = "";
    
    // If candidate uploaded a file (base64)
    if (data.fileData && data.fileName) {
      // Find or create "MoxiWorks Referral Resumes" folder in Google Drive
      var folderName = "MoxiWorks Referral Resumes";
      var folders = DriveApp.getFoldersByName(folderName);
      var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(folderName);
      
      // Decode Base64 and create file in Drive
      var decoded = Utilities.base64Decode(data.fileData.split(',')[1] || data.fileData);
      var blob = Utilities.newBlob(decoded, data.fileType || "application/pdf", data.name + " - Resume - " + data.fileName);
      var file = folder.createFile(blob);
      
      // Set permissions to anyone with link can view
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      resumeUrl = file.getUrl();
    } else if (data.resumeUrl) {
      resumeUrl = data.resumeUrl;
    }
    
    // Append row to Google Sheet
    sheet.appendRow([
      new Date(),
      data.role || '',
      data.name || '',
      data.email || '',
      data.phone || '',
      data.experience || '',
      data.linkedin || '',
      resumeUrl,
      data.notes || ''
    ]);
    
    return ContentService.createTextOutput(JSON.stringify({
      "status": "success",
      "resumeUrl": resumeUrl
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({
      "status": "error",
      "message": err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
```

3. Click the 💾 **Save** icon.

---

### Step 3: Deploy Webhook URL
1. Click **Deploy** → **New deployment** (top right).
2. Select type: **Web app**.
3. Set **Execute as**: `Me`.
4. Set **Who has access**: `Anyone`.
5. Click **Deploy** and copy the **Web App URL**.
6. Paste the URL into `REFERRAL_WEBHOOK_URL` in `index.html` (or share it here and I will connect it!).
