# Branch Protection for Gusdaz-SSH

This document describes the branch protection configuration for the `Gusdaz-SSH` branch.

## Overview

The `Gusdaz-SSH` branch has special protections in place for the `opendbc_repo` directory. These protections ensure that files in this directory remain untouched through two mechanisms:

1. **Git merge strategy**: The `.gitattributes` file specifies that all files under `opendbc_repo/**` use the "ours" merge strategy, which always keeps the version from `Gusdaz-SSH` during merges.

2. **CI guard**: A GitHub Actions workflow blocks any pull request that attempts to modify files in `opendbc_repo`.

## Required Branch Protection Settings

To fully protect the `Gusdaz-SSH` branch, the following branch protection rules must be configured in GitHub:

### Steps to Configure

1. Navigate to: **Settings → Branches → Add rule**

2. Set the branch name pattern to: `Gusdaz-SSH`

3. Enable the following settings:

   - ✅ **Require a pull request before merging**
     - This ensures all changes go through code review

   - ✅ **Require status checks to pass before merging**
     - Under this option, search for and select:
       - `Protect opendbc_repo on Gusdaz-SSH / guard`

   - ✅ **Do not allow bypassing the above settings** (Recommended)
     - This prevents administrators from bypassing the protection

   - ✅ **Restrict who can push to matching branches** (Optional but recommended)
     - Select specific users or teams who are allowed to push

   - ✅ **Block force pushes**
     - This prevents history rewriting

4. Save the rule

## How It Works

### Merge Protection

The `.gitattributes` file contains:

```
# Always KEEP OUR VERSION of everything under opendbc_repo during merges
opendbc_repo/** merge=ours
```

This tells Git to always keep the `Gusdaz-SSH` version of files in `opendbc_repo` when merging from other branches. No Git configuration is needed; the "ours" merge driver is built into Git.

### CI Guard

The workflow at `.github/workflows/protect-opendbc.yml` runs on all pull requests targeting `Gusdaz-SSH`. It:

1. Checks out the code with full history
2. Compares the PR branch with `Gusdaz-SSH`
3. Looks for any changes in the `opendbc_repo` directory
4. Fails the check if any modifications are detected

When the check fails, GitHub will block the PR from being merged (if branch protection is configured as described above).

## Testing

### Test PR Protection

1. Create a test branch from `Gusdaz-SSH`
2. Modify any file in `opendbc_repo`
3. Open a pull request to `Gusdaz-SSH`
4. The workflow should fail with an error message listing the modified files
5. GitHub should show the PR as blocked from merging

### Test Merge Protection

1. Create a test branch from `Gusdaz-SSH`
2. Modify files in `opendbc_repo`
3. Commit and push the changes
4. Locally merge this branch into `Gusdaz-SSH`:
   ```bash
   git checkout Gusdaz-SSH
   git merge <test-branch>
   ```
5. Verify that files in `opendbc_repo` remain unchanged after the merge

## Troubleshooting

### CI check is not appearing

- Ensure the workflow file exists on the `Gusdaz-SSH` branch
- Check that the workflow file is syntactically correct
- The workflow will only run on PRs targeting `Gusdaz-SSH`, not other branches

### Merge strategy not working

- Verify the `.gitattributes` file exists on the `Gusdaz-SSH` branch
- Ensure the path pattern matches: `opendbc_repo/**` (note the spelling)
- The merge driver "ours" is built into Git and requires no additional configuration

### Force pushes are overriding protections

- Enable "Block force pushes" in the branch protection settings
- Consider restricting who can push to the branch
