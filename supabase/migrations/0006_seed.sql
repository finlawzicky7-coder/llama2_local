-- ============================================================================
-- 0006_seed.sql
-- Minimal seed data: example campaigns, one demo agent (replace before prod).
-- DO NOT use these phone/email values in production.
-- ============================================================================

insert into campaigns (name, channel, product_focus, utm_source, utm_medium, utm_campaign)
values
  ('Google Search — Medicare Review',  'google',     'MAPD','google','cpc','medicare-review-evergreen'),
  ('Google Search — T65 Birthday',     'google',     'T65', 'google','cpc','t65-birthday'),
  ('Local SEO — City Pages',           'seo',        'MAPD','seo',   'organic','local-pages'),
  ('YouTube — Medicare Education',     'youtube',    'MAPD','youtube','video','education-evergreen'),
  ('Meta — Retargeting Educated',      'meta',       'MAPD','meta',  'social','retarget-educated'),
  ('Direct Mail — QR Postcards',       'directmail', 'T65', 'directmail','qr','t65-postcards-2026'),
  ('Referral — Existing Clients',      'referral',   'MAPD','referral','word_of_mouth','client-referrals'),
  ('Community — Senior Center Events', 'event',      'MAPD','event', 'community','senior-events-2026')
on conflict do nothing;

-- Demo agent (REPLACE BEFORE PROD)
insert into agents (full_name, email, phone, npn, active, fmo, timezone)
values ('Demo Agent','demo@example.com','+10000000000','99999999',true,'Your FMO','America/New_York')
on conflict (email) do nothing;
