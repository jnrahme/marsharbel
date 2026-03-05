window.TESTIMONY_CONFIG = {
  supabaseUrl: 'https://YOUR_PROJECT.supabase.co',
  supabaseAnonKey: 'YOUR_SUPABASE_ANON_KEY',
  turnstileSiteKey: 'YOUR_TURNSTILE_SITE_KEY',
  // Turnstile token must be validated on server before accepting a submission.
  turnstileVerifyEndpoint: '/turnstile-verify.php',
  requireTurnstile: true
};
