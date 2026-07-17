# Wilson Lab Demo Script

## Current two-minute demonstration

### 1. Frame the customer problem

> Small technical teams often need a safer way to understand and operate lab infrastructure without giving every user unrestricted Docker access.

Explain that Wilson Lab presents a narrow product surface around inventory, roles, confirmation, and auditability.

### 2. Show the public dashboard

- Open the GitHub Pages dashboard.
- Search for a resource.
- Filter by a tag.
- Sort by name and recent activity.
- Explain that the current public UI uses mock inventory until M3 connects authenticated API sessions.

### 3. Show the API contract

Run the backend in mock mode and open `/docs`.

Demonstrate:

- public `/health`
- token login
- Viewer identity
- authenticated inventory
- resource details
- Administrator-only operations
- Administrator-only audit history

### 4. Demonstrate the safety controls

Log in as Viewer and show that an operation returns 403.

Log in as Administrator:

1. Request an operation without confirmation and show the 409 response.
2. Submit the confirmed operation.
3. Show the updated resource state.
4. Open the audit endpoint and show the actor, resource, outcome, timestamp, and request identifier.
5. Repeat an invalid transition and show that the failed attempt is also audited.

### 5. Explain the Docker boundary

- The API accepts only `start`, `stop`, and `restart` enums.
- Docker inventory is filtered to `wilson-lab.managed=true`.
- A resource is checked against the label again before use.
- The project exposes no shell, create, delete, pull, host-path, or arbitrary Docker functionality.
- The real runtime will live on an isolated cloud sandbox, not a personal network.

## Current truthful status

### Complete

- React/TypeScript dashboard
- Search, tags, sorting, status cards, and UTC timestamps
- FastAPI control-plane foundation
- JWT authentication
- Viewer/Admin authorization
- Mock and Docker adapters
- Confirmed safe operations
- Action and audit persistence
- Frontend and backend CI
- Architecture and security documentation

### Next

- Connect the dashboard to authenticated API sessions
- Show live/mock source state
- Enable role-aware buttons and confirmation UI
- Add resource details and Administrator audit panel
- Deploy a dedicated HTTPS cloud sandbox

## Interview talking points

- **Discovery:** narrowed a broad “manage a cyber lab” idea into a safe, demonstrable MVP.
- **Product judgment:** built the user-facing inventory before adding privileged operations.
- **Security:** used layered controls rather than trusting a disabled browser button.
- **Communication:** documented current versus planned capability to avoid overstating the product.
- **Delivery:** separated frontend and backend CI and preserved a chronological build log.
- **Tradeoff:** selected SQLite and mock runtime for a single-instance showcase while documenting what production would require.
