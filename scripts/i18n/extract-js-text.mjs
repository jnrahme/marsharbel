// Parse source instead of matching strings inside comments or regular expressions.
import {readFileSync} from 'node:fs';
import {parse} from 'acorn';

const source = readFileSync(process.argv[2], 'utf8');
const tree = parse(source, {ecmaVersion:'latest', sourceType:'script', allowReturnOutsideFunction:true});
const texts = [];
function visit(node) {
  if (!node || typeof node !== 'object') return;
  const value = node.type === 'Literal' && typeof node.value === 'string' ? node.value
    : node.type === 'TemplateElement' ? node.value.cooked : null;
  // This guard identifies likely prose, not every string used as an API key,
  // route, selector, or identifier. AGENTS.md also requires code review.
  if (value && (/\p{L}.*\s.*\p{L}/u.test(value) || /^[A-Z][a-z]+$/.test(value))
      && !/[<>{}\[\]#=]|https?:\/\//.test(value)) texts.push(value.trim());
  for (const [key, child] of Object.entries(node)) {
    if (['start','end','loc'].includes(key)) continue;
    if (Array.isArray(child)) child.forEach(visit);
    else if (child && typeof child === 'object') visit(child);
  }
}
visit(tree);
process.stdout.write(JSON.stringify(texts));
