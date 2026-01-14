"""
Test configuration and fixtures for the Callcenter Backend.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from src.core.database import Base, get_db
from src.main import app
from src.models.company import Company
from src.models.contact import Contact
from src.models.lead import Lead, LeadStatus
from src.models.campaign import Campaign
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.contact_history import ContactHistory, HistoryType
from src.models import Setting, LookupValue  # noqa: F401 - needed for metadata


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with StaticPool for in-memory database
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============== Test Data Fixtures ==============

@pytest_asyncio.fixture
async def sample_company(db_session: AsyncSession) -> Company:
    """Create a sample company for testing."""
    company = Company(
        name="Test GmbH",
        street="Teststraße 1",
        zip_code="1010",
        city="Wien",
        country="Österreich",
        website="https://test.at",
        phone="+43 1 1234567",
        email="info@test.at",
        employee_count=50,
        potential_category="A",
        industry="IT",
    )
    db_session.add(company)
    await db_session.flush()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def sample_contact(db_session: AsyncSession, sample_company: Company) -> Contact:
    """Create a sample contact for testing."""
    contact = Contact(
        first_name="Max",
        last_name="Mustermann",
        email="max.mustermann@test.at",
        phone="+43 1 9876543",
        mobile="+43 664 1234567",
        position="Geschäftsführer",
        department="Management",
        salutation="Herr",
        title="Mag.",
        is_primary=True,
        is_active=True,
        company_id=sample_company.id,
    )
    db_session.add(contact)
    await db_session.flush()
    await db_session.refresh(contact)
    return contact


@pytest_asyncio.fixture
async def sample_contact_no_company(db_session: AsyncSession) -> Contact:
    """Create a sample contact without company for testing."""
    contact = Contact(
        first_name="Erika",
        last_name="Musterfrau",
        email="erika.musterfrau@example.at",
        phone="+43 1 5555555",
        is_active=True,
    )
    db_session.add(contact)
    await db_session.flush()
    await db_session.refresh(contact)
    return contact


@pytest_asyncio.fixture
async def sample_campaign(db_session: AsyncSession) -> Campaign:
    """Create a sample campaign for testing."""
    campaign = Campaign(
        name="Winter Kampagne 2026",
        description="Testkampagne für Q1",
        type="landing_page",
        source="google",
        is_active=True,
        landing_page_url="https://landing.test.at/winter2026",
    )
    db_session.add(campaign)
    await db_session.flush()
    await db_session.refresh(campaign)
    return campaign


@pytest_asyncio.fixture
async def sample_lead(
    db_session: AsyncSession, sample_contact: Contact, sample_campaign: Campaign
) -> Lead:
    """Create a sample lead for testing."""
    lead = Lead(
        status=LeadStatus.NEW,
        source="landing_page",
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="winter2026",
        contact_id=sample_contact.id,
        campaign_id=sample_campaign.id,
    )
    db_session.add(lead)
    await db_session.flush()
    await db_session.refresh(lead)
    return lead


@pytest_asyncio.fixture
async def sample_task(db_session: AsyncSession, sample_contact: Contact) -> Task:
    """Create a sample task for testing."""
    task = Task(
        title="Rückruf vereinbaren",
        description="Kontakt anrufen wegen Angebot",
        status=TaskStatus.OPEN,
        priority=TaskPriority.HIGH,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
        assigned_to="current_user",
        created_by="current_user",
        contact_id=sample_contact.id,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def sample_overdue_task(db_session: AsyncSession, sample_contact: Contact) -> Task:
    """Create an overdue task for testing."""
    task = Task(
        title="Überfällige Aufgabe",
        description="Diese Aufgabe ist überfällig",
        status=TaskStatus.OPEN,
        priority=TaskPriority.URGENT,
        due_date=datetime.now(timezone.utc) - timedelta(days=2),
        assigned_to="current_user",
        created_by="current_user",
        contact_id=sample_contact.id,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def sample_history_note(db_session: AsyncSession, sample_contact: Contact) -> ContactHistory:
    """Create a sample history note for testing."""
    history = ContactHistory(
        contact_id=sample_contact.id,
        type=HistoryType.NOTE,
        title="Notiz hinzugefügt",
        content="Interessent hat Interesse an Produkt X gezeigt",
        created_by="current_user",
    )
    db_session.add(history)
    await db_session.flush()
    await db_session.refresh(history)
    return history


@pytest_asyncio.fixture
async def sample_history_call(db_session: AsyncSession, sample_contact: Contact) -> ContactHistory:
    """Create a sample call history entry for testing."""
    import json
    history = ContactHistory(
        contact_id=sample_contact.id,
        type=HistoryType.CALL,
        title="Anruf dokumentiert",
        content="Gespräch über Angebot geführt, Follow-up in 1 Woche",
        extra_data=json.dumps({"duration_minutes": 15, "outcome": "reached"}),
        created_by="current_user",
    )
    db_session.add(history)
    await db_session.flush()
    await db_session.refresh(history)
    return history


@pytest_asyncio.fixture
async def multiple_contacts(db_session: AsyncSession, sample_company: Company) -> list[Contact]:
    """Create multiple contacts for pagination/search testing."""
    contacts = [
        Contact(
            first_name="Anna",
            last_name="Schmidt",
            email="anna.schmidt@test.at",
            is_active=True,
            company_id=sample_company.id,
        ),
        Contact(
            first_name="Peter",
            last_name="Wagner",
            email="peter.wagner@test.at",
            is_active=True,
            company_id=sample_company.id,
        ),
        Contact(
            first_name="Maria",
            last_name="Huber",
            email="maria.huber@test.at",
            is_active=True,
        ),
        Contact(
            first_name="Thomas",
            last_name="Maier",
            email="thomas.maier@test.at",
            is_active=False,  # Inactive contact
        ),
        Contact(
            first_name="Lisa",
            last_name="Berger",
            email="lisa.berger@test.at",
            is_active=True,
            title="Dr.",
        ),
    ]
    for contact in contacts:
        db_session.add(contact)
    await db_session.flush()
    for contact in contacts:
        await db_session.refresh(contact)
    return contacts


@pytest_asyncio.fixture
async def multiple_leads(
    db_session: AsyncSession, multiple_contacts: list[Contact], sample_campaign: Campaign
) -> list[Lead]:
    """Create multiple leads for testing."""
    leads = []
    statuses = [LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED, LeadStatus.NEW, LeadStatus.CONVERTED]
    
    for i, (contact, status) in enumerate(zip(multiple_contacts, statuses)):
        lead = Lead(
            status=status,
            source="import" if i % 2 == 0 else "landing_page",
            contact_id=contact.id,
            campaign_id=sample_campaign.id if i < 3 else None,
        )
        db_session.add(lead)
        leads.append(lead)
    
    await db_session.flush()
    for lead in leads:
        await db_session.refresh(lead)
    return leads
