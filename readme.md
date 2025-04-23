# 📘 API Usage Guide

This document outlines the available API endpoints for authentication, user management, roles, payments, subscriptions, and account handling in the system. Each endpoint is categorized and described with its purpose and access requirements.

---

## 🔐 Authentication

### `GET /api/auth/me`

- **Description**: Retrieves the currently authenticated user.
- **Access**: Authenticated User (r)

### `POST /api/auth/login`

- **Description**: Logs in a user.
- **Access**: Public

### `POST /api/auth/register`

- **Description**: Registers a new user.
- **Access**: Public

---

## 🧑‍💼 Roles

### `POST /api/role/add`

- **Description**: Adds a new role to the system.
- **Access**: Admin (ad)

### `GET /api/role/all`

- **Description**: Fetches all available roles.
- **Access**: Admin (ad)

### `PUT /api/role/mod/`

- **Description**: Modifies an existing role.
- **Access**: Admin (ad)

### `DELETE /api/role/del`

- **Description**: Deletes an existing role.
- **Access**: Admin (ad)

---

## 👤 Users

### `POST /api/user/admin/add`

- **Description**: Adds an internal admin user.
- **Access**: Admin (ad)

### `GET /api/user/get/{identifier}`

- **Description**: Fetches a user by a given identifier (e.g., ID, username).
- **Access**: Authenticated User (r)

### `GET /api/user/all`

- **Description**: Retrieves all registered users.
- **Access**: Admin (ad)

### `PUT /api/user/mod`

- **Description**: Modifies the authenticated user’s details.
- **Access**: Authenticated User (r)

---

## 🛍️ Products

### `GET /api/plan/products`

- **Description**: Retrieves all available Stripe products.
- **Access**: Public/Authenticated User

---

## 💳 Payments

### `POST /api/payment/create-checkout-session`

- **Description**: Creates a new Stripe Checkout session for payment processing.
- **Access**: Authenticated User (r)

### `POST /api/payment/webhook`

- **Description**: Endpoint to receive Stripe webhook events (e.g., subscription updates).
- **Access**: Stripe (automated, secured)

---

## 📦 Subscriptions

### `GET /api/subscriptions/`

- **Description**: Retrieves all subscriptions of the current user.
- **Access**: Authenticated User (r)

### `PUT /api/subscriptions/{subscription_id}`

- **Description**: Updates a user’s subscription (typically status or plan).
- **Access**: Admin (ad)

### `GET /api/subscriptions/filter`

- **Description**: Fetches subscriptions based on filter criteria.
- **Access**: Admin (ad)

### `GET /api/subscriptions/me`

- **Description**: Retrieves the currently active subscription of the user.
- **Access**: Authenticated User (r)

---

## 🧾 Accounts

### `PUT /api/accounts/{account_id}`

- **Description**: Updates details of a specific user account.
- **Access**: Authenticated User (r)

### `GET /api/accounts/{account_id}`

- **Description**: Retrieves details for a specific user account.
- **Access**: Authenticated User (r)

### `POST /api/accounts/transfer`

- **Description**: Transfers money between accounts.
- **Access**: Authenticated User (r)

### `GET /api/accounts/transactions`

- **Description**: Retrieves a list of transactions associated with the current user.
- **Access**: Authenticated User (r)

### `GET /api/accounts/balance/me`

- **Description**: Fetches the current user’s account balance.
- **Access**: Authenticated User (r)

---

📌 **Note**: All authenticated routes require a valid JWT token in the `Authorization` header.
