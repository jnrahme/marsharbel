window.TESTIMONY_CONFIG = Object.freeze({
  // Public values only. Never place service-role or Turnstile secret keys here.
  supabaseUrl: 'https://YOUR_PROJECT.supabase.co',
  supabaseAnonKey: 'YOUR_SUPABASE_ANON_KEY',
  turnstileSiteKey: 'YOUR_TURNSTILE_SITE_KEY',
  submissionEndpoint: '/.netlify/functions/submit-testimony',
  submissionsEnabled: false,
  moderationEnabled: false
});
