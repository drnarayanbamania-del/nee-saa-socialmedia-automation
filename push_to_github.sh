#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/drnarayanbamania-del/Bamania-scine-ai.git"
BRANCH="main"

printf "\n🚀 Preparing to push project to GitHub...\n"
printf "Repository: %s\n" "$REPO_URL"

if [ -n "$GITHUB_TOKEN" ]; then
  AUTH_REPO_URL="https://x-access-token:${GITHUB_TOKEN}@github.com/drnarayanbamania-del/Bamania-scine-ai.git"
  printf "✅ Using GITHUB_TOKEN from environment for authenticated push\n"
else
  AUTH_REPO_URL="$REPO_URL"
  printf "ℹ️ No GITHUB_TOKEN found in environment, using standard git auth\n"
fi

if [ ! -d ".git" ]; then
  git init
  printf "✅ Initialized git repository\n"
fi

if ! git config user.name >/dev/null; then
  printf "\nℹ️ Git user.name is not set.\n"
  printf "Run: git config --global user.name \"Your Name\"\n"
fi

if ! git config user.email >/dev/null; then
  printf "\nℹ️ Git user.email is not set.\n"
  printf "Run: git config --global user.email \"you@example.com\"\n"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
  printf "✅ Updated existing origin remote\n"
else
  git remote add origin "$REPO_URL"
  printf "✅ Added origin remote\n"
fi

git add .

if git diff --cached --quiet; then
  printf "ℹ️ No staged changes to commit.\n"
else
  git commit -m "feat: prepare Bamania's Cine AI for vercel deployment"
  printf "✅ Created commit\n"
fi

git branch -M "$BRANCH"
printf "✅ Set branch to %s\n" "$BRANCH"

printf "\n📤 Pushing to GitHub...\n"
git push -u "$AUTH_REPO_URL" "$BRANCH"

printf "\n🎉 Push complete!\n"
printf "GitHub Repo: %s\n" "$REPO_URL"
