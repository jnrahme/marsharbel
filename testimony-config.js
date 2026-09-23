// Public configuration only. Secrets belong in Supabase Edge Function settings.
window.TESTIMONY_CONFIG = Object.freeze({
  supabaseUrl: 'https://alxccoizzksyitxvqhpv.supabase.co',
  supabaseAnonKey: 'sb_publishable_CSt9QELXHVmN0B4hUDxffw_mB7Qz0Ai',
  turnstileSiteKey: '0x4AAAAAAFAXSDklOoqGMd4v',
  // Public widget key; private verification key is stored in Supabase secrets.
  submissionCaptchaProvider: 'hcaptcha',
  hcaptchaSiteKey: 'e09a4522-0884-4fb6-82d6-fcfedf7e939c',
  accountsEnabled: false,
  submissionsEnabled: true,
  moderationEnabled: true,
  // Password-access migration applied after owner confirmation.
  moderatorMfaRequired: false
});
