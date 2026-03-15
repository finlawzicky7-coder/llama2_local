import { useState, useEffect } from 'react';
import {
  generateId,
  loadContacts,
  saveContacts,
  loadCalls,
  saveCalls,
  todayString,
} from './utils';
import ContactList from './components/ContactList';
import ContactDetail from './components/ContactDetail';
import ContactForm from './components/ContactForm';
import ReminderList from './components/ReminderList';

/*
  App is the single source of truth for contacts and calls.
  It handles all data mutations and passes data + callbacks down to children.
  Navigation is simple: we track a "view" string and an optional selectedContactId.
*/
export default function App() {
  // --- State ---
  const [contacts, setContacts] = useState(() => loadContacts());
  const [calls, setCalls] = useState(() => loadCalls());
  const [view, setView] = useState('contacts'); // 'contacts' | 'detail' | 'reminders'
  const [selectedContactId, setSelectedContactId] = useState(null);
  const [editingContact, setEditingContact] = useState(null);
  const [showContactForm, setShowContactForm] = useState(false);

  // --- Persist to localStorage whenever data changes ---
  useEffect(() => {
    saveContacts(contacts);
  }, [contacts]);

  useEffect(() => {
    saveCalls(calls);
  }, [calls]);

  // --- Contact CRUD ---
  function addContact(data) {
    const newContact = {
      id: generateId(),
      name: data.name,
      phone: data.phone || '',
      email: data.email || '',
      company: data.company || '',
      notes: data.notes || '',
      createdAt: todayString(),
      lastContactedAt: null,
    };
    setContacts((prev) => [...prev, newContact]);
    setShowContactForm(false);
  }

  function updateContact(id, data) {
    setContacts((prev) =>
      prev.map((c) => (c.id === id ? { ...c, ...data } : c))
    );
    setEditingContact(null);
    setShowContactForm(false);
  }

  function deleteContact(id) {
    if (!window.confirm('Delete this contact and all their call logs?')) return;
    setContacts((prev) => prev.filter((c) => c.id !== id));
    setCalls((prev) => prev.filter((call) => call.contactId !== id));
    setView('contacts');
    setSelectedContactId(null);
  }

  // --- Call CRUD ---
  function addCall(callData) {
    const newCall = {
      id: generateId(),
      contactId: callData.contactId,
      date: callData.date,
      direction: callData.direction,
      summary: callData.summary,
      notes: callData.notes || '',
      followUpDate: callData.followUpDate || null,
      completed: false,
    };
    setCalls((prev) => [...prev, newCall]);

    // Update lastContactedAt on the contact
    setContacts((prev) =>
      prev.map((c) =>
        c.id === callData.contactId
          ? { ...c, lastContactedAt: callData.date }
          : c
      )
    );
  }

  function markFollowUpDone(callId) {
    setCalls((prev) =>
      prev.map((call) =>
        call.id === callId ? { ...call, completed: true } : call
      )
    );
  }

  // --- Navigation helpers ---
  function viewContact(id) {
    setSelectedContactId(id);
    setView('detail');
  }

  function openAddContact() {
    setEditingContact(null);
    setShowContactForm(true);
  }

  function openEditContact(contact) {
    setEditingContact(contact);
    setShowContactForm(true);
  }

  function closeForm() {
    setEditingContact(null);
    setShowContactForm(false);
  }

  // --- Reminder count for the nav badge ---
  const today = todayString();
  const dueCount = calls.filter(
    (c) => c.followUpDate && c.followUpDate <= today && !c.completed
  ).length;

  // --- Render ---
  const selectedContact = contacts.find((c) => c.id === selectedContactId);
  const contactCalls = calls
    .filter((c) => c.contactId === selectedContactId)
    .sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div className="app">
      <nav className="nav-bar">
        <div className="nav-brand">Simple CRM</div>
        <div className="nav-links">
          <button
            className={`nav-link ${view === 'contacts' || view === 'detail' ? 'active' : ''}`}
            onClick={() => {
              setView('contacts');
              setSelectedContactId(null);
              closeForm();
            }}
          >
            Contacts
          </button>
          <button
            className={`nav-link ${view === 'reminders' ? 'active' : ''}`}
            onClick={() => {
              setView('reminders');
              setSelectedContactId(null);
              closeForm();
            }}
          >
            Reminders{dueCount > 0 && <span className="badge">{dueCount}</span>}
          </button>
        </div>
      </nav>

      <main className="main-content">
        {showContactForm && (
          <ContactForm
            contact={editingContact}
            onSave={(data) => {
              if (editingContact) {
                updateContact(editingContact.id, data);
              } else {
                addContact(data);
              }
            }}
            onCancel={closeForm}
          />
        )}

        {view === 'contacts' && !showContactForm && (
          <ContactList
            contacts={contacts}
            onView={viewContact}
            onAdd={openAddContact}
          />
        )}

        {view === 'detail' && selectedContact && !showContactForm && (
          <ContactDetail
            contact={selectedContact}
            calls={contactCalls}
            onBack={() => {
              setView('contacts');
              setSelectedContactId(null);
            }}
            onEdit={() => openEditContact(selectedContact)}
            onDelete={() => deleteContact(selectedContact.id)}
            onAddCall={addCall}
          />
        )}

        {view === 'reminders' && (
          <ReminderList
            calls={calls}
            contacts={contacts}
            onMarkDone={markFollowUpDone}
            onViewContact={viewContact}
          />
        )}
      </main>
    </div>
  );
}
