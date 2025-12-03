// sanity/updateSlug.js

import { getCliClient } from 'sanity/cli';

// 引数を手動でパースするシンプルな方法
const args = {};
process.argv.slice(2).forEach((arg, i, arr) => {
  if (arg.startsWith('--')) {
    const key = arg.substring(2);
    const next = arr[i + 1];
    if (next && !next.startsWith('--')) {
      args[key] = next;
    }
  }
});

const { id, slug } = args;

if (!id || !slug) {
  console.error('Error: Please provide both --id and --slug arguments.');
  console.error('Example: sanity exec updateSlug.js -- --id <document-id> --slug <new-slug>');
  process.exit(1);
}

// Sanityクライアントを取得する
// このスクリプトは `sanity exec --with-user-token` で実行される必要があります
const client = getCliClient();

// ドキュメントを更新する
client
  .patch(id)
  .set({ 'slug.current': slug })
  .commit()
  .then((updatedDoc) => {
    console.log(`✅ Successfully updated slug for document "${updatedDoc._id}"`);
    console.log(`   New slug: "${updatedDoc.slug.current}"`);
  })
  .catch((err) => {
    console.error('❌ Error updating document:', err.message);
    process.exit(1);
  });
