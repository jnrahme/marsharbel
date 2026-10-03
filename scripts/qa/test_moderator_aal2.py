"""Static guards: moderation is enforced as aal2 in the database, not only in page JS."""
import re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MIG = sorted((ROOT / 'supabase/migrations').glob('*.sql'))
DEF = re.compile(r'create or replace function public\.testimony_is_moderator\(\).*?\$\$(.*?)\$\$', re.S | re.I)

class ModeratorAal2(unittest.TestCase):
    def last_definition(self):
        last = None
        for f in MIG:
            for m in DEF.finditer(f.read_text()):
                last = (f.name, m.group(1))
        self.assertIsNotNone(last)
        return last

    def test_latest_is_moderator_requires_user_role_and_aal2(self):
        name, body = self.last_definition()
        self.assertIn('auth.uid() is not null', body, name)
        self.assertIn("app_metadata'->>'role'", body, name)
        self.assertIn("auth.jwt()->>'aal'", body, name)
        self.assertIn("'aal2'", body, name)

    def test_no_password_only_override_is_last(self):
        name, _ = self.last_definition()
        self.assertNotIn('password_access', name)

    def test_moderation_rpcs_call_the_check_first(self):
        text = '\n'.join(f.read_text() for f in MIG)
        for fn in ('testimony_moderate', 'testimony_set_controls', 'testimony_resolve_report', 'testimony_retry_review', 'testimony_manual_review'):
            m = re.search(r'function public\.%s\(.*?\$\$(.*?)\$\$' % fn, text, re.S)
            self.assertIsNotNone(m, fn)
            self.assertIn('testimony_require_moderator()', m.group(1), fn)

    def test_moderator_policies_use_the_function(self):
        text = '\n'.join(f.read_text() for f in MIG)
        for table in ('testimony_controls', 'testimony_audit', 'testimony_reports'):
            m = re.search(r'create policy \w+ on public\.%s for select[^;]*;' % table, text, re.I)
            self.assertIsNotNone(m, table)
            self.assertIn('testimony_is_moderator()', m.group(0), table)

    def test_client_requires_mfa(self):
        cfg = (ROOT / 'testimony-config.js').read_text()
        self.assertRegex(cfg, r'moderatorMfaRequired:\s*true')
        js = (ROOT / 'testimony-admin.js').read_text()
        self.assertIn("'aal2'", js)
        self.assertIn('getAuthenticatorAssuranceLevel', js)

if __name__ == '__main__':
    unittest.main()
