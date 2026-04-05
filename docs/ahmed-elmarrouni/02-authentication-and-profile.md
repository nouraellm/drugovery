# Authentication and Profile Updates

## 1. Added a Sign-Up Page

**What I changed:** The app previously only had a login page. I created a new `Signup.js` page and fixed the React Router in `App.js` so it wouldn't redirect users away from it.
**Why I did this:** To make the app public-facing, users need to be able to create their own accounts without relying on the backend `create_admin.py` script.

## 2. Strict Input Validation & Better UX

**What I changed:** \* Added an "eye" icon to both the Login and Signup pages to let users show/hide their passwords.

- Added strict validation (Regex) on the Signup page: Full Name cannot have numbers, email must be valid, and passwords must be at least 8 characters with a mix of uppercase, lowercase, numbers, and symbols.
- Updated `api.js` to stop the page from instantly refreshing when a user types the wrong password, so they can actually read the error message.

## 3. Interactive User Profile in the Layout

**What I changed:** \* The top navigation bar now fetches and displays the logged-in user's full name next to their avatar.

- I added a "My Profile" option to the dropdown menu.
- Clicking "My Profile" opens a clean, read-only dialog showing the user's details.
- Clicking "Edit Details" switches the dialog into a form where the user can update their name, email, or password.

## 4. Backend Support for Profile Updates

**What I changed:** Added a new `UserUpdate` schema in `user.py` and created a new `PUT /me` endpoint in `auth.py`.
**Why I did this:** The frontend needed a secure way to save the profile changes back to the database.

## 5. UI/UX Redesign

**What I changed:** Replaced the basic Material-UI styling with a custom Light Mode theme in `App.js`. This includes clean indigo colors, rounded corners, soft shadows, and a full-screen gradient background for the login pages.

---

\_(Note: I made these UI/UX improvements using AI because the original style felt a bit old. I wanted to make it look clean and professional! I'm not sure if you already had a specific design in mind, so let me know what you think.)
