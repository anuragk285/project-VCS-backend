# Contributing to Vinayaka Cloth Store

These rules keep five people's work fitting together. Read them once. The same file is in the frontend and the backend repository.

First time here? Follow `TEAM-SETUP.md` (frontend repo) to get everything running.

## 1. How we pick work

1. Open the task queue document and choose a task whose "Needs" tasks are done.
2. Write your name in **Responsibility taken** and set **Status** to In progress. One task per person at a time.
3. Stuck for more than a day? Say so in the group chat and clear your name so someone else can take it.
4. Exam weeks: take only **D** and **C** tasks.

## 2. Branches and commits

- Never work on `main`, and never push straight to it.
- Start from the latest `main`:
  ```
  git switch main
  git pull
  git switch -c feature/short-task-name
  ```
- Branch names: `feature/cart-page`, `fix/login-error`, `chore/add-eslint`.
- Commit often with a short message that says what changed: `Add cloth card component`. Not `changes` or `fix`.
- Keep a branch small: one task, one pull request.
- Never commit `.env`, passwords, API keys or `node_modules`. Add new settings to `.env.example` with empty values.

## 3. Pull requests

1. Push your branch and open a pull request into `main`.
2. In the description write: the task number and name, what you did, and how to test it. For anything visible, add a screenshot (phone and desktop width).
3. Another member reviews it. Reviewers: check that it runs, that the code is readable, and that the rules in this file are followed.
4. Fix review comments on the same branch. Merge only after one approval and green checks.
5. After merging, update the task status to **Done**.

## 4. Frontend rules

- **Colours: only our theme classes** from `src/index.css` (`bg-card`, `text-primary`, `border-border` and so on). No `bg-blue-500`, `bg-white`, `text-[#123456]`, no hex in code, no `dark:`. The list is in `TEAM-SETUP.md`. Run `npm run check:colours` before every commit.
- Need a new colour? Ask in the group, then add one named token in `src/index.css`. Do not invent it in your own file.
- TypeScript strict. Do not use `any`. Give props and API data proper types.
- Folders: `src/pages` (one file per route), `src/components` (shared pieces), `src/features/<name>` (cart, catalogue, studio ...), `src/api` (calls to the backend), `src/lib` (helpers).
- Server data goes through TanStack Query. Do not fetch inside `useEffect`.
- Add shadcn components with `npx shadcn@latest add <name>` and commit the generated file. Do not edit files in `src/components/ui` by hand unless the whole team agrees.
- Body text is at least 16 px (`text-base`). `text-sm` only for captions, labels and chips. Tap targets at least 44 px high.
- All text on screen is in English.
- Before a pull request: `npm run build`, `npm run lint` and `npm run check:colours` all pass.

## 5. Backend rules

- Structure: `app/api` (routes), `app/models` (database tables), `app/schemas` (request and response shapes), `app/services` (business logic), `app/core` (settings, security).
- Routes stay thin. Put the logic in `app/services`. Never return a database model directly; return a schema.
- Money and metres use `Decimal` and `Numeric`, never `float`.
- Anything that changes stock or creates an order runs in **one database transaction**.
- Every database change goes through an Alembic migration (`alembic revision --autogenerate -m "short message"`). Check the generated file before committing it, and **commit the `migrations` folder**. Do not edit a migration that is already merged; write a new one.
- Secrets and settings come from `.env` through `pydantic-settings`. Never hard-code them.
- Write at least one test for every endpoint. Before a pull request: `ruff check .` and `pytest` pass.
- Adding a package? Install it, then run `pip freeze > requirements.txt` and commit the file.

## 6. Good habits

- Run `git pull` on `main` before starting anything new.
- If two people need the same file, tell the group so you do not edit it at once.
- Ask early. A question in the group costs a minute; a day lost to being stuck costs much more.
- Be kind in reviews: say what is good, then what to change, and why.

## 7. Definition of done

A task is Done when: it works on phone and desktop width, the checks pass, another member approved the pull request, it is merged into `main`, and the task queue shows **Done** with your name.
