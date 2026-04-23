# GitHub in VS Code - Beginner's Guide

A step-by-step guide to commit, push, pull, and sync files using VS Code instead of the command line.

---

## Step 1: Sign In to VS Code with GitHub Account

1. Open **VS Code**
2. Click on the **Account icon** in the bottom left corner (or top right)
3. Select **"Sign in with GitHub"**
4. Your browser will open - sign in with your GitHub credentials
5. Click **"Authorize"** to allow VS Code to access your GitHub account
6. You should see a success message - go back to VS Code
7. You'll see your GitHub username in the bottom left corner

✅ You're now connected to GitHub!

---

## Step 2: Install Essential Extensions

VS Code has built-in Git support, but these extensions make it even easier:

### Method A: Install via Extensions Marketplace
1. Click the **Extensions icon** on the left sidebar (or press `Ctrl+Shift+X`)
2. Search for each extension below and click **Install**

### Recommended Extensions:

| Extension | Purpose |
|-----------|---------|
| **GitHub Pull Requests and Issues** | Manage PRs and issues directly in VS Code |
| **GitLens** | See who changed what and when |
| **Git Graph** | Visualize your Git history |
| **GitHub Copilot** | (Optional) AI coding assistant |

**To install:**
- Search "GitHub Pull Requests and Issues" → Install
- Search "GitLens" → Install
- Search "Git Graph" → Install

✅ All extensions are ready!

---

## Step 3: Choose & Initialize a Repository

Your friend has **3 options**:

### Option A: Clone an Existing Repository from GitHub
**Use this if:** You want to work on a project that already exists on GitHub

**Steps:**
1. Go to GitHub.com and find the repository you want
2. Click the green **"Code"** button
3. Copy the HTTPS URL (e.g., `https://github.com/username/project-name.git`)
4. In VS Code, press `Ctrl+Shift+P`
5. Type: **"Git: Clone"**
6. Paste the repository URL
7. Choose a folder on your computer where you want to save it (e.g., `C:\Users\YourName\Documents\MyProjects`)
8. Click **"Open"** or **"Open in New Window"**
9. Wait for it to download - you're ready to work!

✅ **Now you have all the files from GitHub locally!**

---

### Option B: Create a New Repository Locally, Then Push to GitHub
**Use this if:** You have a new project you want to start fresh

**Steps:**

1. **Create a folder on your computer:**
   - Example: `C:\Users\YourName\Documents\MyNewProject`

2. **Open it in VS Code:**
   - File → Open Folder → Select your new folder

3. **Initialize Git locally:**
   - Press `Ctrl+Shift+P`
   - Type: **"Git: Initialize Repository"**
   - Click on the folder when prompted

4. **Create a file (so there's something to commit):**
   - Create a file like `README.md` with a description

5. **Commit your first changes:**
   - Click Source Control icon (left sidebar)
   - Stage all files (click `+`)
   - Write a message: "Initial commit"
   - Press `Ctrl+Enter` to commit

6. **Create a repository on GitHub.com:**
   - Go to GitHub.com
   - Click **"New"** (top left)
   - Name your repository (e.g., "MyNewProject")
   - Click **"Create Repository"**
   - GitHub will show you setup instructions

7. **Link your local folder to GitHub:**
   - In VS Code, press `Ctrl+Shift+P`
   - Type: **"Git: Add Remote"**
   - Paste the repository URL from GitHub
   - Name it "origin" (default)

8. **Push to GitHub:**
   - Click the three dots (...) in Source Control
   - Select **"Push"**

✅ **Your project is now on GitHub!**

---

### Option C: Open an Existing Local Repository
**Use this if:** You already have a folder with Git initialized

**Steps:**
1. File → Open Folder
2. Select your folder (it should have a `.git` folder inside)
3. You'll see the Source Control panel automatically
4. Ready to work!

---

## How to Choose the Right Option:

| Scenario | Use Option |
|----------|-----------|
| Joining an existing project on GitHub | **Option A** (Clone) |
| Starting a brand new project | **Option B** (Create New) |
| You already have a local folder with `.git` | **Option C** (Open Existing) |
| Working on a friend's project | **Option A** (Clone their repo) |

---

## Step 4: Make Changes and Commit

### View Changes:
1. Click the **Source Control icon** on the left sidebar (looks like a branch)
2. You'll see all modified files listed under "Changes"

### Stage Changes:
- **Stage all changes:** Click the `+` icon next to "Changes"
- **Stage specific files:** Click the `+` icon next to each file

### Commit Changes:
1. Type a **commit message** in the text box at the top (e.g., "Fix bug in login")
2. Press `Ctrl+Enter` or click the **Commit button** (checkmark icon)

**Good commit messages:**
- ✅ "Add user authentication"
- ✅ "Fix navigation bug"
- ❌ "update"
- ❌ "asdf"

---

## Step 5: Push Your Changes to GitHub

### Push to GitHub:
1. In the **Source Control panel**, click the **three dots** (...)
2. Select **"Push"**

Or use the keyboard shortcut:
- Press `Ctrl+Shift+P` → Type "Git: Push" → Enter

**You should see a message: "Pushing... 1/1"**

✅ Your changes are now on GitHub!

---

## Step 6: Pull Latest Changes from GitHub

### Pull Updates:
1. Click the **three dots** (...) in Source Control
2. Select **"Pull"**

Or:
- Press `Ctrl+Shift+P` → Type "Git: Pull" → Enter

**This fetches the latest changes from your team members.**

---

## Step 7: Sync (Push & Pull Together)

### Sync Your Repository:
1. Click the **three dots** (...) in Source Control
2. Select **"Sync"** (combines Pull + Push)

Or use the keyboard shortcut in the bottom status bar:
- You might see a sync icon with arrows - click it

**This ensures you have the latest code AND your changes are uploaded.**

---

## Undo/Discard Changes

### Before Committing:
1. Right-click a file in Source Control
2. Select **"Discard Changes"** (reverses unsaved edits)

### After Committing (Undo Last Commit):
1. Press `Ctrl+Shift+P`
2. Type "Git: Undo Last Commit"
3. Choose to keep or discard your changes

⚠️ **Only do this if changes aren't pushed to GitHub yet!**

---

## Troubleshooting

### Problem: "Failed to push"
**Solution:** Pull first (`Ctrl+Shift+P` → Git: Pull) to get latest changes, then push

### Problem: "Permission denied"
**Solution:** 
- Make sure you're signed in with GitHub (check bottom left corner)
- Your repository must be accessible to your account

### Problem: Can't see the Source Control panel
**Solution:** Click the branch icon on the left sidebar (or press `Ctrl+Shift+G`)

### Problem: VS Code doesn't recognize Git
**Solution:** 
- Install Git from https://git-scm.com/
- Restart VS Code

---

## Quick Reference Cheat Sheet

| Task | Steps |
|------|-------|
| **Commit** | Source Control → Stage files → Write message → Ctrl+Enter |
| **Push** | Source Control (three dots) → Push |
| **Pull** | Source Control (three dots) → Pull |
| **Sync** | Source Control (three dots) → Sync |
| **View History** | Click Git Graph extension |
| **See Blame** | Right-click code → View Git Blame (with GitLens) |

---

## Tips & Best Practices

✅ **DO:**
- Commit frequently (small, focused commits)
- Write clear commit messages
- Pull before starting new work
- Sync daily to avoid conflicts
- Use branches for new features

❌ **DON'T:**
- Commit directly to `main` (use branches)
- Commit sensitive info (passwords, API keys)
- Push without reviewing your changes
- Force push without knowing what you're doing

---

## Need More Help?

- **GitHub Docs:** https://docs.github.com/
- **VS Code Git Docs:** https://code.visualstudio.com/docs/sourcecontrol/overview
- **GitLens Docs:** https://www.gitkraken.com/gitlens

Good luck! 🚀
