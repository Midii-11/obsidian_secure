# Lock/Unlock Workflow Guide

## Normal Workflow

### 1. Unlock Vault
```
ObsidianSecure → Select Vault → Unlock → Enter Password
```

### 2. Launch Obsidian
```
ObsidianSecure → Launch Obsidian
```

### 3. Work on Your Notes
- Edit existing notes
- Create new files and folders
- Delete files
- All changes are automatically tracked

### 4. Lock the Vault
```
ObsidianSecure → Lock
```

**What happens:**
- All changes are saved and encrypted
- New files are added to the vault
- Deleted files are removed from the vault
- Workspace is securely deleted

### 5. Done!
Your encrypted vault is secure and the workspace is gone.

## Best Practices

1. **Close Obsidian before locking** (recommended)
   - Ensures clean shutdown
   - Prevents file locking issues

2. **If you forget to close Obsidian:**
   - Try locking anyway
   - If you get an error, close Obsidian and lock again
   - The app will tell you if there's a problem

3. **Never leave vault unlocked when away**
   - Always lock before stepping away
   - Your data is only protected when locked

4. **Use strong passwords** (12+ characters)

5. **Keep encrypted vault backups**

## Troubleshooting

### "Failed to delete files" error
**Cause**: Obsidian or another program has files open

**Solution**:
1. Close Obsidian completely (File → Exit)
2. Close any file explorers viewing the workspace
3. Click Lock again

The app will show you exactly what's wrong.

### Workspace verification
After locking, the workspace should be deleted:
```
%LOCALAPPDATA%\ObsidianSecure\workspace\
```

If files remain, it means locking failed. Check the error message and try again.

### App won't close / Console stays busy
If you close the app while vault is unlocked:
- The app will ask if you want to lock first
- Choose "Yes" to lock and exit cleanly
- Choose "No" to exit without locking (workspace remains)

## Quick Reference

**Full workflow:** Unlock → Launch Obsidian → Work → Lock

**Recommended:** Close Obsidian before locking

**If you forget:** The app will handle it and show errors if needed
