import { useState } from 'react';
import { formatDate, daysDiff } from '../utils';

/*
  ContactList shows all contacts in a searchable table.
  - Search filters by name, phone, or company (case-insensitive).
  - Each row has a "View" button to navigate to the detail view.
  - A subtle indicator shows if a contact hasn't been reached in 30+ days.
*/
export default function ContactList({ contacts, onView, onAdd }) {
  const [search, setSearch] = useState('');

  const filtered = contacts.filter((c) => {
    const q = search.toLowerCase();
    return (
      c.name.toLowerCase().includes(q) ||
      c.phone.toLowerCase().includes(q) ||
      c.company.toLowerCase().includes(q)
    );
  });

  return (
    <div className="contact-list">
      <div className="list-header">
        <h2>Contacts</h2>
        <button className="btn btn-primary" onClick={onAdd}>
          + Add Contact
        </button>
      </div>

      <input
        type="text"
        className="search-box"
        placeholder="Search by name, phone, or company…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {filtered.length === 0 ? (
        <div className="empty-state">
          {contacts.length === 0
            ? 'No contacts yet. Add your first one!'
            : 'No contacts match your search.'}
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Company</th>
              <th>Last Contacted</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => {
              const stale =
                !c.lastContactedAt ||
                daysDiff(c.lastContactedAt) <= -30;
              return (
                <tr key={c.id}>
                  <td>
                    {c.name}
                    {stale && (
                      <span className="stale-badge" title="Not contacted in 30+ days">
                        overdue
                      </span>
                    )}
                  </td>
                  <td>{c.phone || '—'}</td>
                  <td>{c.company || '—'}</td>
                  <td>{formatDate(c.lastContactedAt)}</td>
                  <td>
                    <button
                      className="btn btn-small"
                      onClick={() => onView(c.id)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
