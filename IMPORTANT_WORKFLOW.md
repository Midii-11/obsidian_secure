# ⚠️ IMPORTANT: Correct Lock/Unlock Workflow

## The Problem

On Windows, **Obsidian keeps files open** which prevents them from being deleted. If you try to lock the vault while Obsidian is still running, the plaintext files **will NOT be deleted** and your notes remain unencrypted on disk!

## ✅ Correct Workflow

### 1. Unlock Vault
```
ObsidianSecure → Select Vault → Unlock → Enter Password
```

### 2. Launch Obsidian
```
ObsidianSecure → Launch Obsidian
```
You'll see a warning reminding you to close Obsidian before locking.

### 3. Work on Your Notes
Edit, create, modify your notes in Obsidian as usual.

### 4. **CLOSE OBSIDIAN COMPLETELY**
```
Obsidian → File → Exit (or Alt+F4)
```
⚠️ **CRITICAL**: Make sure Obsidian is fully closed! Check:
- No Obsidian window visible
- No Obsidian in system tray
- No Obsidian process in Task Manager

### 5. Lock the Vault
```
ObsidianSecure → Lock
```
You'll be asked to confirm you've closed Obsidian.

### 6. Verify
The workspace should be deleted. Check:
```
%LOCALAPPDATA%\ObsidianSecure\workspace\
```
This folder should be empty or not exist.

## ❌ What NOT to Do

- ❌ Don't lock while Obsidian is running
- ❌ Don't close ObsidianSecure while vault is unlocked
- ❌ Don't manually delete workspace files
- ❌ Don't open multiple instances of the workspace

## 🔒 Security Impact

If you lock while Obsidian is running:
- ✅ Modified files ARE re-encrypted
- ✅ Index IS updated
- ❌ **Plaintext files are NOT deleted**
- ❌ **Your notes remain unencrypted on disk!**

## 🛠️ If You Forgot to Close Obsidian

If you tried to lock and got an error about files being locked:

1. **Close Obsidian now**
2. **Click Lock again** in ObsidianSecure
3. The workspace will be properly deleted this time

## 📋 Quick Checklist

Before clicking "Lock":
- [ ] Saved all your work in Obsidian
- [ ] Closed Obsidian completely (File → Exit)
- [ ] Checked Obsidian is not in Task Manager
- [ ] Checked Obsidian is not in system tray

Then:
- [ ] Click "Lock" in ObsidianSecure
- [ ] Wait for "Vault locked successfully"
- [ ] Verify workspace is gone

## 🎯 Best Practices

1. **Always close Obsidian before locking**
2. **Never leave the vault unlocked when away from computer**
3. **Check workspace is deleted after locking**
4. **Use strong passwords (12+ characters)**
5. **Keep encrypted vault backups**

## 🐛 Troubleshooting

### "Failed to delete files" error
**Cause**: Obsidian or another program has files open

**Solution**:
1. Close Obsidian completely
2. Close any file explorers viewing the workspace
3. Try locking again

### Files still exist after locking
**Cause**: Locking failed silently (old bug - now fixed!)

**Solution**:
1. Update to latest version
2. Close Obsidian
3. Lock again

### Obsidian reopens in workspace
**Cause**: You reopened Obsidian and it remembered the last vault

**Solution**:
1. Close Obsidian
2. Lock the vault
3. Delete the workspace manually if needed:
   ```
   rmdir /s "%LOCALAPPDATA%\ObsidianSecure\workspace"
   ```

## 📞 Remember

**Your security depends on following this workflow correctly!**

If the workspace is not deleted, your notes are sitting unencrypted on disk, defeating the entire purpose of ObsidianSecure.

---

**Always**: Unlock → Launch Obsidian → Work → **Close Obsidian** → Lock
