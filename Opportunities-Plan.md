---
name: Opportunities Work Packages
overview: Opportunities feature split into 5 sequential work packages. Each package is fully implemented and tested before proceeding to the next.
todos:
  - id: wp1-model
    content: "WP1: Create Opportunity SQLAlchemy model with OpportunityStage enum"
    status: pending
  - id: wp1-schema
    content: "WP1: Create Pydantic schemas (OpportunityCreate, Update, Response)"
    status: pending
  - id: wp1-migration
    content: "WP1: Run database migration and verify table creation"
    status: pending
  - id: wp1-test
    content: "WP1: Test model instantiation and relationships"
    status: pending
  - id: wp2-service
    content: "WP2: Implement opportunity_service.py with all CRUD methods"
    status: pending
  - id: wp2-conversion
    content: "WP2: Implement lead-to-opportunity conversion logic"
    status: pending
  - id: wp2-stats
    content: "WP2: Implement pipeline statistics aggregation"
    status: pending
  - id: wp2-test
    content: "WP2: Test all service methods"
    status: pending
  - id: wp3-routes
    content: "WP3: Create opportunities API routes with all endpoints"
    status: pending
  - id: wp3-register
    content: "WP3: Register routes in main.py"
    status: pending
  - id: wp3-test
    content: "WP3: Test all API endpoints via Swagger/curl"
    status: pending
  - id: wp4-types
    content: "WP4: Add Opportunity TypeScript types"
    status: pending
  - id: wp4-hook
    content: "WP4: Create use-opportunities hook"
    status: pending
  - id: wp4-list
    content: "WP4: Build Opportunities list page with filters"
    status: pending
  - id: wp4-dialog
    content: "WP4: Build OpportunityDialog for create/edit"
    status: pending
  - id: wp4-test
    content: "WP4: Test list view CRUD operations in browser"
    status: pending
  - id: wp5-pipeline
    content: "WP5: Build Pipeline Kanban board with drag-and-drop"
    status: pending
  - id: wp5-convert
    content: "WP5: Add lead conversion UI to Leads page"
    status: pending
  - id: wp5-dashboard
    content: "WP5: Add opportunity KPIs to Dashboard"
    status: pending
  - id: wp5-test
    content: "WP5: End-to-end testing of full opportunity workflow"
    status: pending
---

# Opportunities Feature - Work Packages

Each work package is self-contained and must be fully implemented and tested before proceeding to the next.

---

## Work Package 1: Backend Data Layer

**Goal:** Create the database model, schemas, and migration for opportunities.

### Deliverables
- `backend/src/models/opportunity.py` - SQLAlchemy model with OpportunityStage enum
- `backend/src/schemas/opportunity.py` - Pydantic schemas (Create, Update, Response)
- Database migration creating `opportunities` table
- Update `backend/src/models/__init__.py` to export Opportunity

### Data Model

```python
class OpportunityStage(str, Enum):
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
```

### Testing Criteria
- [ ] Migration runs successfully (table created)
- [ ] Model can be instantiated with all required fields
- [ ] Relationships to Company, Contact, Lead work correctly
- [ ] Enum values are stored/retrieved correctly

---

## Work Package 2: Backend Service Layer

**Goal:** Implement business logic for opportunity operations.

### Deliverables
- `backend/src/services/opportunity_service.py` with:
  - `create_opportunity()`
  - `get_opportunity()` / `get_opportunities()`
  - `update_opportunity()`
  - `delete_opportunity()`
  - `convert_lead_to_opportunity()`
  - `close_opportunity()`
  - `get_pipeline_stats()`

### Business Rules
- Lead conversion: Only QUALIFIED leads can be converted
- Stage transitions: Cannot skip directly to CLOSED states
- Probability auto-updates based on stage (configurable)
- Closing sets `actual_close_date` automatically

### Testing Criteria
- [ ] CRUD operations work correctly
- [ ] Lead conversion creates opportunity and updates lead status to CONVERTED
- [ ] Stage transition validation works
- [ ] Pipeline stats return correct aggregations
- [ ] Unit tests pass for all service methods

---

## Work Package 3: Backend API Layer

**Goal:** Expose opportunity operations via REST API.

### Deliverables
- `backend/src/api/routes/opportunities.py` with endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/opportunities` | List with filters (stage, company, owner) |
| GET | `/api/opportunities/{id}` | Get single opportunity |
| POST | `/api/opportunities` | Create new opportunity |
| PUT | `/api/opportunities/{id}` | Update opportunity |
| DELETE | `/api/opportunities/{id}` | Delete opportunity |
| POST | `/api/opportunities/convert/{lead_id}` | Convert lead to opportunity |
| POST | `/api/opportunities/{id}/close` | Close opportunity (won/lost) |
| GET | `/api/opportunities/stats` | Pipeline statistics |

- Register routes in `backend/src/api/routes/__init__.py`
- Update `backend/src/main.py` to include router

### Testing Criteria
- [ ] All endpoints return correct status codes
- [ ] Validation errors return 422 with details
- [ ] Filters work correctly (stage, company_id, etc.)
- [ ] Lead conversion endpoint works end-to-end
- [ ] API can be tested via Swagger UI at `/docs`

---

## Work Package 4: Frontend Data Layer and List View

**Goal:** Create data hooks and basic opportunities list view.

### Deliverables
- `frontend/src/lib/types.ts` - Add Opportunity types
- `frontend/src/hooks/use-opportunities.ts` - Data fetching hook
- `frontend/src/pages/Opportunities.tsx` - Table view with:
  - Sortable columns (Name, Company, Value, Stage, Close Date)
  - Stage filter dropdown
  - Search by name/company
  - Row click opens detail dialog
- `frontend/src/components/opportunities/OpportunityDialog.tsx` - Create/Edit modal
- Update `frontend/src/App.tsx` - Add route

### Testing Criteria
- [ ] List loads and displays opportunities from API
- [ ] Filters work correctly
- [ ] Create dialog submits and refreshes list
- [ ] Edit dialog loads existing data and updates
- [ ] Delete confirmation works
- [ ] Stage badges show correct colors
- [ ] Currency formatting for expected_value

---

## Work Package 5: Pipeline Board and Integration

**Goal:** Build Kanban pipeline view, lead conversion UI, and dashboard integration.

### Deliverables

**Pipeline Board:**
- `frontend/src/pages/Pipeline.tsx` - Kanban board with:
  - Columns for each stage (except CLOSED states combined)
  - Drag-and-drop between columns
  - Opportunity cards showing: Name, Company, Value, Close Date
  - Quick actions (Edit, Close)
  - Column totals (count + value sum)

**Lead Conversion:**
- Update `frontend/src/pages/Leads.tsx` - Add "Convert to Opportunity" action for QUALIFIED leads
- `frontend/src/components/opportunities/ConvertLeadDialog.tsx` - Conversion modal

**Dashboard Integration:**
- Update `frontend/src/pages/Dashboard.tsx` with KPIs:
  - Total Pipeline Value
  - Win Rate %
  - Opportunities by Stage (bar chart)
  - Recent Opportunities list

**Navigation:**
- Update sidebar with Pipeline and Opportunities links

### Testing Criteria
- [ ] Pipeline board renders all stages correctly
- [ ] Drag-and-drop updates opportunity stage via API
- [ ] Lead conversion creates opportunity and marks lead as CONVERTED
- [ ] Dashboard KPIs display correct values
- [ ] Close opportunity dialog records won/lost reason
- [ ] Navigation between views works

---

## Execution Order

```
WP1 ──────► WP2 ──────► WP3 ──────► WP4 ──────► WP5
Data        Service     API         List UI     Pipeline
Layer       Layer       Layer       + CRUD      + Dashboard
```

Each package builds on the previous. No frontend work until backend API is complete and tested.
