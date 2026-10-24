// Daily-prayer email templates. Prayer text is verbatim from published site copy - never reworded here.
// Postal line is the only place the mailing address appears; the pending ZIP lands as a one-string patch.
export const POSTAL_ADDRESS = '7820 NW 4th Ave, Miami, FL';
const SITE = 'https://marsharbel.com';

export function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function shell(preheader: string, bodyHtml: string, footerHtml: string): string {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mar Charbel Daily Prayer</title></head>
<body style="margin:0;padding:0;background:#f5efe3;">
<span style="display:none;max-height:0;overflow:hidden;">${escapeHtml(preheader)}</span>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5efe3;padding:24px 12px;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fffdf8;border:1px solid #e4d9c3;border-radius:12px;overflow:hidden;">
<tr><td style="background:#3d2b1f;padding:20px 28px;">
  <span style="font-family:Georgia,'Times New Roman',serif;font-size:20px;color:#f0dfba;letter-spacing:0.5px;">Mar Charbel</span>
  <span style="font-family:Georgia,'Times New Roman',serif;font-size:13px;color:#cdb389;display:block;margin-top:2px;">Daily Prayer</span>
</td></tr>
<tr><td style="padding:28px;font-family:Georgia,'Times New Roman',serif;font-size:16px;line-height:1.6;color:#33291f;">
${bodyHtml}
</td></tr>
<tr><td style="padding:18px 28px;border-top:1px solid #e4d9c3;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:#8a7c66;">
${footerHtml}
</td></tr>
</table>
</td></tr></table>
</body></html>`;
}

function footer(withUnsubscribeUrl?: string): string {
  const links = [`<a href="${SITE}" style="color:#6d5a43;">marsharbel.com</a>`];
  if (withUnsubscribeUrl) links.push(`<a href="${withUnsubscribeUrl}" style="color:#6d5a43;">Unsubscribe</a>`);
  return `You receive this because you subscribed to the daily prayer at marsharbel.com.<br>
${links.join(' &middot; ')}<br>
${escapeHtml(POSTAL_ADDRESS)}`;
}

export function confirmEmail(confirmUrl: string): { subject: string; html: string; text: string } {
  const body = `
<p style="margin:0 0 16px;">Peace be with you,</p>
<p style="margin:0 0 16px;">one step left: confirm that you would like to receive the daily prayer - the rosary mystery of the day, a link to the Maronite prayers of the day, and a daily prayer to Saint Charbel.</p>
<p style="margin:0 0 24px;text-align:center;">
  <a href="${confirmUrl}" style="display:inline-block;background:#6d3b2a;color:#fffdf8;text-decoration:none;padding:12px 28px;border-radius:8px;font-size:16px;">Confirm my subscription</a>
</p>
<p style="margin:0;color:#6d5a43;font-size:14px;">If you did not ask for this, ignore this email and nothing else will arrive.</p>`;
  const text = `Peace be with you,\n\nConfirm your daily prayer subscription:\n${confirmUrl}\n\nIf you did not ask for this, ignore this email and nothing else will arrive.\n\n${POSTAL_ADDRESS}`;
  return { subject: 'Confirm your daily prayer subscription', html: shell('One step left: confirm your daily prayer subscription.', body, footer()), text };
}

export interface IssueContent {
  issueDateLabel: string;
  mysterySet: string;
  mysteries: string[];
  prayerTitle: string;
  prayerText: string;
  prayerPageUrl: string;
  prayersOfDayUrl: string;
  unsubscribeUrl: string;
}

export function issueEmail(content: IssueContent): { subject: string; html: string; text: string } {
  const mysteryItems = content.mysteries.map(mystery => `<li style="margin:0 0 4px;">${escapeHtml(mystery)}</li>`).join('');
  const body = `
<p style="margin:0 0 4px;font-size:14px;color:#6d5a43;">${escapeHtml(content.issueDateLabel)}</p>
<h1 style="margin:0 0 20px;font-size:22px;font-weight:normal;color:#3d2b1f;">Today&rsquo;s prayer</h1>
<h2 style="margin:0 0 8px;font-size:17px;font-weight:normal;color:#6d3b2a;">Rosary: the ${escapeHtml(content.mysterySet)} Mysteries</h2>
<ol style="margin:0 0 20px;padding-left:22px;">
${mysteryItems}
</ol>
<h2 style="margin:0 0 8px;font-size:17px;font-weight:normal;color:#6d3b2a;">${escapeHtml(content.prayerTitle)}</h2>
<p style="margin:0 0 8px;font-style:italic;">${escapeHtml(content.prayerText)}</p>
<p style="margin:0 0 20px;font-size:14px;"><a href="${content.prayerPageUrl}" style="color:#6d3b2a;">More Saint Charbel prayers</a></p>
<p style="margin:0;padding:14px 16px;background:#f5efe3;border-radius:8px;font-size:14px;">
  Pray with today&rsquo;s full set: <a href="${content.prayersOfDayUrl}" style="color:#6d3b2a;">the Maronite prayers of the day</a>.
</p>`;
  const text = `Today's prayer - ${content.issueDateLabel}\n\nRosary: the ${content.mysterySet} Mysteries\n${content.mysteries.map((mystery, index) => `${index + 1}. ${mystery}`).join('\n')}\n\n${content.prayerTitle}\n${content.prayerText}\nMore: ${content.prayerPageUrl}\n\nThe Maronite prayers of the day: ${content.prayersOfDayUrl}\n\nUnsubscribe: ${content.unsubscribeUrl}\n${POSTAL_ADDRESS}`;
  return {
    subject: `Daily prayer - ${content.issueDateLabel}`,
    html: shell(`The ${content.mysterySet} Mysteries and today's Saint Charbel prayer.`, body, footer(content.unsubscribeUrl)),
    text
  };
}

export function landingPage(title: string, messageHtml: string, actionHtml: string): string {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(title)} - Mar Charbel</title></head>
<body style="margin:0;padding:0;background:#f5efe3;font-family:Georgia,'Times New Roman',serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:48px 12px;"><tr><td align="center">
<table role="presentation" width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;background:#fffdf8;border:1px solid #e4d9c3;border-radius:12px;overflow:hidden;">
<tr><td style="background:#3d2b1f;padding:18px 24px;"><span style="font-size:18px;color:#f0dfba;">Mar Charbel</span></td></tr>
<tr><td style="padding:28px 24px;font-size:16px;line-height:1.6;color:#33291f;">
<h1 style="margin:0 0 14px;font-size:21px;font-weight:normal;">${escapeHtml(title)}</h1>
${messageHtml}
${actionHtml}
</td></tr>
<tr><td style="padding:14px 24px;border-top:1px solid #e4d9c3;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#8a7c66;">
<a href="${SITE}" style="color:#6d5a43;">marsharbel.com</a>
</td></tr>
</table></td></tr></table>
</body></html>`;
}
