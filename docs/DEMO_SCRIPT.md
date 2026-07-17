# Wilson Lab Demo Script

## Current three-minute demonstration

### 1. Frame the customer problem

> Small technical teams often need a safer way to understand and operate lab infrastructure without giving every user unrestricted Docker access.

Explain that Wilson Lab presents a deliberately narrow control surface around inventory, roles, confirmation, and auditability.

### 2. Show the public dashboard

- Open the GitHub Pages dashboard.
- Point out the API availability and Demo Data indicators.
- Search for a resource, filter by tag, and sort the inventory.
- Open a resource detail drawer.
- Explain that the dashboard stays useful even before a cloud API is connected.

### 3. Connect to the local or cloud API

- Start the FastAPI backend in mock mode.
- Refresh the dashboard and show that the API indicator changes to Available.
- Sign in as the Viewer account.
- Point out that the data source changes from Demo Data to Live Inventory.
- Show that Viewer access exposes details but no resource operations.

### 4. Demonstrate Administrator controls

Sign out and sign in as Administrator:

1. Open a running resource.
2. Select a backend-provided action such as restart or stop.
3. Show the explicit confirmation dialog.
4. Confirm the operation.
5. Show the updated resource state.
6. Open the audit timeline and identify the actor, resource, outcome, timestamp, and request identifier.
7. Explain that failed operations are also retained as evidence.

### 5. Explain the safety controls

- The browser never sends raw Docker commands.
- The API accepts only `start`, `stop`, and `restart` enums.
- The UI renders only actions returned by the API for the current resource state.
- Server-side RBAC remains authoritative even if browser code is modified.
- Docker inventory is filtered to `wilson-lab.managed=true`.
- A resource is checked against the label again before use.
- The project exposes no shell, create, delete, pull, host-path, or arbitrary Docker functionality.
- The real runtime belongs on an isolated cloud sandbox, not a personal network.

## Current truthful status

### Complete

- React/TypeScript dashboard
- Search, tags, sorting, status cards, and UTC timestamps
- FastAPI control-plane foundation
- JWT authentication
- Viewer/Admin authorization
- Validated live API responses
- Session-scoped browser storage
- Live-versus-demo source state
- Role-aware resource controls
- Confirmation dialog
- Resource details
- Administrator audit timeline
- Mock and Docker adapters
- Action and audit persistence
- Frontend and backend CI
- Architecture and security documentation

### Next

- Deploy the API to a dedicated HTTPS cloud sandbox
- Add labeled demonstration containers
- Configure the production `VITE_API_ORIGIN`
- Add reverse-proxy, TLS, backup, and recovery runbooks
- Capture final screenshots and a short demonstration recording

## Interview talking points

- **Discovery:** narrowed a broad “manage a cyber lab” idea into a safe, demonstrable MVP.
- **Product judgment:** preserved a useful public demo instead of allowing backend downtime to break the experience.
- **Security:** used layered controls rather than trusting hidden or disabled browser buttons.
- **Resilience:** invalid and expired sessions return safely to demo mode.
- **Communication:** surfaced data provenance so viewers know whether they are seeing simulated or live state.
- **Testing:** added frontend contract tests without expanding the dependency surface.
- **Delivery:** separated frontend and backend CI and preserved a chronological build log.
- **Tradeoff:** selected SQLite and a mock runtime for a single-instance showcase while documenting what production would require.
